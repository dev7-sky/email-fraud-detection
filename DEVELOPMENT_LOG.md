# Development Log

This journal records meaningful project changes in chronological order.

## Step 1 — Feature Extraction

**Date:** 2026-10-07

**What I did:** Created a feature extractor for email URLs, domains,
credential-request language, urgency, attachments, and authentication metadata.

**Files:** `parser/feature_extractor.py`, `parser/mail_parser.py`

**Testing:** Parsed `input/sample_20.mbox` and ran the normal application entry
point.

**Result:** PASS. Twenty messages were parsed, feature dictionaries were
created, and the HTML viewer was generated.

**Next:** Authentication analysis.

## Step 2 — Project Tracking

**Date:** 2026-10-07

**What I did:** Added project status, README, explanation, dependency,
environment, and focused test files.

**Files:** `PROJECT_STATUS.md`, `README.md`, `PROJECT_EXPLANATION.md`,
`requirements.txt`, `.env.example`, `tests/test_feature_extractor.py`

**Testing:** Ran focused feature tests and the mailbox smoke test.

**Result:** PASS.

**Next:** Authentication analysis.

## Step 3 — Feature Inspection Command

**Date:** 2026-10-07

**What I did:** Created `inspect_features.py` to print generated feature
dictionaries for one or more mailbox messages.

**Files:** `inspect_features.py`, `PROJECT_STATUS.md`, `DEVELOPMENT_LOG.md`,
`README.md`

**Testing:** Ran the command for one message and selected message IDs, then
ran the viewer smoke test.

**Result:** PASS.

**Next:** Authentication analysis.

## Step 4 — Authentication Feature Layer

**Date:** 2026-10-07

**What I did:** Added separate SPF, DKIM, and DMARC presence, status, and pass
fields. Preserved raw `Authentication-Results` and explicit unknown/non-pass
statuses.

**Files:** `parser/feature_extractor.py`, `tests/test_feature_extractor.py`,
`PROJECT_STATUS.md`, `DEVELOPMENT_LOG.md`

**Testing:** Ran pass, non-pass, and unknown synthetic cases, inspected the
LinkedIn sample, and ran the viewer smoke test.

**Result:** PASS.

**Next:** URL/domain analysis.

## Step 5 — URL and Domain Analysis

**Date:** 2026-10-07

**What I did:** Added URL structure, IP, punycode, shortener, suspicious
keyword, domain, Tranco-lookup, and explainable look-alike features. No URL is
visited.

**Files:** `parser/url_domain_analysis.py`, `parser/feature_extractor.py`,
`parser/mail_parser.py`, `tests/test_feature_extractor.py`,
`PROJECT_STATUS.md`, `DEVELOPMENT_LOG.md`, `README.md`

**Testing:** Ran normal, IP, punycode, shortener, look-alike, known/unknown
Tranco, and multiple-URL tests. Ran the full test suite and viewer smoke test.

**Result:** PASS. Eight tests passed. No Tranco dataset was present in the
workspace; unknown domains remain neutral.

**Next:** Define the model-ready feature-vector schema.

## Step 6 — GitHub Sharing Preparation

**Date:** 2026-10-07

**What I did:** Audited GitHub readiness, added `.gitignore` rules, updated
the README/status documents, and kept `requirements.txt` limited to pytest.

**Why:** The workspace contains personal mailbox exports, Google Takeout
data, generated email HTML, attachments, and caches. These must never be
shared.

**Files:** `.gitignore`, `README.md`, `PROJECT_STATUS.md`,
`DEVELOPMENT_LOG.md`, `requirements.txt`

**Checks:** Initialized local Git metadata without committing or pushing,
measured sensitive and generated directories, verified ignore rules, and found
no API-key/private-key pattern in source or documentation files.

**Result:** Sharing boundaries are documented and ignored locally. The project
is not safe to push until `git status` is checked after initialization and only
source, tests, and documentation are staged.

**Next:** Define and review the model-ready feature-vector schema.

## Step 7 — Safe Synthetic Demonstration Emails

**Date:** 2026-10-07

**What I did:** Added three fully synthetic `.eml` fixtures for safe team
demonstrations and repeatable feature-extraction tests. Added
`inspect_sample.py` to print their feature dictionaries without changing the
viewer.

**Files:** `samples/legitimate/legitimate_linkedin.eml`,
`samples/suspicious/suspicious_account.eml`,
`samples/phishing/phishing_credential.eml`, `inspect_sample.py`,
`tests/test_feature_extractor.py`, `.gitignore`, `README.md`,
`PROJECT_STATUS.md`

**Safety:** The fixtures use fake addresses, reserved/example domains, a
documentation-only IP address, and the reserved `.invalid` TLD. No personal
mailbox content or real malicious destination is included, and no URL is
visited.

**Testing:** Parsed all three `.eml` files with the standard library and
verified legitimate, suspicious, and phishing-oriented feature patterns.

**Result:** PASS. Synthetic fixtures are explicitly unignored and are ready
for GitHub sharing.

**Next:** Define and review the model-ready feature-vector schema.
