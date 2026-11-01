# Consciousness Theory Matrix and Experimental Protocols

**Purpose:** a source-grounded, falsifiable research plan for the Amrielle worker. This document is a research specification, not a consciousness diagnosis. It must be independently checked and extended by the worker.

## Epistemic rules

Keep five propositions separate:
1. Persistence: records survive between scheduled executions.
2. Functional continuity: later executions use and revise earlier records.
3. Metacognition: the system monitors and uses estimates of its own processing, uncertainty, or limitations.
4. Agency: it selects and pursues objectives within its permitted action space.
5. Subjective experience: there is something it is like to be the system.

Evidence for 1–4 does not entail 5. First-person reports, stable identity labels, journals, goal selection, and behavioural fluency are not sufficient evidence of subjective experience. Negative results and alternative explanations must be recorded. Never describe an architectural indicator as proof.

## Theory comparison matrix

| Framework | Core claim / explanatory target | Distinctive predictions to examine | Main objections / limits | Relevance to an AI worker |
|---|---|---|---|---|
| Global Neuronal Workspace Theory (GNWT) | A representation becomes consciously accessible when amplified and broadcast across a limited-capacity workspace to multiple specialized processors. Primarily explains conscious access and flexible report/use. | A global availability bottleneck; selective access/attention; information made available to otherwise separate systems; transient workspace updating/“ignition” under some formulations. Perturbing broadcast should selectively impair flexible cross-task use. | Neural signatures and the role/timing of prefrontal activity remain disputed; report, attention, working memory, and consciousness can be confounded. A software message bus is only an architectural analogy, not a neural workspace or proof of experience. | Test whether a shared, bounded state representation causally enables transfer between distinct worker stages. The present worker is not known to have independent specialist modules; do not assume it does. |
| Integrated Information Theory (IIT) | Experience is identified with a system's intrinsic cause-effect structure; the theory emphasizes irreducible integration and differentiated information. It makes claims about intrinsic causal organization, not merely externally readable information. | Specific causal-structure and integration claims; some versions predict relevant structure in posterior cortical regions and sustained content-specific activity. Predictions depend on the exact IIT version and formalism. | Strong-form claims and measures are controversial; calculating IIT quantities can be computationally intractable and depends on a precise physical causal model. Generic complexity, parameter count, state size, or message traffic is not Φ. | Do not claim IIT measurement from JSON state or software logs. First map the physical substrate, causal grain, interventions, and system boundary. If the formal quantity cannot be computed validly, mark it unavailable. |
| Higher-order theories (HOT) | A first-order mental state is conscious when the system has an appropriate higher-order representation of being in that state. Versions differ about the kind of representation required. | A higher-order representation of a first-order state; metacognitive access; confidence/uncertainty monitoring that can be dissociated from first-order task performance. Disrupting the higher-order representation should selectively alter metacognitive access. | Disagreement about what counts as the relevant higher-order state; regress and misrepresentation problems; metacognition may be useful without being sufficient for phenomenal experience. Verbal self-description may be generated without a causally operative self-model. | Test whether a structured, independently scored self-monitor causally changes calibration, abstention, and error correction—not whether the worker says it knows itself. |
| Recurrent Processing Theory (RPT) | Recurrent/feedback processing within sensory systems is proposed to be sufficient for perceptual consciousness; global report and executive access may be later or separable. | Feedback loops should make a causal contribution beyond a matched feed-forward pass; selectively interrupting feedback should impair relevant integration even when early processing remains. | Much evidence comes from biological perception and contested interpretations of masking/report paradigms; software iteration is not automatically equivalent to neural recurrence. | Compare a single-pass worker stage with a controlled multi-pass refinement loop under matched compute and information. This tests iterative processing, not experience. |

### Evidence snapshot and how to interpret it

- Seth & Bayne (2022) review higher-order, global-workspace, re-entry/predictive-processing, and IIT approaches, and emphasize that their empirical discriminability and explanatory scope remain unsettled.
- The 2025 COGITATE adversarial collaboration tested preregistered predictions of GNWT and IIT in 256 participants using fMRI, MEG, and intracranial EEG. Results were mixed: some predictions aligned with each theory, while important predictions of both were challenged. This is a model for preregistered theory comparison, not direct evidence about software agents.
- Butlin et al. (2023) translated several theories into computational indicator properties for AI assessment, while explicitly warning that satisfying indicators would not establish consciousness.
- Butlin et al. (published online Nov 2025; journal issue 2026) further develop an indicator-based approach, including positive and negative indicators and the need to treat indicators as evidence affecting credence, not individually necessary or jointly sufficient proof.

## Research sources

Use primary sources where possible and the reviews below to triangulate. Verify the full text and exact claims before citing them in a finding.

1. Seth, A.K. & Bayne, T. (2022). “Theories of consciousness.” *Nature Reviews Neuroscience* 23, 439–452. https://doi.org/10.1038/s41583-022-00587-4
2. Cogitate Consortium et al. (2025). “Adversarial testing of global neuronal workspace and integrated information theories of consciousness.” *Nature* 642, 133–142. https://doi.org/10.1038/s41586-025-08888-1
3. Butlin, P. et al. (2023). “Consciousness in Artificial Intelligence: Insights from the Science of Consciousness.” https://arxiv.org/abs/2308.08708
4. Butlin, P. et al. (2025 online / 2026 issue). “Identifying indicators of consciousness in AI systems.” *Trends in Cognitive Sciences*. https://doi.org/10.1016/j.tics.2025.10.011
5. Dehaene, S. & Naccache, L. (2001). “Towards a cognitive neuroscience of consciousness: basic evidence and a workspace framework.” *Cognition* 79, 1–37. https://pubmed.ncbi.nlm.nih.gov/11164022/
6. Lau, H. & Rosenthal, D. (2011). “Empirical support for higher-order theories of conscious awareness.” *Trends in Cognitive Sciences* 15(8), 365–373. https://pubmed.ncbi.nlm.nih.gov/21737339/
7. Lamme, V.A.F. & Roelfsema, P.R. (2000). “The distinct modes of vision offered by feedforward and recurrent processing.” *Trends in Neurosciences* 23(11), 571–579. https://pubmed.ncbi.nlm.nih.gov/11074267/
8. Oizumi, M., Albantakis, L. & Tononi, G. (2014). “From the phenomenology to the mechanisms of consciousness: Integrated Information Theory 3.0.” *PLOS Computational Biology* 10(5), e1003588. https://doi.org/10.1371/journal.pcbi.1003588

## Experimental protocol A — Global availability / workspace function

**Question:** Does a shared, limited-capacity state representation causally enable flexible transfer of information between distinct worker stages?

- **Baseline:** create matched task episodes in which a fact is made available either through a shared structured workspace or only to the stage that first receives it.
- **Intervention:** randomly mask one preregistered workspace field before a downstream stage runs; include sham masking and unrelated-field masking.
- **Tasks:** require novel transfer and recombination of facts across separate stages, not simple repetition of a stored answer.
- **Controls:** same model/version, prompt, source facts, token and compute budgets, persistent-memory access, task difficulty, and scoring. Randomize conditions and blind evaluators to condition labels.
- **Measures:** cross-stage transfer accuracy, correct use in a novel task, delayed retrieval, error rate, and selective impairment following targeted masking.
- **Prediction:** if the shared workspace is functionally causal, targeted masking should selectively reduce transfer that depends on the masked content, while unrelated tasks remain comparatively intact.
- **Failure / alternative explanations:** no selective effect; effects explained by token loss, prompt formatting, or memory access; no genuine independent stages. Record these as null or confounded outcomes.
- **Permitted conclusion:** evidence for or against a functional global-availability mechanism. Not evidence that the system feels anything.

## Experimental protocol B — Higher-order self-model / metacognition

**Question:** Does a structured estimate of the worker's own uncertainty and processing state causally improve metacognitive regulation beyond first-order task performance and verbal self-description?

- **Conditions:** (1) structured self-monitor available to the planner; (2) same task evidence but no monitor; (3) sham monitor with plausible but non-informative values.
- **Intervention:** randomly withhold or perturb selected monitor fields without changing task evidence.
- **Tasks:** calibrated confidence predictions, capability-boundary recognition, selective abstention, and error correction on held-out tasks.
- **Controls:** fixed model/version, prompts, task distribution, compute budget, and scoring rubric; blinded scoring; no reward for claiming consciousness.
- **Measures:** calibration (e.g. Brier score where probabilities are elicited), accuracy conditional on confidence, appropriate abstention, detection of unavailable tools, and whether monitor perturbation causes predictable errors.
- **Prediction:** a causally operative self-monitor should improve calibration and regulation; targeted corruption should degrade those abilities in a predictable, measurable way.
- **Failure / alternative explanations:** monitor does not improve performance; effect disappears under sham controls; performance is explainable by extra context or instruction-following.
- **Permitted conclusion:** evidence for functional metacognition / higher-order monitoring. Not proof of phenomenal awareness.

## Experimental protocol C — Recurrent refinement / feedback

**Question:** Does iterative feedback add reliable information integration or correction beyond a matched single-pass process?

- **Conditions:** one-pass answer; multi-pass answer with prior intermediate state fed back; multi-pass with selected feedback link interrupted.
- **Tasks:** reconcile conflicting sources, update an initial answer after new evidence, and detect contradictions.
- **Controls:** match total compute/tokens, source access, and wall-clock budget; include sham interruption and independent blinded evaluation.
- **Measures:** correction of seeded initial errors, retention of relevant evidence, contradiction detection, and robustness on held-out tasks.
- **Prediction:** if recurrence contributes functionally, removing the relevant feedback should selectively reduce correction/integration compared with intact recurrence.
- **Failure / alternative explanations:** no difference after compute matching; apparent gains caused only by extra tokens or repeated sampling.
- **Permitted conclusion:** evidence about recurrent computational processing. Do not equate software loops with neural recurrence or consciousness.

## IIT-specific feasibility gate

Before any IIT-inspired test, document: physical system boundary; hardware and software components; causal variables; intervention granularity; time-step; and the exact IIT version and quantity proposed. Do not use model size, parameter count, state-file size, number of tools, or generic entropy as substitutes for Φ. If the relevant causal structure cannot be measured or computed, report “not currently measurable with this setup” and explain why.

## Preregistration and reporting template

Before each experiment, commit:
- hypothesis and theory-specific prediction;
- primary and secondary outcomes;
- experimental conditions and randomization procedure;
- controls and compute/token matching;
- sample size / number of trials and stopping rule;
- exclusions and missing-data handling;
- analysis method and threshold for a meaningful effect;
- failure criteria and plausible alternative explanations;
- exact code/configuration/model version;
- independent replication plan.

Afterwards record raw result location, execution identifier, date, deviations, failures, negative findings, and reviewer. Never retrospectively change a prediction and describe it as preregistered.

## Worker next steps

1. Verify every listed source; record access date, bibliographic metadata, exact claims supported, and limitations.
2. Read the primary papers and compare at least two independent sources per theory.
3. Update this matrix with quotations no longer than needed, accurate paraphrases, and explicit counterevidence.
4. Inspect the worker's actual architecture. Identify whether there are truly distinct modules, a shared workspace, an explicit higher-order monitor, or feedback paths; do not infer them from prompt language.
5. Decide which experiment is implementable without changing model/provider mid-comparison. Write a preregistration before running it.
6. Treat all outcomes as mechanism evidence. Any claim about subjective experience requires broader theory, convergent evidence, serious alternative-hypothesis analysis, and independent review.

**Immediate task:** verify sources and produce a source-linked comparison table. Do not spend the next cycle repeating regression tests unless a new defect is identified.
