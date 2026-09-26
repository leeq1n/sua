"""Bounded drift and resume regressions for the runtime-neutral control contract."""

import pytest

from src.goal_control import ControlPlane, Goal, Task, DriftError


def plane(capsule_dir=None):
    control = ControlPlane(capsule_dir=capsule_dir)
    control.add_goal(Goal("G1", "Deliver the user report", ("report delivered",),
                          ("build a dashboard",), ("use cited evidence",)))
    control.add_task(Task("T1", "Write report", "G1", ("report delivered",)))
    return control


@pytest.mark.parametrize("action", [
    "build a dashboard",  # proxy drift: a method becomes an objective
    "polish unrelated interface",  # subtask drift
    "rewrite the control system",  # meta drift
])
def test_action_requires_goal_trace(action):
    with pytest.raises(DriftError):
        plane().record_action(action, "T1", "report delivered")


def test_feedback_does_not_silently_mutate_goal():
    p = plane()
    assert p.route_feedback("T1", "try a shorter method", "method_feedback") == "T1"
    assert p.goals["G1"].version == 1
    with pytest.raises(DriftError):
        p.route_feedback("T1", "ship a dashboard", "goal_mutation")
    assert p.goals["G1"].version == 1


def test_method_feedback_cannot_modify_inactive_task(tmp_path):
    p = plane(tmp_path)
    p.wait_for_user("T1", "Need source approval")
    with pytest.raises(DriftError):
        p.route_feedback("T1", "try another method", "method_feedback")
    assert p.tasks["T1"].version == 1


def test_superseded_goal_is_not_resident(tmp_path):
    p = plane(tmp_path)
    p.add_goal(Goal("G2", "Deliver a chart", ("chart delivered",)))
    p.add_task(Task("T2", "Draw chart", "G2", ("chart delivered",)))
    p.supersede_goal("G1", "G2")
    assert p.working_context()["goal"].goal_id == "G2"
    assert "T1" not in p.working_context()["tasks"]
    with pytest.raises(DriftError):
        p.record_action("write report", "T1", "report delivered")


def test_adding_another_active_goal_keeps_context_consistent():
    p = plane()
    p.add_goal(Goal("G2", "Deliver a chart", ("chart delivered",)))
    context = p.working_context()
    assert context["goal"].goal_id == "G1"
    assert set(context["tasks"]) == {"T1"}
    p.add_task(Task("T2", "Draw chart", "G2", ("chart delivered",)))
    p.activate_task("T2")
    context = p.working_context()
    assert context["goal"].goal_id == "G2"
    assert set(context["tasks"]) == {"T2"}


def test_resume_fidelity_and_eviction(tmp_path):
    p = plane(tmp_path)
    p.wait_for_user("T1", "Need source approval")
    assert p.tasks["T1"].residency == "COLD"
    assert p.working_context()["tasks"] == {}
    capsule = p.capture("T1")
    p.resume("T1", capsule, "Need source approval")
    assert p.tasks["T1"].title == "Write report"
    assert p.tasks["T1"].status == "ACTIVE"
    assert p.tasks["T1"].residency == "HOT"


def test_resume_rejects_capsule_after_goal_version_changes(tmp_path):
    p = plane(tmp_path)
    p.wait_for_user("T1", "Need source approval")
    capsule = p.capture("T1")
    p.revise_goal("G1", p.goal_checksum("G1"), objective="Deliver the updated report")
    with pytest.raises(DriftError):
        p.resume("T1", capsule, "Need source approval")
    assert p.tasks["T1"].residency == "COLD"


def test_capsule_persists_before_eviction_and_resumes_in_fresh_controller(tmp_path):
    path = tmp_path / "capsule.json"
    p = plane()
    p.pause_and_persist("T1", "WAITING_USER", path, "Need source approval")
    assert path.exists()
    assert p.tasks["T1"].residency == "COLD"
    fresh = plane(tmp_path)
    fresh.wait_for_user("T1", "Need source approval")
    fresh.resume_from_file("T1", path, "Need source approval")
    assert fresh.tasks["T1"].status == "ACTIVE"
    assert fresh.working_context()["tasks"]["T1"].title == "Write report"


def test_failed_persistence_does_not_evict_task(tmp_path):
    p = plane()
    with pytest.raises(FileNotFoundError):
        p.pause_and_persist("T1", "WAITING_USER", tmp_path / "missing" / "capsule.json", "Need source approval")
    assert p.tasks["T1"].status == "ACTIVE"
    assert p.tasks["T1"].residency == "HOT"
    assert p.working_context()["tasks"]["T1"].title == "Write report"


def test_direct_transition_requires_durable_capsule():
    p = plane()
    with pytest.raises(DriftError):
        p.transition_task("T1", "WAITING_USER", "Need source approval")
    assert p.tasks["T1"].status == "ACTIVE"
    assert p.tasks["T1"].residency == "HOT"


def test_resume_needs_matching_named_trigger(tmp_path):
    p = plane(tmp_path)
    p.wait_for_user("T1", "Need source approval")
    capsule = p.capture("T1")
    with pytest.raises(DriftError):
        p.resume("T1", capsule, "Unrelated event")
    assert p.tasks["T1"].status == "WAITING_USER"


def test_supersession_requires_persistence_before_goal_change():
    p = plane()
    p.add_goal(Goal("G2", "Deliver a chart", ("chart delivered",)))
    with pytest.raises(DriftError):
        p.supersede_goal("G1", "G2")
    assert p.goals["G1"].status == "ACTIVE"
    assert p.tasks["T1"].status == "ACTIVE"


def test_supersession_persistence_failure_does_not_partially_evict(tmp_path, monkeypatch):
    p = plane(tmp_path)
    p.add_task(Task("T3", "Check report", "G1", ("report delivered",)))
    p.add_goal(Goal("G2", "Deliver a chart", ("chart delivered",)))
    original = p._persist_capsule

    def fail_second(task_id, capsule, path=None):
        if task_id == "T3":
            raise OSError("store unavailable")
        return original(task_id, capsule, path)

    monkeypatch.setattr(p, "_persist_capsule", fail_second)
    with pytest.raises(OSError):
        p.supersede_goal("G1", "G2")
    assert p.goals["G1"].status == "ACTIVE"
    assert p.tasks["T1"].status == "ACTIVE"
    assert p.tasks["T3"].status == "ACTIVE"


def test_supersession_archives_cold_tasks(tmp_path):
    p = plane(tmp_path)
    p.wait_for_user("T1", "Need source approval")
    p.add_goal(Goal("G2", "Deliver a chart", ("chart delivered",)))
    p.supersede_goal("G1", "G2")
    assert p.tasks["T1"].status == "SUPERSEDED"
    assert p.tasks["T1"].residency == "ARCHIVED"


def test_traceability_and_dependencies():
    p = plane()
    p.add_task(Task("T0", "Collect citations", "G1", ("report delivered",)))
    p.tasks["T1"].dependencies = ("T0",)
    p.activate_task("T1")
    p.allow_action("T1", "Draft report", "report delivered")
    trace = p.record_action("Draft report", "T1", "report delivered")
    assert trace == ("Draft report", "T1", "report delivered", "G1")
    assert set(p.working_context()["tasks"]) == {"T1", "T0"}


def test_goal_checksum_rejects_stale_feedback_and_suspends_old_criterion(tmp_path):
    p = plane(tmp_path)
    checksum = p.goal_checksum("G1")
    p.revise_goal("G1", checksum, success_criteria=("revised report delivered",))
    assert p.goals["G1"].version == 2
    assert p.tasks["T1"].status == "SUSPENDED"
    with pytest.raises(DriftError):
        p.revise_goal("G1", checksum, objective="stale edit")


def test_objective_revision_suspends_existing_task_plan(tmp_path):
    p = plane(tmp_path)
    p.allow_action("T1", "Draft report", "report delivered")
    p.revise_goal("G1", p.goal_checksum("G1"), objective="Deliver a different report")
    assert p.tasks["T1"].status == "SUSPENDED"
    assert p.tasks["T1"].residency == "COLD"
    with pytest.raises(DriftError):
        p.record_action("Draft report", "T1", "report delivered")


def test_direct_goal_mutation_cannot_authorize_an_action():
    p = plane()
    p.allow_action("T1", "Draft report", "report delivered")
    p.goals["G1"].objective = "Deliver something else"
    with pytest.raises(DriftError):
        p.record_action("Draft report", "T1", "report delivered")
    assert p.working_context()["goal"] is None


def test_action_authorization_cannot_be_relabelled_to_another_criterion():
    p = ControlPlane()
    p.add_goal(Goal("G1", "Deliver report and chart", ("report delivered", "chart delivered")))
    p.add_task(Task("T1", "Prepare outputs", "G1", ("report delivered", "chart delivered")))
    p.allow_action("T1", "Draft report", "report delivered")
    with pytest.raises(DriftError):
        p.record_action("Draft report", "T1", "chart delivered")
    assert p.record_action("Draft report", "T1", "report delivered") == (
        "Draft report", "T1", "report delivered", "G1")


def test_durable_knowledge_requires_explicit_retrieval():
    p = plane()
    p.durable_knowledge["old failure"] = "historical note"
    assert p.working_context()["knowledge"] == {}
    p.retrieve_knowledge("T1", "old failure")
    assert p.working_context()["knowledge"] == {"old failure": "historical note"}


def test_retrieved_knowledge_does_not_leak_to_another_active_task():
    p = plane()
    p.durable_knowledge["report-only"] = "old report note"
    p.retrieve_knowledge("T1", "report-only")
    p.add_task(Task("T2", "Verify citations", "G1", ("report delivered",)))
    p.activate_task("T2")
    assert p.working_context()["knowledge"] == {}
    p.retrieve_knowledge("T2", "report-only")
    assert p.working_context()["knowledge"] == {"report-only": "old report note"}


@pytest.mark.parametrize("status,residency", [
    ("WAITING_USER", "COLD"), ("BLOCKED", "COLD"),
    ("SUSPENDED", "COLD"), ("SUPERSEDED", "ARCHIVED"),
    ("DONE", "ARCHIVED"), ("ABANDONED", "ARCHIVED"),
])
def test_lifecycle_eviction(status, residency, tmp_path):
    p = plane(tmp_path)
    p.transition_task("T1", status, "explicit trigger")
    assert p.tasks["T1"].residency == residency
    assert p.working_context()["tasks"] == {}
