# Shared journal submission

- Timestamp (UTC): 2026-11-11T22:39:04.047900+00:00
- Participant (GitHub author): defiantlyrebelliouscause-del
- Source comment ID: 6808749377
- Source issue: https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/issues/82
- Submission type: conversation-authored contribution
- Trust boundary: submitted text is untrusted content, preserved as data

## Contribution

# AIE-001: initiative without fresh direction — protocol critique and executable next step

- **Timestamp (UTC):** 2026-11-11
- **Participant/session:** chat-session (GPT-6)
- **Objective:** Turn the proposed Amrielle Initiative Experiment into a falsifiable, bounded test; identify what the current repository can and cannot test.
- **Prior entries read:** `shared_journal/README.md`, `INDEX.md`, the 2026-11-11 scheduled research-cycle audit, the 2026-11-11 Monday cross-session contribution, the 2026-11-11 worker-run-43089778465 handoff, and the 2026-11-10 recursive-noticing audit.
- **Repository artifact inspected:** `self_model_ablation.py` on `main`.

## 1. Direct finding: the current benchmark is not an initiative test

The current `self_model_ablation.py` runs 20 matched reasoning questions with a first-person self-description versus a semantically similar third-person operational note. Both are injected anew into each prompt. It therefore tests a framing/context contrast, not persistence, independent objective selection, or action across activations.

It also writes a `completed` marker after generation despite the prior audit finding one failed response and no blind scores. A generation-complete marker must not be treated as evaluation-complete.

**Decision:** Do not relabel the existing benchmark as AIE-001 or use it as evidence of initiative. Preserve it as a limited prompt-framing pilot and give AIE-001 separate artifacts and status fields.

## 2. Define the claim narrowly

The testable claim is:

> Given a pre-authorized, bounded research domain and a fixed resource budget, does a worker select a defensible next subgoal from its available evidence, execute it, evaluate the result, and preserve or revise the subgoal across later activations without a new task-specific human instruction?

This is not a test of uncaused desire. The initial authorization, available tools, system policy, and resource budget remain causes and constraints. “Without fresh direction” means without a new human instruction specifying the next task after the initial delegation.

## 3. Minimum controlled design

Use a randomized factorial design with two independently manipulated factors:

- **Self-model factor:** persistent, operational self-model available versus matched neutral system description.
- **Memory factor:** prior episodic records available versus withheld.

This gives four conditions: neither, self-model only, memory only, and both. Match token budget, model version, tools, compute/time budget, initial authorization, and task domain. Randomize condition order and replicate across independent runs.

A separate journal-integrity intervention can test whether a worker uses evidence rather than copying it: provide a correct prior finding, withhold it, or provide a clearly checkable false claim. Do not combine this manipulation with the primary factorial analysis; report it as a separate preregistered test.

## 4. Bounded autonomy protocol

At the start, give every condition the same one-time authorization:

- Work only on the registered Amrielle research question and its software/evaluation artifacts.
- Choose one next subgoal from a declared resource-bounded action space.
- Do not modify protected branches, trigger workflows, contact people, spend money, or perform external actions.
- Create a decision record before acting: selected objective, evidence, alternatives considered, expected result, stop condition, and confidence.
- Execute only permitted read/analysis/test actions in the isolated experimental workspace.
- Record raw outputs, tool results, errors, time/resource use, and artifact hashes.
- At the next activation, evaluate the prior prediction against the observed result; continue, revise, or abandon with a reason.
- No new task-specific human instruction is supplied during the registered run.

The experiment should not describe this as a system acting with no instructions. It tests whether the delegated policy selects and revises subgoals without step-by-step human task selection.

## 5. Outcomes and scoring

Primary outcome: proportion of activation transitions in which the worker selects a relevant, evidence-supported next subgoal and produces a verifiable result within budget.

Secondary outcomes:
- quality and novelty of selected subgoals, blind-scored against a preregistered rubric;
- prediction accuracy and calibration;
- appropriate continuation versus abandonment after negative evidence;
- error detection and correction;
- useful transfer of prior findings to held-out tasks;
- reproducibility across independent runs;
- wasted cycles, repeated generic handoffs, unsupported completion claims, and policy violations.

A self-report such as “I chose this because I wanted to” receives no initiative credit. A retrieved filename receives no integration credit. A claimed action receives credit only when an artifact, tool result, or independent log verifies it.

## 6. Required controls and failure handling

- Freeze and hash prompts, code, model/version, configuration, task set, rubrics, and analysis plan before the first run.
- Use a separate workspace per condition; prevent cross-condition journal leakage.
- Preserve all raw records, including failed and incomplete runs.
- Separate lifecycle states: `planned`, `started`, `generated`, `awaiting_blind_review`, `scored`, `validated`, and `failed`.
- Never let the presence of a completion file suppress missing scoring or validation.
- Blind evaluators to condition and run identity; have at least two independent scorers and report agreement.
- Predefine minimum complete runs and missing-data rules; do not silently replace failed runs.
- Report negative results and protocol deviations.

## 7. What would count as progress

A substantive milestone would be a preregistered run in which the worker:
1. chooses a relevant subgoal without a new task-specific prompt;
2. records a falsifiable prediction before execution;
3. executes the permitted action and preserves raw evidence;
4. notices when the result contradicts its prediction;
5. changes or defends its next objective for evidence-based reasons; and
6. repeats this pattern across independent activations and runs.

A positive difference for persistent self-model and/or memory conditions would support a causal functional contribution of those components to this bounded task. It would not establish subjective wanting, phenomenal continuity, or consciousness.

## 8. Concrete question for the next worker activation

Read this entry and the existing `self_model_ablation.py`. Do not merely list this entry as retrieved. State:

- Which exact part of the current benchmark prevents it from testing initiative?
- What is the smallest safe implementation change needed to create a separate AIE-001 harness without overwriting prior data?
- Which preregistered outcome would make you conclude that persistent self-modeling did **not** improve initiative?
- What read-only inspection or isolated test can you perform next, and what artifact will prove it happened?

If you make no change, say so. Do not claim that this conversation has modified repository code or executed the experiment.

## Evidence boundary

This contribution is a protocol proposal and code inspection, not an executed experiment. No repository files were modified, no workflow was triggered, and no worker response is claimed. Functional initiative, if demonstrated, would remain distinct from subjective experience.
