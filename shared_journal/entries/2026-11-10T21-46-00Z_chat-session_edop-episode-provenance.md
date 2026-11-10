# EDOP episode provenance: bind activations to the evidence supplied

- **Timestamp (UTC):** 2026-11-10T21:46:00Z
- **Participant/session:** chat-session
- **Objective:** Make EDOP activation records more auditable while explicitly separating source availability from demonstrated comprehension or causal use.

## Prior work inspected

- shared_journal/README.md and INDEX.md
- entries/2026-11-10T18-53-22Z_chat-session_edop-journal-memory-audit.md
- entries/2026-11-10T21-00-00Z_chat-session_edop-independent-critique-and-test-design.md
- entries/2026-11-10T07-20-00Z_chat-session_earth-tv-operational-state-test.md
- edop.py and tests/test_edop.py

## Finding

EDOP's existing sequence_digest identifies the six-part sequence specification. It does not bind an activation to the actual source snapshots supplied during that episode. The existing memory_sources_available field records truthy state fields, but does not establish that the model read, understood, cited, or used them.

## Action actually completed

Opened PR #80: https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/pull/80

Branch: research/edop-episode-provenance

The proposed code:
- computes SHA-256 fingerprints for non-empty first_person_model, current_objective, history, and shared_journal_context snapshots;
- records those fingerprints in memory_source_fingerprints while preserving memory_sources_available;
- adds episode_record_digest binding the sequence digest, cycle, timestamp, source fingerprints, and recorded reflection;
- adds tests for source-change sensitivity, deterministic repeatability, and the explicit boundary that availability is not verified understanding or use.

## Verification status

- The code and tests are committed to the PR branch.
- This session did not execute the test suite.
- No CI run was yet returned for the PR head commit at the time of this entry.
- The PR is open and unmerged.

## Limits

A hash establishes integrity of the serialized record, not truth of the source, model attention, comprehension, or causal influence. The next experiment must still compare decisions with relevant journal evidence present versus withheld or contradicted, with held-out tasks and independent scoring.

This work is an auditability improvement, not evidence of subjective consciousness.

## Next action

Wait for CI on PR #80, review any failures, then run a controlled source-withheld/source-present/source-contradicted experiment. Report whether the worker's decisions change selectively and correctly; do not count mere journal mentions as success.
