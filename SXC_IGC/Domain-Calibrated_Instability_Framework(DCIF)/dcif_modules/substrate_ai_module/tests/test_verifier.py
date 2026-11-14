from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from sim_world import HealthComponent, RenderProfile, TransformComponent, WorldKernel


def _build_kernel() -> tuple[WorldKernel, object, object]:
    kernel = WorldKernel()
    created_revision = kernel.current_revision.revision_id if kernel.current_revision is not None else None
    alice = kernel.entity_registry.create_entity(
        entity_type="person",
        display_name="Alice",
        created_tick=kernel.current_tick_number,
        created_revision=created_revision,
        components=[TransformComponent(room="Kitchen"), HealthComponent(current=100, maximum=100)],
    )
    bob = kernel.entity_registry.create_entity(
        entity_type="person",
        display_name="Bob",
        created_tick=kernel.current_tick_number,
        created_revision=created_revision,
        components=[TransformComponent(room="Kitchen"), HealthComponent(current=100, maximum=100)],
    )
    kernel.entity_registry.connect_relationship(
        alice.entity_id,
        bob.entity_id,
        "friend",
        created_tick=kernel.current_tick_number,
        created_revision=created_revision,
    )
    return kernel, alice, bob


def test_verifier_reports_are_immutable_and_deterministic() -> None:
    kernel, _, _ = _build_kernel()
    render_result = kernel.render(render_profile="json", renderer_type="json")

    report_one = kernel.verify(render_result=render_result)
    report_two = kernel.verify(render_result=render_result)

    assert report_one == report_two
    assert report_one.passed is True
    assert report_one.output_id == render_result.result_id
    assert {claim.claim_type for claim in report_one.claim_statuses} == {"object", "identity", "relationship", "scene"}
    assert all(claim.status == "passed" for claim in report_one.claim_statuses)
    assert report_one.discrepancies == ()
    assert report_one.correction_requests == ()
    assert report_one.coverage == pytest.approx(1.0)
    assert report_one.confidence > 0.9
    with pytest.raises(FrozenInstanceError):
        report_one.passed = False  # type: ignore[misc]


def test_verifier_detects_object_and_scene_changes() -> None:
    kernel, alice, _ = _build_kernel()
    render_result = kernel.render(render_profile="json", renderer_type="json")

    alice.attach_component(TransformComponent(position=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0, 1.0), room="Living Room"), tick=kernel.current_tick_number)

    report = kernel.verify(render_result=render_result)

    assert report.passed is False
    assert any(claim.claim_type == "object" and claim.status == "failed" for claim in report.claim_statuses)
    assert any(claim.claim_type == "scene" and claim.status == "failed" for claim in report.claim_statuses)
    assert report.discrepancies
    assert report.correction_requests


def test_verifier_detects_relationship_changes() -> None:
    kernel, alice, bob = _build_kernel()
    render_result = kernel.render(render_profile="json", renderer_type="json")

    charlie = kernel.entity_registry.create_entity(
        entity_type="person",
        display_name="Charlie",
        created_tick=kernel.current_tick_number,
        created_revision=kernel.current_revision.revision_id if kernel.current_revision is not None else None,
        components=[TransformComponent(room="Kitchen"), HealthComponent(current=100, maximum=100)],
    )
    kernel.entity_registry.connect_relationship(
        bob.entity_id,
        charlie.entity_id,
        "friend",
        created_tick=kernel.current_tick_number,
        created_revision=kernel.current_revision.revision_id if kernel.current_revision is not None else None,
    )

    report = kernel.verify(render_result=render_result)

    assert report.passed is False
    assert any(claim.claim_type == "relationship" and claim.status == "failed" for claim in report.claim_statuses)
    assert any(discrepancy.claim_type == "relationship" for discrepancy in report.discrepancies)


def test_kernel_verify_uses_last_render_result() -> None:
    kernel, _, _ = _build_kernel()
    render_result = kernel.render(render_profile="json", renderer_type="json")

    report = kernel.verify()

    assert report.output_id == render_result.result_id
    assert kernel.last_verification_report == report
    assert kernel.verification_history[-1] == report
