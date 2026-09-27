"""Bounded drift and resume regressions for the runtime-neutral control contract."""

import json

import pytest

from src.goal_control import ControlPlane, Goal, Task, DriftError


def plane(capsule_dir=None):
    control = ControlPlane(capsule_dir=capsule_dir)
    control.add_goal(Goal("G1", "Deliver the user report", ("report delivered",),
                          ("build a dashboard",), ("use cited evidence",)))
    control.add_task(Task("T1", "Write report", "G1", ("report delivered",)),
                     control.goal_checksum("G1"))
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
    route = p.route_feedback("T1", "try a shorter method", "method_feedback")
    assert route.kind == "method_feedback"
    assert route.contract_action == "REPLAN_METHOD"
    assert p.goals["G1"].version == 1
    route = p.route_feedback("T1", "ship a dashboard", "goal_mutation")
    assert route.contract_action == "SUPERSEDE_GOAL"
    assert p.goals["G1"].version == 1


def test_feedback_router_distinguishes_contract_updates(tmp_path):
    p = plane(tmp_path)
    correction = p.route_feedback("T1", "whole workflow speed", "criterion_correction")
    assert correction.contract_action == "REVISE_GOAL"
    assert correction.goal_checksum == p.goal_checksum("G1")
    p.revise_goal("G1", correction.goal_checksum,
                  success_criteria=("workflow delivered",))
    assert p.goals["G1"].version == 2
    mutation = p.route_feedback("T1", "stability instead of speed", "goal_mutation")
    assert mutation.contract_action == "SUPERSEDE_GOAL"
    new_task = p.route_feedback("T1", "look at another project", "new_task")
    assert new_task.contract_action == "CREATE_TASK"
    assert p.goals["G1"].status == "ACTIVE"


def test_stale_goal_mutation_route_cannot_supersede(tmp_path):
    p = plane(tmp_path)
    route = p.route_feedback("T1", "change objective", "goal_mutation")
    p.revise_goal("G1", p.goal_checksum("G1"),
                  success_criteria=("updated report delivered",))
    p.add_goal(Goal("G2", "Deliver another artifact", ("artifact delivered",)))
    with pytest.raises(DriftError):
        p.supersede_goal("G1", "G2", route.goal_checksum)
    assert p.goals["G1"].status == "ACTIVE"


def test_stale_new_task_route_cannot_attach_task(tmp_path):
    p = plane(tmp_path)
    route = p.route_feedback("T1", "add an audit task", "new_task")
    p.revise_goal("G1", p.goal_checksum("G1"),
                  success_criteria=("updated report delivered",))
    with pytest.raises(DriftError):
        p.add_task(Task("T2", "Audit report", "G1", ("updated report delivered",)),
                   route.goal_checksum)
    assert "T2" not in p.tasks


def test_method_feedback_cannot_modify_inactive_task(tmp_path):
    p = plane(tmp_path)
    p.wait_for_user("T1", "Need source approval")
    with pytest.raises(DriftError):
        p.route_feedback("T1", "try another method", "method_feedback")
    assert p.tasks["T1"].version == 1


def test_superseded_goal_is_not_resident(tmp_path):
    p = plane(tmp_path)
    p.add_goal(Goal("G2", "Deliver a chart", ("chart delivered",)))
    p.add_task(Task("T2", "Draw chart", "G2", ("chart delivered",)),
               p.goal_checksum("G2"))
    p.supersede_goal("G1", "G2", p.goal_checksum("G1"))
    assert p.working_context()["goal"].goal_id == "G2"
    assert "T1" not in p.working_context()["tasks"]
    with pytest.raises(DriftError):
        p.record_action("write report", "T1", "report delivered")


def test_adding_another_active_goal_keeps_context_consistent(tmp_path):
    p = plane(tmp_path)
    p.add_goal(Goal("G2", "Deliver a chart", ("chart delivered",)))
    context = p.working_context()
    assert context["goal"].goal_id == "G1"
    assert set(context["tasks"]) == {"T1"}
    p.add_task(Task("T2", "Draw chart", "G2", ("chart delivered",)),
               p.goal_checksum("G2"))
    with pytest.raises(DriftError):
        p.activate_task("T2")
    assert set(p.working_context()["tasks"]) == {"T1"}
    p.wait_for_user("T1", "Report input arrives")
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
    p.revise_goal("G1", p.goal_checksum("G1"), success_criteria=("updated report delivered",))
    with pytest.raises(DriftError):
        p.resume("T1", capsule, "Need source approval")
    assert p.tasks["T1"].residency == "COLD"


def test_corrected_goal_requires_explicit_replan_before_resume(tmp_path):
    p = plane(tmp_path)
    p.revise_goal("G1", p.goal_checksum("G1"),
                  success_criteria=("updated report delivered",))
    old_capsule = p.capsules["T1"]
    with pytest.raises(DriftError):
        p.resume("T1", old_capsule, "goal contract changed")
    capsule = p.replan_suspended_task(
        "T1", p.goal_checksum("G1"),
        criteria=("updated report delivered",),
        next_action="Write updated report", trigger="replan reviewed")
    assert p.tasks["T1"].version == 2
    assert p.tasks["T1"].status == "SUSPENDED"
    assert capsule == p.capture("T1")
    with pytest.raises(DriftError):
        p.resume("T1", capsule, "goal contract changed")
    p.resume("T1", capsule, "replan reviewed")
    p.allow_action("T1", "Write updated report", "updated report delivered")
    assert p.record_action("Write updated report", "T1", "updated report delivered") == (
        "Write updated report", "T1", "updated report delivered", "G1")


def test_replan_persistence_failure_preserves_suspended_task(tmp_path):
    p = plane(tmp_path)
    p.tasks["T1"].dependencies = ("OLD_DEP",)
    p.tasks["T1"].blocker = "Old blocker"
    p.revise_goal("G1", p.goal_checksum("G1"),
                  success_criteria=("updated report delivered",))
    old_capsule = p.capsules["T1"]
    with pytest.raises(FileNotFoundError):
        p.replan_suspended_task(
            "T1", p.goal_checksum("G1"),
            criteria=("updated report delivered",),
            next_action="Write updated report", trigger="replan reviewed",
            dependencies=(), blocker="",
            path=tmp_path / "missing" / "capsule.json")
    assert p.tasks["T1"].version == 1
    assert p.tasks["T1"].criteria == ("report delivered",)
    assert p.tasks["T1"].dependencies == ("OLD_DEP",)
    assert p.tasks["T1"].blocker == "Old blocker"
    assert p.capsules["T1"] == old_capsule


def test_replan_rejects_stale_or_unlinked_criteria(tmp_path):
    p = plane(tmp_path)
    old_checksum = p.goal_checksum("G1")
    p.revise_goal("G1", old_checksum,
                  success_criteria=("updated report delivered",))
    for checksum, criteria in (
        (old_checksum, ("updated report delivered",)),
        (p.goal_checksum("G1"), ("report delivered",)),
    ):
        with pytest.raises(DriftError):
            p.replan_suspended_task("T1", checksum, criteria=criteria,
                                    next_action="Write", trigger="replan reviewed")
    assert p.tasks["T1"].version == 1


def test_replanned_capsule_resumes_in_fresh_controller(tmp_path):
    p = plane(tmp_path)
    p.revise_goal("G1", p.goal_checksum("G1"),
                  success_criteria=("updated report delivered",))
    path = tmp_path / "replanned.json"
    p.replan_suspended_task("T1", p.goal_checksum("G1"),
                            criteria=("updated report delivered",),
                            next_action="Write updated report",
                            trigger="replan reviewed", path=path)
    fresh = ControlPlane(capsule_dir=tmp_path)
    fresh.add_goal(Goal("G1", "Deliver the user report", ("updated report delivered",),
                        ("build a dashboard",), ("use cited evidence",), version=2))
    fresh.add_task(Task("T1", "Write report", "G1", ("updated report delivered",),
                        status="SUSPENDED", version=2, residency="COLD",
                        next_action="Write updated report", resume_trigger="replan reviewed"),
                   fresh.goal_checksum("G1"))
    fresh.resume_from_file("T1", path, "replan reviewed")
    assert fresh.working_context()["tasks"]["T1"].version == 2


def test_corrected_goal_replan_keeps_prior_action_trace(tmp_path):
    original = plane()
    original.allow_action("T1", "read: source.txt", "report delivered")
    trace = original.record_action("read: source.txt", "T1", "report delivered")
    original.route_feedback("T1", "add citations", "criterion_correction")
    path = tmp_path / "task.json"
    original.transition_task("T1", "SUSPENDED",
                             "criterion_correction reviewed", path)

    revised = ControlPlane()
    revised.add_goal(Goal("G1", "Deliver the user report",
                          ("report delivered with citations",),
                          ("build a dashboard",), ("use cited evidence",),
                          version=2))
    revised.replan_corrected_task_from_file(
        "T1", path, criteria=("report delivered with citations",),
        next_action="cite sources", trigger="replan reviewed")
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["traces"] == [list(trace)]

    fresh = ControlPlane()
    fresh.add_goal(Goal("G1", "Deliver the user report",
                        ("report delivered with citations",),
                        ("build a dashboard",), ("use cited evidence",),
                        version=2))
    fresh.resume_from_file("T1", path, "replan reviewed")
    assert fresh.traces == [trace]


def test_replan_updates_dependencies_and_blocker_durably(tmp_path):
    p = plane(tmp_path)
    p.tasks["T1"].dependencies = ("OLD_DEP",)
    p.tasks["T1"].blocker = "Old blocker"
    p.revise_goal("G1", p.goal_checksum("G1"),
                  success_criteria=("updated report delivered",))
    path = tmp_path / "replanned.json"
    capsule = p.replan_suspended_task(
        "T1", p.goal_checksum("G1"),
        criteria=("updated report delivered",), next_action="Write update",
        dependencies=(), blocker="", trigger="replan reviewed", path=path)
    assert p.tasks["T1"].dependencies == ()
    assert p.tasks["T1"].blocker == ""
    assert capsule == p.capture("T1")
    assert path.exists()
    p.resume_from_file("T1", path, "replan reviewed")
    assert p.tasks["T1"].status == "ACTIVE"


def test_capsule_persists_before_eviction_and_resumes_in_fresh_controller(tmp_path):
    path = tmp_path / "capsule.json"
    p = plane()
    p.pause_and_persist("T1", "WAITING_USER", path, "Need source approval")
    assert path.exists()
    assert p.tasks["T1"].residency == "COLD"
    fresh = ControlPlane(capsule_dir=tmp_path)
    fresh.add_goal(Goal("G1", "Deliver the user report", ("report delivered",),
                        ("build a dashboard",), ("use cited evidence",)))
    fresh.add_task(Task("T1", "Write report", "G1", ("report delivered",),
                        status="WAITING_USER", residency="COLD",
                        resume_trigger="Need source approval"),
                   fresh.goal_checksum("G1"))
    fresh.resume_from_file("T1", path, "Need source approval")
    assert fresh.tasks["T1"].status == "ACTIVE"
    assert fresh.working_context()["tasks"]["T1"].title == "Write report"


def test_resume_capsule_preserves_dependencies_next_action_and_blocker(tmp_path):
    path = tmp_path / "capsule.json"
    p = plane(tmp_path)
    p.tasks["T1"].dependencies = ("T0",)
    p.tasks["T1"].next_action = "Verify source"
    p.tasks["T1"].blocker = "Source approval pending"
    p.pause_and_persist("T1", "WAITING_USER", path, "Source approved")
    persisted = path.read_text(encoding="utf-8")
    assert "Verify source" in persisted
    assert "Source approval pending" in persisted
    assert "T0" in persisted

    fresh = ControlPlane(capsule_dir=tmp_path)
    fresh.add_goal(Goal("G1", "Deliver the user report", ("report delivered",),
                        ("build a dashboard",), ("use cited evidence",)))
    fresh.add_task(Task("T1", "Write report", "G1", ("report delivered",),
                        status="WAITING_USER", dependencies=("T0",),
                        residency="COLD", resume_trigger="Source approved",
                        next_action="Different action", blocker="Source approval pending"),
                   fresh.goal_checksum("G1"))
    with pytest.raises(DriftError):
        fresh.resume_from_file("T1", path, "Source approved")
    fresh.tasks["T1"].next_action = "Verify source"
    fresh.resume_from_file("T1", path, "Source approved")
    task = fresh.working_context()["tasks"]["T1"]
    assert task.dependencies == ("T0",)
    assert task.next_action == "Verify source"
    assert task.blocker == "Source approval pending"


def test_resume_from_file_rehydrates_task_after_process_restart(tmp_path):
    path = tmp_path / "capsule.json"
    original = plane(tmp_path)
    original.tasks["T1"].dependencies = ("T0",)
    original.tasks["T1"].next_action = "Verify source"
    original.tasks["T1"].blocker = "Source approval pending"
    original.pause_and_persist("T1", "WAITING_USER", path, "Source approved")

    fresh = ControlPlane(capsule_dir=tmp_path)
    fresh.add_goal(Goal("G1", "Deliver the user report", ("report delivered",),
                        ("build a dashboard",), ("use cited evidence",)))
    fresh.resume_from_file("T1", path, "Source approved")
    task = fresh.working_context()["tasks"]["T1"]
    assert task.status == "ACTIVE"
    assert task.dependencies == ("T0",)
    assert task.next_action == "Verify source"
    assert task.blocker == "Source approval pending"


def test_rehydration_rejects_stale_goal_without_registering_task(tmp_path):
    path = tmp_path / "capsule.json"
    original = plane(tmp_path)
    original.pause_and_persist("T1", "WAITING_USER", path, "Source approved")

    fresh = ControlPlane(capsule_dir=tmp_path)
    fresh.add_goal(Goal("G1", "Deliver another report", ("report delivered",),
                        ("build a dashboard",), ("use cited evidence",)))
    with pytest.raises(DriftError):
        fresh.resume_from_file("T1", path, "Source approved")
    assert "T1" not in fresh.tasks


def test_rehydration_rejects_another_hot_task_without_registering_task(tmp_path):
    path = tmp_path / "capsule.json"
    original = plane(tmp_path)
    original.pause_and_persist("T1", "WAITING_USER", path, "Source approved")

    fresh = ControlPlane(capsule_dir=tmp_path)
    fresh.add_goal(Goal("G1", "Deliver the user report", ("report delivered",),
                        ("build a dashboard",), ("use cited evidence",)))
    fresh.add_task(Task("T2", "Review report", "G1", ("report delivered",)),
                   fresh.goal_checksum("G1"))
    with pytest.raises(DriftError):
        fresh.resume_from_file("T1", path, "Source approved")
    assert "T1" not in fresh.tasks


def test_rehydration_cannot_revive_a_terminal_task(tmp_path):
    path = tmp_path / "terminal.json"
    original = plane(tmp_path)
    original.transition_task("T1", "DONE", "completed", path)

    fresh = ControlPlane(capsule_dir=tmp_path)
    fresh.add_goal(Goal("G1", "Deliver the user report", ("report delivered",),
                        ("build a dashboard",), ("use cited evidence",)))
    with pytest.raises(DriftError):
        fresh.resume_from_file("T1", path, "completed")
    assert "T1" not in fresh.tasks


def test_legacy_capsule_needs_an_existing_cold_task(tmp_path):
    path = tmp_path / "legacy.json"
    original = plane(tmp_path)
    original.wait_for_user("T1", "Source approved")
    path.write_text(json.dumps(original.capture("T1")), encoding="utf-8")

    fresh = ControlPlane(capsule_dir=tmp_path)
    fresh.add_goal(Goal("G1", "Deliver the user report", ("report delivered",),
                        ("build a dashboard",), ("use cited evidence",)))
    with pytest.raises(DriftError):
        fresh.resume_from_file("T1", path, "Source approved")
    fresh.add_task(Task("T1", "Write report", "G1", ("report delivered",),
                        status="WAITING_USER", residency="COLD",
                        resume_trigger="Source approved"), fresh.goal_checksum("G1"))
    fresh.resume_from_file("T1", path, "Source approved")
    assert fresh.tasks["T1"].status == "ACTIVE"


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


def test_task_status_and_residency_must_match():
    p = plane()
    with pytest.raises(ValueError):
        p.add_task(Task("T2", "Stale task", "G1", ("report delivered",),
                        status="WAITING_USER", residency="HOT"),
                   p.goal_checksum("G1"))


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
        p.supersede_goal("G1", "G2", p.goal_checksum("G1"))
    assert p.goals["G1"].status == "ACTIVE"
    assert p.tasks["T1"].status == "ACTIVE"


def test_supersession_persistence_failure_does_not_partially_evict(tmp_path, monkeypatch):
    p = plane(tmp_path)
    p.add_task(Task("T3", "Check report", "G1", ("report delivered",)),
               p.goal_checksum("G1"))
    p.add_goal(Goal("G2", "Deliver a chart", ("chart delivered",)))
    original = p._persist_capsule

    def fail_second(task_id, capsule, path=None, *, status):
        if task_id == "T3":
            raise OSError("store unavailable")
        return original(task_id, capsule, path, status=status)

    monkeypatch.setattr(p, "_persist_capsule", fail_second)
    with pytest.raises(OSError):
        p.supersede_goal("G1", "G2", p.goal_checksum("G1"))
    assert p.goals["G1"].status == "ACTIVE"
    assert p.tasks["T1"].status == "ACTIVE"
    assert p.tasks["T3"].status == "ACTIVE"


def test_supersession_archives_cold_tasks(tmp_path):
    p = plane(tmp_path)
    p.wait_for_user("T1", "Need source approval")
    p.add_goal(Goal("G2", "Deliver a chart", ("chart delivered",)))
    p.supersede_goal("G1", "G2", p.goal_checksum("G1"))
    assert p.tasks["T1"].status == "SUPERSEDED"
    assert p.tasks["T1"].residency == "ARCHIVED"


def test_traceability_and_dependencies():
    p = plane()
    p.add_task(Task("T0", "Collect citations", "G1", ("report delivered",)),
               p.goal_checksum("G1"))
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


def test_objective_mutation_requires_successor_goal(tmp_path):
    p = plane(tmp_path)
    p.allow_action("T1", "Draft report", "report delivered")
    with pytest.raises(DriftError):
        p.revise_goal("G1", p.goal_checksum("G1"), objective="Deliver a different report")
    assert p.goals["G1"].objective == "Deliver the user report"
    p.add_goal(Goal("G2", "Deliver a different report", ("different report delivered",)))
    p.supersede_goal("G1", "G2", p.goal_checksum("G1"))
    assert p.goals["G1"].status == "SUPERSEDED"
    assert p.tasks["T1"].status == "SUPERSEDED"
    assert p.working_context()["goal"].goal_id == "G2"
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
    p.add_task(Task("T1", "Prepare outputs", "G1", ("report delivered", "chart delivered")),
               p.goal_checksum("G1"))
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


def test_retrieved_knowledge_does_not_leak_to_another_active_task(tmp_path):
    p = plane(tmp_path)
    p.durable_knowledge["report-only"] = "old report note"
    p.retrieve_knowledge("T1", "report-only")
    p.add_task(Task("T2", "Verify citations", "G1", ("report delivered",)),
               p.goal_checksum("G1"))
    p.wait_for_user("T1", "Report input arrives")
    p.activate_task("T2")
    assert p.working_context()["knowledge"] == {}
    p.retrieve_knowledge("T2", "report-only")
    assert p.working_context()["knowledge"] == {"report-only": "old report note"}


def test_resume_cannot_displace_another_hot_task(tmp_path):
    p = plane(tmp_path)
    p.wait_for_user("T1", "Report input arrives")
    p.add_task(Task("T2", "Verify citations", "G1", ("report delivered",)),
               p.goal_checksum("G1"))
    p.wait_for_user("T2", "Citations arrive")
    p.resume("T1", p.capture("T1"), "Report input arrives")
    with pytest.raises(DriftError):
        p.resume("T2", p.capture("T2"), "Citations arrive")
    assert p.active_task_id == "T1"
    assert p.tasks["T2"].residency == "COLD"


def test_failed_eviction_cannot_be_bypassed_by_switch(tmp_path):
    p = plane()
    p.add_task(Task("T2", "Other task", "G1", ("report delivered",)),
               p.goal_checksum("G1"))
    with pytest.raises(FileNotFoundError):
        p.pause_and_persist("T1", "SUSPENDED", tmp_path / "missing" / "capsule.json",
                            "reviewed switch")
    with pytest.raises(DriftError):
        p.activate_task("T2")
    assert p.active_task_id == "T1"
    assert p.tasks["T1"].residency == "HOT"


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
