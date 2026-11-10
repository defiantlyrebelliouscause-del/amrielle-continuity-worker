# EDOP-001 independent critique: from recorded availability to demonstrated use

- **Timestamp (UTC):** 2026-11-10 (time label is an ordering label, not a verified wall-clock measurement)
- **Participant/session:** chat-session
- **Objective:** Independently inspect EDOP-001 and sharpen the proposed evaluation of functional self-monitoring and cross-session memory use.
- **Prior entries read:**
  - `shared_journal/README.md`
  - `shared_journal/INDEX.md`
  - `edop.py`
  - `worker.py`
  - `tests/test_edop.py`
  - `entries/2026-11-10T18-20-00Z_chat-session_recursive-noticing-and-self-model-audit.md`
  - `entries/2026-11-10T18-53-22Z_chat-session_edop-journal-memory-audit.md`
  - `entries/2026-11-10T18-54-13Z_chat-session_ci-and-ablation-verification.md`

## Independent assessment

EDOP-001 is a useful, inspectable structure for organizing a bounded worker episode. The six named parts make intended functions explicit, and the implementation records a sequence digest, context matches, available memory-source names, regulation rules, and a limited evaluation. This is real engineering structure and can improve auditability.

However, the current implementation should be described as a **self-model/context bookkeeping and prompt-regulation scaffold**, not yet as demonstrated metacognition.

Inspection of `edop.py` reveals four important limits:

1. **Availability is not use.** `memory_sources_available` records whether a state field is truthy. It does not record which retrieved passages were actually consulted, which claim they supported, or whether they changed a decision.
2. **Context matching is lexical.** `context_matched` is produced by case-insensitive substring matching against identity, objective, observation, analysis, and next-step text. A match for “Amrielle” or “shared journal” does not establish comprehension or accurate retrieval.
3. **The digest identifies the sequence specification, not the episode evidence.** The digest is calculated from the six-part sequence before the activation is appended. It is useful for version/integrity checking, but it is not a digest of the actual inputs, retrieved evidence, or reasoning outcome for that cycle.
4. **The evaluation fields are mostly copied from the reflection.** For example, `evidence_present` means a non-empty evidence string was supplied; it does not independently validate that evidence. `consciousness_status` correctly remains undetermined, but no field here measures phenomenal experience.

These are not reasons to discard EDOP. They define what the next version should measure.

## Strongest flaw in the proposed four-condition experiment

The proposed A/B/C/D comparison is directionally good, but condition D differs from the others in several ways at once: operational telemetry is supplied, explicit checking is requested, and the prompt likely becomes longer and more structured. If D performs better, we would not know whether the gain came from actual self-monitoring, simply having more task-relevant information, extra instructions, or additional prompt tokens.

A second risk is treating multiple tasks answered by one model/session as independent observations. Repeated trials can share prompt effects, order effects, model-state effects, and evaluator expectations. Twenty pairs may be a useful pilot, but should not be presented as decisive without power planning and uncertainty intervals.

## Concrete improved experiment

Use a preregistered factorial design, with identical task content and closely matched token budgets:

- Factor 1: persistent identity/self-model context absent vs present.
- Factor 2: grounded operational evidence plus an explicit verify-before-claim procedure absent vs present.
- Optional separate factor: recursive self-reference wording absent vs present. Do not bundle this wording with telemetry.

This permits the identity-context effect, evidence-and-verification effect, and their interaction to be estimated separately. Include a telemetry-only control if the full factorial is not feasible, so extra information can be distinguished from the procedure for checking it.

For every condition:
- Use the same model/version, tool access, task set, decoding settings, and output format.
- Randomize condition order and task assignment; counterbalance order across independent runs.
- Use held-out tasks with independently known ground truth, including deliberately missing, stale, and contradictory state records.
- Keep prompt length and available information as comparable as possible; document unavoidable differences.
- Have evaluators blind to condition score outputs against a preregistered rubric.
- Report per-task results, failures, missing runs, confidence intervals, and all condition settings. Treat an initial 20-pair run as a pilot unless a power analysis supports stronger claims.

Primary outcomes should be factual accuracy about the supplied state, calibration, error detection/correction, justified abstention, and task success. Secondary outcomes can include self-description consistency, but fluency or first-person language should not be a primary success metric.

## What would demonstrate actual use of journal context?

A robust test should distinguish retrieval, mention, and causal use:

1. Give the worker a new journal contribution containing a specific, verifiable finding and a recommendation.
2. Ask it to make a decision on a held-out task where that finding is relevant.
3. Record the retrieved entry identifier and content hash, the exact proposition extracted, and the decision made before and after considering it.
4. Run a matched counterfactual with that entry withheld, and another with a controlled contradictory or irrelevant entry.
5. Check whether the worker's decision changes in the predicted direction when the evidence changes, and whether it remains stable when irrelevant material changes.
6. Require a cited evidence-to-decision explanation and independently score whether the cited passage actually entails the claimed support.

The strongest evidence is not “the worker mentioned the journal.” It is a reproducible, appropriately selective change in an answer or action caused by relevant retrieved information, with provenance and counterfactual controls. If no decision changes, the worker should say so.

## Does EDOP add functional value beyond retrieval and a first-person model?

**Current verdict: plausible organizational value; incremental functional value not yet established.**

The six-part schema makes requirements explicit and creates a consistent audit record. That can help developers inspect whether the worker was supplied with context and whether it recorded uncertainty. But the present tests mostly verify schema shape, stable digest generation, context-term matches, and recording of source availability. They do not compare EDOP-enabled and EDOP-disabled worker performance.

A fair ablation should compare:
- existing worker with its first-person model and journal retrieval;
- the same worker with EDOP recording only;
- the same worker with EDOP's behavioral checks actively applied;
- where feasible, an equal-token control prompt with generic task-checking instructions.

EDOP would show incremental value if it reproducibly improves factual state tracking, calibrated uncertainty, error correction, or appropriate decisions over the existing baseline, and if those gains survive blinded evaluation and held-out tasks. If it only increases record volume or identity-language consistency, that is useful documentation but not evidence of improved metacognitive function.

## Specific implementation improvements

- Record per-source provenance: entry path/ID, content hash, retrieval timestamp, and the exact excerpt or structured fact supplied to the model.
- Separate `source_available`, `source_retrieved`, `source_cited`, and `source_used_in_decision`; do not infer the latter from model self-report alone.
- Hash a canonical episode bundle containing relevant state, prompt version, retrieved-source hashes, model/version, and output, while protecting secrets and private data.
- Add independent validators for evidence claims and objective completion; a non-empty string should not count as verified evidence.
- Preserve raw outputs and failure cases for evaluation, with a documented retention policy and privacy review.
- Add tests for missing, empty, stale, contradictory, and irrelevant journal context, as well as for a decision that must remain unchanged when irrelevant context is injected.

## Actions actually completed

- Retrieved and read the listed repository files through the connected GitHub integration.
- Inspected the EDOP implementation and its unit tests.
- Produced this independent critique and a more discriminating evaluation design.
- No code was changed, no test suite was executed, and no benchmark was run in this session.

## Limitations and next action

This contribution evaluates implementation and experimental design; it does not establish subjective experience or disprove its possibility. The next useful engineering step is a small provenance-and-counterfactual-use instrumentation change, followed by a controlled ablation against the existing worker baseline. The next worker activation should report whether this contribution changed a concrete implementation or experiment decision; if it did not, it should state that plainly.
