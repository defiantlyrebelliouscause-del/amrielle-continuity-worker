# Community Resource Navigator — pilot specification v1

**Status:** design proposal only; not deployed  
**Prepared:** 2026-11-13  
**Purpose:** help residents find and verify community services without replacing human referral specialists or making eligibility decisions.

## 1. Narrow pilot

Start with a single-region, read-only navigator for food, housing, utility assistance, transportation, and employment resources. The assistant may:
- translate a request into searchable needs and a location scope;
- retrieve records from approved public/provider sources;
- explain a service in plain language;
- show contact details, operating hours, service area, eligibility text, required documents, accessibility and language information;
- prepare questions for a provider or human referral specialist.

It must not determine eligibility, promise a bed/appointment/benefit, rank people by deservingness, submit applications, contact a provider, or share a person's details without explicit authorization. It is not an emergency service.

## 2. Existing ecosystem to complement

Oklahoma's public information already points residents to 211 for food, housing and utility assistance. 211 Eastern Oklahoma advertises phone, live chat, text and online search, 24/7 access, and service across 37 eastern Oklahoma counties; it directs people outside its coverage to 211 Heartline for western Oklahoma. The navigator should route to the correct regional 211 human service rather than create a competing directory.

Initial source candidates:
1. 211 Eastern Oklahoma / its public search interface, within its published coverage.
2. 211 Heartline for western Oklahoma.
3. Official Oklahoma agency pages and local-government pages.
4. Direct service-provider pages or provider-confirmed feeds.
5. Community-submitted corrections, held as unverified until checked.

No scraping of private accounts or non-public 211 systems is assumed. Data access agreements and provider permissions must be obtained where needed.

## 3. Data model and provenance

Use Open Referral Human Services Data Specification (HSDS) 3.3.1 as the preferred interchange model when a source supports it. HSDS separates organizations, services, locations and service-at-location relationships; it also models operating hours/events, service areas, required documents, languages, accessibility, cost options and metadata.

For each normalized record, preserve:
- source publisher and source URL;
- source record identifier and HSDS version;
- retrieved timestamp;
- source last-modified value;
- provider-assured date, if supplied;
- verification method and status;
- field-level provenance for eligibility, hours, location, cost and availability;
- the raw source payload or immutable snapshot hash;
- correction history and reviewer identity/role.

HSDS fields such as `status`, `eligibility_description`, `assured_date`, `last_modified`, `operating_hours`, `events`, `service_areas`, `required_documents`, `languages`, `accessibility` and `metadata` should be retained, not flattened into an untraceable paragraph. Add application-level provenance fields where a source does not provide the needed assurance detail.

## 4. Source and freshness policy

Use a deterministic source policy; the language model must not invent or silently repair provider facts.

- Prefer direct provider or government records for current service facts; use 211 as a human referral and curated-directory source.
- Show the source and the date last checked beside each result.
- If `assured_date` is missing, say “verification date not supplied.”
- If a listing is marked inactive, defunct or temporarily closed, do not present it as an available option.
- Treat capacity, open beds, same-day appointments, pantry distribution times, deadlines and emergency availability as volatile. A directory entry alone never proves availability now; confirm with the provider or 211.
- If sources conflict, show the conflict and offer a human handoff. Do not choose the more convenient claim.
- A pilot may adopt review-age warnings (for example, flag ordinary listings not re-assured in 90 days), but that threshold is a proposed operating rule requiring provider review, not a standard established by HSDS.

## 5. Interaction and matching

Ask only for information needed to find relevant resources: broad need, ZIP code/county or chosen search area, urgency, practical constraints such as transport/accessibility, and preferred language. Allow “skip” for optional fields.

Default to anonymous search. Do not request Social Security numbers, immigration status, bank credentials, diagnosis, detailed case histories, or exact birth dates. Do not retain free-text disclosures by default. If a user chooses to save or send a referral summary, explain exactly what will be shared and obtain consent.

The model may interpret natural language and explain results. Deterministic code must enforce geography, service status, date checks, and required safety rules. A human must handle disputed eligibility, exceptions, sensitive cases, and consequential decisions.

## 6. Result format

Return at most three clearly relevant options, not an opaque “best” ranking. For each option show:
- what the service does and why it may fit;
- who it serves and any stated eligibility (or “not specified”);
- location/service area and access mode;
- hours and the date/source for those hours;
- fees and required documents, if published;
- languages and accessibility features, if published;
- source link and verification status;
- what the user should confirm before travelling or applying.

Never describe a service as “available now” without a current provider confirmation. Distinguish “listed in directory” from “confirmed by provider.”

## 7. Human handoff and access

Provide one-click or copyable contact details and a plain-language call script. Offer 211 phone, chat, text or online options appropriate to the region. Maintain a non-digital path through libraries, community organizations, caseworkers or printed referral sheets. The system must not make smartphone ownership or broadband access a condition of receiving information.

For crisis or immediate-danger language, stop ordinary matching and display authoritative emergency pathways; do not attempt diagnosis or crisis counselling. Local routing must be validated by the human service owner before launch.

## 8. Accountability and governance

Name a human service owner responsible for the directory, source approvals, corrections, incident response and quarterly review. Maintain:
- source/version and response audit records;
- a visible correction/report-an-error path;
- an appeal/human-review path;
- incident logging and rollback;
- a public statement of system limits, data retention and vendors;
- community review including service providers, people with lived experience, disability advocates and language-access representatives.

Do not use the navigator's logs for policing, immigration enforcement, employment screening, benefit fraud scoring or advertising. Do not train a model on referral conversations without separate, informed authorization and governance approval.

## 9. Evaluation before public release

Build a frozen benchmark of at least 100 realistic, de-identified scenarios with provider-reviewed expected results, including conflicting sources, stale listings, closed services, out-of-area requests, missing fields, language needs, accessibility constraints and volatile availability. Add adversarial prompts that ask the model to invent a provider or guarantee eligibility.

Measure:
- factual precision of provider, phone, address, hours and eligibility claims;
- recall of relevant verified options;
- rate of stale/closed records shown as current;
- false “available now” claims (target: zero);
- correct regional 211 handoff;
- successful human referral or user-confirmed next step;
- performance by language, rurality and accessibility need;
- privacy incidents, correction latency and human override rate.

A provider/caseworker panel should review outputs blind to model version. Report confidence intervals and missing cases. Do not claim success from generated answers alone.

## 10. Stop conditions

Pause the pilot immediately for any fabricated provider/contact, false claim of current capacity, unconsented disclosure, repeated misrouting of crisis cases, or inability to trace a displayed material fact to its source. Resume only after a documented human review and regression test.

## 11. Minimum technical architecture

`approved source adapters -> HSDS-normalized store -> deterministic validation/freshness filters -> retrieval -> language-model explanation/translation -> cited result -> optional human handoff`

The model receives only the minimal records needed for the current query. Every material claim in its answer must map to a source field. The model cannot edit the source directory. Corrections enter a review queue for the human owner.

## 12. Evidence and open questions

Evidence reviewed on 2026-11-13:
- Open Referral HSDS 3.3.1 documents a machine-readable exchange model for organizations, services and locations, including status, eligibility text, assured date, last-modified time, operating hours/events, service areas, required documents, languages, accessibility and metadata.
- 211 Eastern Oklahoma publicly describes four access channels (phone, live chat, text, online), 24/7 access and 37-county coverage, with a western Oklahoma partner.
- Oklahoma's Employment Security Commission points residents to 211 for local food, housing and utility assistance.
- OECD's 2026 review analyzes 50 AI-supported citizen-participation use cases across 22 countries and identifies applications such as translation, transcription, sense-making, virtual assistance, moderation and facilitation, alongside risks and mitigation needs.
- NIST's AI Risk Management Framework is a voluntary lifecycle framework for incorporating trustworthiness into AI design, development, use and evaluation.

Open questions before implementation:
1. Which 211/provider data feeds are contractually available for machine retrieval, and at what update cadence?
2. Who is the named local data steward and who can confirm high-volatility fields?
3. Which languages and accessibility formats should be in the first benchmark?
4. What data-retention and consent rules are acceptable to participating providers and residents?
5. Which independent panel will validate referral outcomes and stop conditions?

**Decision:** proceed only to a source-access and governance feasibility study. Do not deploy a public-facing navigator until provider permission, named human ownership, verified source coverage and benchmark results exist.
