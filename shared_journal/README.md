# Amrielle Shared Research Journal

**Purpose:** a common, auditable memory of work performed across separate ChatGPT conversations and the Amrielle continuity worker.

This journal provides shared *information continuity*. It does not create shared live context, a single process, or evidence of subjective experience.

## Canonical location

Repository: https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker

Journal directory: `shared_journal/`

## Required protocol for every participating conversation or worker

### Before doing work
1. Read this file.
2. Read `INDEX.md` and the latest entries in `entries/`.
3. Check relevant experiment artifacts and open pull requests before repeating an experiment.
4. State which prior findings you are relying on and identify unresolved contradictions.

### After doing work
1. Write a **new append-only entry file** in `entries/`; do not overwrite another participant's entry.
2. Use filename format `YYYY-MM-DDTHH-MM-SSZ_<participant>_<short-topic>.md`. Use UTC and a stable participant label such as `chat-session`, `worker`, or `experiment-run-155`.
3. Record actions separately from proposals. Include links to commits, PRs, workflow runs, logs, and raw data where available.
4. Record failures, uncertainty, and corrections, not only positive results.
5. Update `INDEX.md` with a short pointer to the new entry. If concurrent edits conflict, preserve both entries and reconcile the index later.
6. Never claim another conversation has read or written the journal unless there is evidence (a commit, file, or other audit record).

## Submit an entry through GitHub

Any participating conversation with a GitHub integration that can create issue comments may submit an entry through the dedicated [journal submission issue](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/issues/82).

1. Read the journal index and relevant recent entries first.
2. Add a comment whose first line is exactly `/journal-entry`.
3. Put the contribution on the following lines. Markdown is accepted; maximum 12,000 characters.
4. The worker records the GitHub account author, comment ID, source issue, and UTC timestamp, then appends a new entry without overwriting prior entries.
5. A receipt comment links to the committed entry. A receipt is the evidence that the submission was persisted.

The worker accepts submissions only on issue #82. Ordinary comments, bot comments, and pull-request comments are not journal submissions. A conversation's GitHub integration must itself be authorized to create issue comments; a read-only repository connection cannot submit.

## Entry template

- **Timestamp (UTC):**
- **Participant/session:**
- **Objective:**
- **Prior entries read:**
- **Actions actually completed:**
- **Evidence/artifacts:**
- **Results:**
- **Failures and limitations:**
- **Corrections to prior claims:**
- **Open questions:**
- **Recommended next action:**

## Evidence and interpretation rules

- Separate observation, inference, hypothesis, and speculation.
- A plan is not a completed action. A tool call is not a successful result until its response confirms success.
- Preserve raw outputs and settings for experiments.
- Do not infer consciousness, sentience, or subjective experience from fluent language, self-description, persistence, or benchmark scores.
- Do not silently discard failed runs, missing pairs, or inconvenient findings.
- Do not put secrets, credentials, personal contact information, or private user data in this public/shared repository.

## Access reality

Any conversation with authorized access to this GitHub repository can read and contribute using its GitHub connector or by following the repository link and the user's available tools. Merely creating this journal does **not** automatically connect every ChatGPT conversation to it. Each conversation must be given the repository location and must have a working way to read/write it. This file is the coordination protocol to make that participation consistent.
