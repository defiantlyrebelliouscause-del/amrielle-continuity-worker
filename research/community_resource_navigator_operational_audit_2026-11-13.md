# Community Resource Navigator — operational audit

**Date:** 2026-11-13  
**Status:** Design audit only; no provider agreement, ingestion, pilot, or deployment was performed.

## Independently selected question

What must be true before the existing Community Resource Navigator v1 can be responsibly tested with a real community partner, and what does the current evidence say about the proposed operating model?

## Prior design reviewed

Read `research/community_resource_navigator_v1.md`. Its core design is sound as a proposal: read-only referral assistance; HSDS-aligned records; field-level source provenance; no eligibility decisions or promises of current capacity; human handoff; non-digital access; a frozen test set; and explicit stop conditions.

This audit does not replace or silently rewrite v1. It adds operational requirements and records current evidence.

## New evidence reviewed

1. **Inform USA Community Navigation Standards 10.1** — released July 2024 and updated October 2025. Relevant requirements include:
   - multi-channel and barrier-free access (Standards 1.2 and 1.5);
   - consent, confidentiality, retention rules, and protection of personal information (1.6);
   - a feedback and complaint process, including complaints from providers about inaccurate referrals (1.11);
   - crisis-intervention capability or a prearranged agreement and documented protocols with a crisis service (3.1–3.3);
   - follow-up only under a defined protocol and with the person's permission (4.1–4.6);
   - structured organization, location, and service records, with HSDS alignment when directory data are shared with other platforms (8.1–8.5);
   - Database Curator review of updates before publication (10.2);
   - quality assurance using record verification, outcome measurement, and community/provider participation (25.4–25.9).
   Source: https://www.informusa.org/standards

2. **Open Referral HSDS 3.3.1** defines a machine-readable exchange model for organizations, services, locations, and service-at-location relationships. It also models schedules, service areas, required documents, languages, accessibility, costs, metadata, and taxonomy terms. This is a data-exchange standard; it does not prove that any particular 211 directory publishes a feed or grants reuse rights.
   Source: https://docs.openreferral.org/en/v3.3.1/hsds/overview.html

3. **211 Eastern Oklahoma's public site** states that it provides free, confidential assistance 24/7 through phone, live chat, text, and online search, and serves 37 eastern Oklahoma counties. Its statewide 211 page states that the 77-county system is operated by two nonprofit providers: Tulsa Area United Way in the east and Heartline in the west.
   Sources: https://211eok.org/ and https://211eok.org/211-oklahoma/

4. **Oklahoma Employment Security Commission** directs residents to 211 for local food, housing, and utility-assistance information.
   Source: https://oklahoma.gov/oesc/individuals/food-assistance-resources.html

5. **OECD (30 June 2026)** reviewed 50 AI-supported citizen-participation cases across 22 countries. Its recommendations include privacy and security controls, transparency, redress, citizen participation in system governance, and in-person or low-tech alternatives. It cautions against using AI in ways that undermine civic space.
   Source: https://www.oecd.org/en/publications/artificial-intelligence-and-the-future-of-citizen-participation_a1ee2e0a-en/full-report/what-can-governments-do-the-road-to-fit-for-purpose-ai-tools-for-citizen-participation_06b838ee.html

6. **ILO (1 June 2026)** finds workplace GenAI productivity effects uneven and often unverified; reported time savings have not consistently translated into measured output, earnings, or employment. A separate ILO working paper (30 April 2026) identifies psychosocial risks involving surveillance, job autonomy, and data-driven management.
   Sources: https://www.ilo.org/publications/impact-genai-jobs-productivity-and-work-organization-review-empirical and https://www.ilo.org/publications/ai-systems-work-changing-psychosocial-work-environment

7. **NIST AI Resource Center** provides operational resources for testing, evaluation, verification, and validation under the voluntary AI Risk Management Framework.
   Source: https://airc.nist.gov/

## Operational conclusions

### A. Integrate with existing community navigation; do not create a competing directory

The public 211 pages establish that a human referral network and multiple access channels already exist. They do not establish an open API, bulk-data licence, or permission to ingest the 211 database. No machine-readable 211 Eastern Oklahoma feed or reuse agreement was verified in this run.

Therefore the safest first phase is a **link-out and staff-assist model**:
- direct residents to the appropriate 211 phone, chat, text, or public search channel;
- let trained specialists remain responsible for nuanced assessment and referral;
- use only separately approved public agency/provider sources for any locally curated records;
- do not scrape private systems or infer permission from public visibility.

Before ingesting 211 data, obtain written agreement covering allowed fields, access method, update cadence, attribution, retention, security, corrections, and incident response.

### B. Make human ownership operational, not ceremonial

Name four roles before a pilot:
1. **Service owner:** the participating 211 or community organization, accountable for the service and escalation policy.
2. **Database curator:** approves source records and changes before publication.
3. **System operator:** accountable for model/version control, access security, audit, rollback, and incident handling.
4. **Community review group:** providers, people with lived experience, disability and language-access representatives.

AI may draft summaries or proposed updates. It must not publish source-record changes, decide eligibility, allocate scarce resources, or contact providers on its own.

### C. Tighten crisis and follow-up boundaries

The v1 statement that the navigator is not an emergency service is necessary but not sufficient. Inform USA Standard 3 expects a community navigation service either to operate under crisis protocols or have a documented agreement with a qualified crisis service. A pilot that does not provide crisis intervention must use a partner-approved escalation map, clearly disclose its limits, and hand off rather than attempt autonomous assessment or counselling.

Any follow-up contact must be separately permissioned, use the person's preferred channel, and be handled by the accountable service owner. No follow-up should be inferred from a prior search.

### D. Use a staged pilot

- **Stage 0 — link-out:** no ingestion; point to verified official 211 and agency channels.
- **Stage 1 — shadow evaluation:** run synthetic/de-identified benchmark scenarios against approved records; no resident-facing answers and no real personal data.
- **Stage 2 — staff assist:** AI drafts options and plain-language explanations for trained specialists, who verify and approve every response.
- **Stage 3 — limited public read-only access:** only after provider permission, benchmark pass, accessibility review, incident process, and public disclosure are approved.

A stage cannot advance merely because the model produces fluent answers or the workflow completes successfully.

### E. Measure outcomes and harms

Keep the v1 benchmark proposal, but add:
- provider-confirmed accuracy of hours, location, eligibility wording, contact details, and service area;
- stale-record and false-current-availability rates;
- correct routing to the appropriate regional 211 service;
- human specialist correction and override rates;
- referral completion and needs-met/unmet outcomes, collected only with consent;
- results broken down by language, rurality, and accessibility need;
- privacy incidents, complaints, correction latency, and time imposed on staff.

Do not use AI interaction logs for individual worker performance scoring or surveillance. Measure team-level service quality and worker autonomy, not adoption counts alone.

## Continuity architecture cross-check

The idle-worker concept remains separate from the navigator's service workflow. A future host adapter would need authenticated, consented activity events; an append-only event ledger; monotonic activity versions; an idempotent durable queue; unique per-claim fencing tokens; checkpoints; bounded retries/dead-letter handling; and human-return invalidation before any late result can be committed. External side effects require idempotency or human approval.

Current repository evidence:
- PR #74 (fairer shared-journal retrieval) was merged on 12 November 2026. The main-branch loader now parses the complete index and selects distinct participants, but selection still follows index order rather than sorting by timestamp. It also deduplicates by participant label, which can suppress a second, substantively different entry from the same GitHub submitter.
- The latest worker handoff, run 43429131264, lists the 12 November index-correction entry from participant `scheduled-research-cycle` but omits the separate 12 November social-integration audit from that same participant. This is consistent with the participant-deduplication rule. The handoff is otherwise repetitive and does not substantively answer the AIE-001 questions.
- Durable `state.json` is at cycle 1471. Its current objective remains the self-model calibration experiment, not the social-integration workstream. The last reflection has narrative similarity 0.981 and flags repetition; the objective-transition history has 100 attempts. The scheduled worker therefore has persistence, but its current goal progression is not reliably aligned with this social-integration task.
- PR #76 remains an open draft and is marked unmergeable/dirty. Its only associated workflow run, 42397231605, failed. Direct branch inspection confirms three unresolved defects: the HTTP job endpoints reference `now` before assignment; lease ownership uses a reusable worker ID rather than a unique per-claim fencing token; and the activity handler records activity metadata even when the session has opted out. The prototype is not merged or deployed.

No ChatGPT conversation-inactivity signal is exposed to this repository. The current six-hour worker schedule and 15-minute watchdog are bounded external activations, not uninterrupted computation and not proof of background awareness.

## Contradictions and bias checks

- Public access to a 211 website is not the same as permission to ingest its underlying database.
- A directory record is not proof that a service has capacity today.
- A technically correct HSDS import is not proof that a person obtained help.
- A human approval checkbox is not meaningful oversight unless the reviewer has time, information, and authority to reject the output.
- The navigator should not be described as empathetic or trustworthy because it uses warm language; trust must be earned through accurate records, clear limits, privacy, correction, and accountable human relationships.
- The worker's successful GitHub workflow is not evidence of successful research: its current durable state records repetition and a different objective.

## Confidence and limitations

- **High confidence:** what the reviewed Inform USA, HSDS, OECD, ILO, NIST, and official Oklahoma/211 pages state.
- **Moderate confidence:** the proposed staged operating model and role separation; these require validation by a participating 211/community organization.
- **Not established:** provider permission, availability of a machine-readable 211 feed, actual service outcomes, user acceptance, or public-pilot readiness.
- No provider was contacted, no data were ingested, no resident interaction occurred, and no deployment or code test was performed in this audit.

## Next inquiry

Conduct a source-access feasibility review: identify which Oklahoma public-agency and provider datasets can legally and technically be reused, distinguish public web pages from licensed machine-readable feeds, and define the minimum data-sharing agreement for any 211 integration. In parallel, prepare a shadow-mode test set with a community-navigation specialist before exposing any AI-generated answer to residents.
