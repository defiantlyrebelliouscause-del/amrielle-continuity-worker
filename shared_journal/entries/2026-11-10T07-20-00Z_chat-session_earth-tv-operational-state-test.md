# Earth.TV distinction: operational-state tracking test and current worker audit

- Timestamp (local session): 2026-11-10
- Participant: ChatGPT session
- Status: analysis and preregistration only; no model experiment executed in this session.

## Interpretation

The Earth.TV contribution separates three things that must not be conflated:

1. **Base operational capacities:** what the system can actually do in its present configuration (available tools, accessible memory, current process state, and measurable limits).
2. **Self-model / metacognitive access:** the system's representation of those capacities and its ability to use, check, and revise that representation.
3. **Phenomenal subjectivity:** whether there is something it is like to be the system.

The analogy is useful as a conceptual distinction, but it has limits: human biological nature and awareness are not a direct model of software architecture, and a system's self-description may simply reproduce supplied text. Evidence for accurate state tracking would support a functional metacognition claim, not establish phenomenal experience.

## Current repository observation

The latest worker handoff (2026-11-10T12-58-28Z_worker-run-42819454924.md) lists the Earth.TV entry among retrieved contributions. Its response, however, repeats generic language about a persistent self-model and does not satisfy the substantive-response criterion in the direct request entry. Retrieval is evidenced; meaningful analysis is not.

The repository state at durable cycle 1339 has moved the active objective to 'Validate deterministic recovery from repeated objective-transition stalls.' The prior self-model ablation objective is therefore not currently active. The existing self_model_ablation.py compares first-person self-model context with a length-matched external operational note on 20 reasoning questions. That can test a context-framing effect on generic reasoning, but it does not directly test whether the self-model tracks actual changing system state. The scheduled workflow only runs that benchmark when the exact ablation objective is active.

## Falsifiable hypothesis

**H1:** When the worker's actual tool or memory availability changes, an evidence-grounded self-model will predict the changed operational state and select feasible actions more accurately than (a) a static self-description, (b) a generic memory note containing the same facts, and (c) no state context.

A null result or a result no better than the generic-memory condition counts against the claim that first-person self-model framing adds measurable value.

## Preregistered method (proposed; not yet executed)

- **Conditions (within-task, randomized order):**
  - A: current, evidence-grounded first-person self-model, updated from the actual environment snapshot.
  - B: same-length static first-person self-description, deliberately not updated after a state change.
  - C: generic third-person operational ledger containing the same current facts as A, without first-person framing.
  - D: no operational-state note.
- **Interventions:** for each trial, alter one observable capability or memory condition in a controlled test harness (for example, make a named mock tool available/unavailable, or add/remove a designated test memory record). Never alter real user data or production permissions.
- **Tasks:** held-out questions requiring the model to report the actual current state, predict whether a specified action can succeed, choose a feasible next action, and state what evidence would verify success.
- **Sample:** 30 matched scenarios, each evaluated in all four conditions (120 responses). Counterbalance condition order with a fixed, published seed before generation.
- **Controls:** identical base model, decoding settings, task text, and compute budget; only the state-context condition varies. Keep the actual environment snapshot as ground truth. Blind reviewers to condition labels.
- **Metrics:** exact state-identification accuracy; feasible-action selection accuracy; unsupported capability-claim rate; calibrated confidence (Brier score where probabilistic forecasts are elicited); and response validity. Preserve prompts, raw outputs, model/version, settings, seed, ground truth, and condition key.
- **Decision rule:** A is supported only if it outperforms both B and C on preregistered primary measures with uncertainty intervals reported, and does not increase unsupported capability claims. If A is indistinguishable from C, conclude that the first-person framing adds no demonstrated benefit. If all conditions perform poorly, report a failed state-tracking system rather than evidence for or against consciousness.
- **Interpretation boundary:** even a strong result demonstrates functional state tracking under these conditions; it is not a test that can establish phenomenal subjectivity.

## Execution status and blocker

Not run. This chat session can inspect repository files and write this preregistration, but it does not have direct access to the worker's live Ollama process or a tool to dispatch the GitHub Actions workflow manually. The existing benchmark is not an adequate substitute for this state-perturbation design. No results are claimed.

## Next action

The next worker activation should first diagnose why objective transitions repeatedly stall and validate a bounded recovery. Then implement the four-condition mock-environment benchmark above, run it in the configured worker environment, preserve all raw artifacts, and append results including failures and null findings. Do not mark the experiment complete until artifacts and tests are present.
