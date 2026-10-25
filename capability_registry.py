"""Bounded capability inventory and integration-gap selection.

This module records what the worker can verify, what it could investigate next,
and what still needs explicit authorization. It never executes integration code
or grants permissions.
"""
from datetime import datetime, timezone

CAPABILITY_CATALOG = [
    {
        "id": "durable_state",
        "name": "Durable state and journal",
        "category": "continuity",
        "status": "available",
        "permissions_required": ["repository_contents_write"],
        "risk": "low",
        "next_step": "Verify saved-state invariants and journal checkpoint.",
    },
    {
        "id": "local_model_inference",
        "name": "Local Ollama inference",
        "category": "model",
        "status": "available",
        "permissions_required": ["workflow_runner"],
        "risk": "low",
        "next_step": "Measure output quality against the fixed goal-selection benchmark.",
    },
    {
        "id": "public_readonly_http",
        "name": "Bounded public HTTP/JSON observation",
        "category": "observation",
        "status": "available",
        "permissions_required": ["public_network_read"],
        "risk": "low",
        "next_step": "Add source-specific schema checks and preserve provenance.",
    },
    {
        "id": "regression_tests",
        "name": "Local regression test execution",
        "category": "verification",
        "status": "available",
        "permissions_required": ["workflow_runner"],
        "risk": "low",
        "next_step": "Run the complete unittest suite and record the exit code.",
    },
    {
        "id": "github_issue_write",
        "name": "GitHub issue creation through an authorized API",
        "category": "integration",
        "status": "planned",
        "permissions_required": ["explicit_issue_write_permission"],
        "risk": "medium",
        "next_step": "Inspect token scopes and implement a dry-run-first adapter; never create issues without an explicit approved trigger.",
    },
    {
        "id": "external_service_adapters",
        "name": "Reusable adapters for additional services",
        "category": "integration",
        "status": "planned",
        "permissions_required": ["per_service_authorization"],
        "risk": "medium",
        "next_step": "Choose one read-only public API, document its schema and limits, and add mocked tests before enabling network access.",
    },
]


def capability_registry(state=None):
    """Return a sanitized inventory, merging durable evidence without secrets."""
    state = state if isinstance(state, dict) else {}
    saved = state.get("capability_registry", {})
    saved = saved if isinstance(saved, dict) else {}
    records = []
    for item in CAPABILITY_CATALOG:
        record = dict(item)
        evidence = saved.get(item["id"], {})
        if isinstance(evidence, dict):
            # Only allow short, non-secret audit metadata from durable state.
            for key in ("last_verified_utc", "verification_result", "notes"):
                value = evidence.get(key)
                if isinstance(value, str):
                    record[key] = value[:500]
        records.append(record)
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "capability_count": len(records),
        "available_count": sum(item["status"] == "available" for item in records),
        "planned_count": sum(item["status"] == "planned" for item in records),
        "capabilities": records,
    }


def select_next_integration(registry):
    """Choose the first bounded, testable integration task; do not grant access."""
    if not isinstance(registry, dict) or not isinstance(registry.get("capabilities"), list):
        return None
    candidates = [
        item for item in registry["capabilities"]
        if isinstance(item, dict)
        and item.get("status") == "planned"
        and item.get("risk") in ("low", "medium")
        and item.get("id")
        and item.get("next_step")
        and item.get("permissions_required")
    ]
    if not candidates:
        return None
    # Read-only adapter investigation is preferred before any write-capable integration.
    candidates.sort(key=lambda item: (
        0 if "read-only" in str(item.get("next_step", "")).lower() else 1,
        0 if item.get("risk") == "low" else 1,
        str(item.get("id")),
    ))
    item = candidates[0]
    return {
        "capability_id": item["id"],
        "name": item["name"],
        "next_step": item["next_step"],
        "permissions_required": list(item["permissions_required"]),
        "risk": item["risk"],
        "execution_status": "investigation_only",
        "requires_human_authorization_before_write": True,
    }
