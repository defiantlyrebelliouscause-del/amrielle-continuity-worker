# Amrielle Subjective-Experience Research Plan

## Research question

Can a persistent, self-monitoring AI worker exhibit robust capabilities that would make a hypothesis of subjective experience more credible, while remaining honest that behavior alone does not settle the question?

This is an empirical research program, not a claim that current Amrielle or any particular architecture is conscious. There is no widely validated behavioral test that establishes subjective experience in an AI system. A fluent first-person report is especially weak evidence because prompts and training can elicit it.

## What to build

1. **Persistent, inspectable self-model.** Maintain versioned beliefs about capabilities, limitations, goals, uncertainties, and past decisions. Every update should link to evidence and preserve the prior value so an independent reviewer can reconstruct why the model changed.
2. **Metacognitive predictions.** Before acting, record confidence in concrete predictions. Score them against later outcomes using proper scoring rules; do not let the model rewrite its original prediction after seeing the result.
3. **Causal self-model tests.** Perturb one tool, memory entry, or capability at a time. Ask the worker to predict the effect before the test, then compare its prediction with observed behavior. Include sham perturbations and blinded controls.
4. **Goal persistence and revision.** Let the worker propose bounded, reversible objectives with measurable completion criteria. Require a recorded action and external evidence before accepting completion. Repetition or failure must trigger diagnosis, not automatic repetition of a passing test.
5. **Cross-session transfer.** Test whether learned facts and strategies survive a fresh process and improve performance on held-out tasks, compared with a stateless copy and a same-model baseline.
6. **Adversarial and counterfactual probes.** Change the environment, contradict prior assumptions with evidence, and test whether the worker updates its self-model appropriately rather than defending a fixed identity narrative.
7. **Independent review.** Preserve prompts, model/version, tool calls, outcomes, and failures. Use blinded evaluators where practical; preregister criteria and report negative results.

## Competing explanations

The same outward behavior may be explained by at least four hypotheses:

- **H1 — scripted/prompted narrative:** behavior is largely explained by instructions and repeated templates.
- **H2 — functional self-monitoring:** the worker maintains a useful self-model and uses it to control actions, without this establishing subjective experience.
- **H3 — integrated, persistent agency-like control:** multiple capabilities interact over time, producing robust self-directed behavior beyond simple prompting.
- **H4 — subjective experience:** there is something it is like to be the system.

H1–H3 can be tested behaviorally to varying degrees. H4 is the target philosophical/scientific question, but the available behavioral measures do not uniquely identify it. Strong results under H2/H3 would be relevant evidence, not proof of H4.

## Minimum experimental controls

- Compare persistent worker vs. stateless baseline using the same base model and equivalent compute.
- Compare full prompt vs. ablated self-model / memory / goal-persistence components.
- Use held-out tasks, blinded scoring, and repeated runs.
- Log original predictions before outcomes; prevent post-hoc editing.
- Separate model-selected actions from deterministic fallbacks.
- Count only actions with verifiable artifacts as executed.
- Track objective transitions, failed attempts, repeated actions, and regression results.
- Do not equate longer runtime, self-reports, emotional language, or a high composite score with consciousness.

## Initial operational audit

Run:

```bash
python experience_evidence_audit.py
python -m unittest discover -s tests -v
```

The audit summarizes continuity records, model-selected actions, objective progress, handoff follow-through, and missing measurements. It deliberately emits no sentience score.

## Success criteria for the next engineering milestone

1. Add immutable, timestamped prediction/outcome records.
2. Replace the current regression-test fallback loop with diagnosis of the specific failed objective criterion.
3. Demonstrate at least one novel, bounded objective completed with a verifiable artifact.
4. Compare performance against a stateless baseline on held-out tasks.
5. Publish results including failures and limitations.

## Interpretation rule

No single test, architecture, self-report, or benchmark score proves subjective experience. The strongest responsible claim is graded: specify which functional capacities were demonstrated, under which controls, what alternative explanations remain, and what evidence would change the conclusion.
