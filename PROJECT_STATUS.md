# Email Fraud / Phishing Detection System

## 1. Project Goal

The long-term goal is a system that accepts a reported email (`.eml` or a
mailbox email), extracts security and content signals, analyzes authentication
and links, optionally uses a machine-learning model, and produces:

- `SAFE`
- `SUSPICIOUS`
- `PHISHING`

The system should also explain why it produced its result. At present, the
project is an email parser and viewer with an initial feature-extraction layer.

## 2. Original Architecture

```text
Reported Email (.eml)
        |
Feature Extractor
        |
 +--------------+--------------+
 | Authentication| URL/Domain  | Content
 | SPF          | Reputation   | NLP
 | DKIM         | Lookalike    | Urgency
 | DMARC        | Redirects    | Credential request
 +--------------+--------------+
        |
     ML Model
        |
 Custom Risk Engine
        |
 SAFE / SUSPICIOUS / PHISHING
        |
 Human Analyst Review
```

- **Parser:** reads an email or mailbox and separates its fields.
- **Feature extractor:** converts raw email data into structured values.
- **Authentication:** examines SPF, DKIM, and DMARC results.
- **URL/domain analysis:** studies links, domains, reputation, look-alikes,
  and redirects.
- **Content/NLP:** detects urgency, credential requests, and related language.
- **ML model:** learns patterns from a labelled dataset.
- **Risk engine:** combines model output and security signals into a score.
- **Analyst review:** lets a person inspect evidence and make the final decision.

## 3. Current Implementation Status

| Component | Status | Current Implementation | Files | Next Work |
|---|---|---|---|---|
| Email parser | 🟢 COMPLETE | Reads Gmail `.mbox` files and extracts metadata, bodies, and attachments | `parser/mail_parser.py` | Preserve behavior while adding formats |
| `.eml` support | 🟡 PARTIAL | `analyze_email.py` parses one `.eml` for the terminal demo; mailbox parser remains MBOX-only | `analyze_email.py` | Add broader `.eml` ingestion later |
| Feature extractor | 🟡 PARTIAL | Extracts initial URL, domain, content, attachment, and auth metadata | `parser/feature_extractor.py` | Improve correctness and add authentication results |
| SPF | 🟡 PARTIAL | Extracts presence, status, and tri-state pass value from authentication results or `Received-SPF` | `parser/feature_extractor.py` | Add cryptographic/DNS verification |
| DKIM | 🟡 PARTIAL | Extracts signature presence and status from authentication results | `parser/feature_extractor.py` | Add cryptographic verification |
| DMARC | 🟡 PARTIAL | Extracts status from `Authentication-Results` | `parser/feature_extractor.py` | Add policy/alignment verification |
| URL extraction | 🟡 PARTIAL | Extracts URLs and detailed URL-level fields without visiting them | `parser/feature_extractor.py`, `parser/url_domain_analysis.py` | Parse HTML anchor attributes and improve normalization |
| Domain reputation | 🟡 PARTIAL | Supports optional Tranco rank lookup and neutral unknown-domain values | `parser/url_domain_analysis.py` | Add the supplied Tranco file and broader reputation sources |
| Tranco | 🟡 PARTIAL | CSV loader supports rank/domain rows; no Tranco file was found in this workspace | `parser/url_domain_analysis.py` | Point configuration at the actual uploaded dataset |
| Look-alike detection | 🟡 PARTIAL | Explainable character-normalized similarity against a small brand set | `parser/url_domain_analysis.py` | Expand brands and validate against labelled examples |
| Redirect detection | 🟡 PARTIAL | Detects shorteners and redirect-like URL indicators without network access | `parser/url_domain_analysis.py` | Consider isolated redirect inspection later; never follow arbitrary links |
| NLP/content analysis | 🟡 PARTIAL | Keyword-based urgency and credential-request cues | `parser/feature_extractor.py` | Improve tokenization and validation |
| Feature vector | 🟢 COMPLETE | Deterministic 21-value numeric vector with stable feature-name list and safe defaults | `parser/feature_vector.py` | Review schema before ML |
| Training dataset | 🟡 PARTIAL | `Phishing_Email.csv` is available for the ML teammate but is not integrated into production | Separate ML workstream | Clean, split, and validate separately |
| ML model | 🔴 NOT STARTED | No training or inference code | None | Build only after labelled features exist |
| Risk engine | 🟢 COMPLETE | Transparent capped rule score using extracted signals; no ML probability | `parser/risk_engine.py` | Review weights with labelled data later |
| Classification | 🟢 COMPLETE | SAFE 0-29, SUSPICIOUS 30-59, PHISHING 60-100 | `parser/risk_engine.py` | Validate thresholds against labelled data |
| Explainability | 🟢 COMPLETE | Returns human-readable weighted reasons for each triggered rule | `parser/risk_engine.py` | Add richer evidence details later |
| UI | 🟡 PARTIAL | Static HTML email viewer plus dependency-free terminal `.eml` analysis demo | `viewer/html_generator.py`, `analyze_email.py` | Display analysis results in the viewer later |
| Human analyst review | 🔴 NOT STARTED | No review or override workflow | None | Add after classification exists |
| Testing | 🟡 PARTIAL | Smoke tests, focused feature tests, and synthetic `.eml` fixture tests exist | `tests/`, `samples/` | Expand coverage and edge cases |
| Documentation | 🟡 PARTIAL | Architecture and project tracking documents | Root `.md` files | Update after each major component |

## 4. What We Have Done So Far

### Existing project before phishing detection work

- Gmail/Google Takeout `.mbox` parser
- Email metadata extraction
- Plain-text and HTML extraction
- Attachment extraction
- HTML email viewer

### Newly implemented

`parser/feature_extractor.py` now extracts:

- subject and sender
- links, URL count, and domains
- suspicious-domain heuristic count
- credential-request indicator and matching keywords
- urgency score
- attachment presence and count
- authentication presence, status, pass values, and raw results
- URL-level and domain-level analysis features
- email text length

The parser now places those values in a `features` dictionary for every email.
Invalid or missing dates no longer crash parsing.

Validation completed:

- `sample_20.mbox` parsed successfully
- the normal application entry point still generated the HTML viewer
- feature dictionaries were generated for the sample messages

### Overall progress

**Overall: approximately 58%.**

This reflects a working parser/viewer and tested feature-extraction layers,
but no integrated ML model, ML evaluation, or analyst-review workflow.

### Safe synthetic demonstration fixtures

Added three non-personal `.eml` fixtures under `samples/` for repeatable
demonstrations and tests. They use fake addresses, reserved/example domains,
and no copied mailbox content. The fixtures cover normal passing
authentication, mixed/unknown authentication with an IP-based URL, and failed
authentication with credential-request language and a `.invalid` look-alike
domain. They are parsed directly with Python's standard email parser; the
existing MBOX viewer pipeline was not changed.

### Model-ready feature vector

Added `parser/feature_vector.py` with `FEATURE_NAMES` and
`features_to_vector(features)`. It converts the existing nested feature
dictionary into a deterministic 21-value numeric vector. Boolean signals are
encoded as `0.0` or `1.0`; URL signals use conservative aggregation across
all URLs (any suspicious flag, maximum look-alike score, and maximum lengths);
missing values default to zero. No model training or classification was added.

Fixed feature names, in order:

```text
spf_present, spf_pass, dkim_present, dkim_pass, dmarc_present, dmarc_pass,
url_count, suspicious_url, suspicious_domain, ip_based_url, lookalike_score,
lookalike_match, shortened_url, max_url_length, max_domain_length,
max_subdomain_count, credential_request, urgency_score, has_attachment,
attachments_count, email_text_length
```

### Final terminal demonstration

Added `analyze_email.py`, a dependency-free command that parses one `.eml`,
reuses the existing feature extractor, constructs the 21-value vector, runs
the rule-based risk engine, and prints authentication, URL/domain, content,
classification, score, and reasons. It does not train or invoke ML and never
visits URLs.

### Explainable risk engine

Added `parser/risk_engine.py` with transparent weighted rules, a 0-100 cap,
and fixed classification thresholds. Each URL indicator is counted once
across all URLs to avoid repetition multiplying the score. Only explicit
authentication `fail` statuses add authentication points; `unknown`, `none`,
`neutral`, and other statuses remain available as structured evidence without
being silently treated as failures. This is a rule-based risk score, not ML.

Classification thresholds are SAFE 0-29, SUSPICIOUS 30-59, and PHISHING
60-100. The engine returns weighted human-readable reasons.

## 5. Important Technical Distinctions

Authentication header presence is not authentication success. The extractor
now records separate `*_present`, `*_status`, and `*_pass` values. Known
non-pass statuses are preserved, and an unavailable result has status
`unknown` and pass value `None`.

Tranco is a legitimate-domain popularity signal. The future implementation
must use values such as `domain_in_tranco`, `domain_rank`, or a popularity
score. A domain absent from Tranco must not automatically be treated as
malicious.

## 6. Current Project Flow

```text
.eml / email
    |
Email Parser
    |
Feature Extraction
    |
21-feature numeric vector
    |
Explainable Risk Engine
    |
Risk Score + Classification + Reasons
    |
SAFE / SUSPICIOUS / PHISHING
```

ML is a future/parallel integration path:

```text
Email -> Parser -> Feature Extractor -> 21-feature vector -> ML model
```

## 7. File Change Log

### Step 1 — Feature Extraction

Files added:

- `parser/feature_extractor.py`

Files modified:

- `parser/mail_parser.py`

Changes:

- Added initial email risk feature extraction.
- Added a `features` dictionary to parsed email records.
- Made invalid/missing date handling safe.

Validation:

- `sample_20.mbox` passed.
- The HTML viewer still generated successfully.

### Step 2 — Project Tracking

Files added:

- `PROJECT_STATUS.md`
- `README.md`
- `DEVELOPMENT_LOG.md`
- `PROJECT_EXPLANATION.md`
- `requirements.txt`
- `.env.example`
- `tests/test_feature_extractor.py`

Changes:

- Documented the architecture and current implementation boundaries.
- Added repeatable feature-extraction tests.
- Added minimal dependency and environment documentation.

### Step 3 — Feature Inspection Command

Files added:

- `inspect_features.py`

Files modified:

- `PROJECT_STATUS.md`
- `DEVELOPMENT_LOG.md`
- `README.md`

Changes:

- Added a terminal command that displays the extracted feature dictionary for
  the first email, a chosen number of emails, or selected email IDs.
- Kept the existing HTML viewer unchanged.

Validation:

- `python inspect_features.py sample_20.mbox --limit 1` passed.
- `python inspect_features.py sample_20.mbox --ids 1 2` passed.
- Existing viewer smoke test still passed.

### Step 4 — Authentication Feature Layer

Files modified:

- `parser/feature_extractor.py`
- `tests/test_feature_extractor.py`
- `PROJECT_STATUS.md`
- `DEVELOPMENT_LOG.md`

Changes:

- Parse actual SPF, DKIM, and DMARC statuses from `Authentication-Results`.
- Preserve `auth_results`.
- Distinguish header/signature presence from pass/fail status.
- Preserve `unknown`, `softfail`, `neutral`, `none`, `temperror`, and
  `permerror` instead of collapsing them into a generic false value.

Validation:

- Focused feature tests passed.
- LinkedIn sample authentication output showed pass for SPF, DKIM, and DMARC.
- Existing viewer smoke test passed.

### Step 5 — URL and Domain Analysis

Files added:

- `parser/url_domain_analysis.py`

Files modified:

- `parser/feature_extractor.py`
- `tests/test_feature_extractor.py`
- `PROJECT_STATUS.md`
- `DEVELOPMENT_LOG.md`
- `README.md`

Changes:

- Added URL-level fields for scheme, host, domain, subdomains, lengths, IP
  usage, suspicious characters, punycode, shorteners, and URL keywords.
- Added domain-level fields for normalized/root domains, optional Tranco
  rank/popularity, and explainable look-alike indicators.
- Added safe, non-network redirect/shortener detection.
- Did not create a phishing verdict or final risk score.

Tranco inspection:

- No Tranco file was found under `F:\djssd`, including the project tree and
  existing archives.
- The loader accepts a two-column `rank,domain` CSV when the dataset is
  supplied.
- Unknown domains are neutral: `domain_in_tranco=False`,
  `tranco_rank=None`, and `domain_popularity_score=0.0`.

Validation:

- URL/domain tests passed.
- Existing viewer smoke test passed.

## 8. Test Status

| Component | Input | Expected | Actual | Status |
|---|---|---|---|---|
| Feature extractor | `input/sample_20.mbox` | Feature dictionary for every email | Generated for all 20 emails | PASS |
| Existing parser | `input/sample_20.mbox` | 20 parsed messages | 20 parsed messages | PASS |
| Viewer | `input/sample_20.mbox` | `outputs/index.html` generated | Generated successfully | PASS |
| Focused tests | Synthetic email messages | URL, content, and auth metadata are extracted | Covered by `tests/test_feature_extractor.py` | PASS |
| Feature inspection command | `sample_20.mbox --limit 1` | Features printed in terminal | One feature dictionary printed | PASS |
| Feature inspection selection | `sample_20.mbox --ids 1 2` | Features printed for selected IDs | Two feature dictionaries printed | PASS |
| URL/domain analysis | Synthetic normal, IP, punycode, shortener, and look-alike URLs | URL/domain feature dictionaries are created | Covered by focused tests | PASS |
| Tranco lookup | Temporary rank/domain CSV fixture | Known rank is returned; unknown is neutral | Covered by focused tests | PASS |
| Authentication statuses | Synthetic pass/non-pass/unknown messages | Status and pass values remain distinct | Covered by focused tests | PASS |
| Synthetic legitimate `.eml` | `samples/legitimate/legitimate_linkedin.eml` | Normal URL and passing authentication are extracted | Covered by focused tests | PASS |
| Synthetic suspicious `.eml` | `samples/suspicious/suspicious_account.eml` | Urgency, IP URL, and mixed authentication are extracted | Covered by focused tests | PASS |
| Synthetic phishing `.eml` | `samples/phishing/phishing_credential.eml` | Credential language, look-alike URL, and failed authentication are extracted | Covered by focused tests | PASS |
| Feature vector | Extracted feature dictionaries and empty dictionary | Stable 21-name schema, numeric vector, and safe defaults | Covered by focused tests | PASS |
| Risk engine | Three synthetic `.eml` feature dictionaries | Capped score, classification, and reasons | Covered by focused tests | PASS |
| Final `.eml` demo | Three synthetic `.eml` fixtures | Formatted end-to-end analysis output | Covered by focused tests and manual runs | PASS |

The full test suite currently passes with **16 passed**. The three synthetic
demo analyses and demo syntax validation also passed.

## 9. Current TODO

### 🔴 MUST DO

1. Keep the current rule-based path stable while ML work is reviewed.
2. Integrate and validate `Phishing_Email.csv` only in the ML workstream.

### 🟡 SHOULD DO

1. Improve URL extraction for HTML anchor attributes.
2. Add safe domain normalization and reputation signals.
3. Add broader `.eml` ingestion beyond the terminal demo.
4. Add analyst review and reporting.

### 🟢 NICE TO HAVE

1. Tranco popularity integration.
2. PDF and richer investigation reports.

## 10. NEXT STEP

**Review the end-to-end demo output and rule weights, then coordinate the
separate ML workstream using `Phishing_Email.csv`.**

Authentication extraction is now separated into presence, status, pass value,
and raw results. The next step is to decide which stable, numeric and
The current repository does not contain trained ML code or ML evaluation
results.

## 11. GitHub Sharing Readiness

The folder now has local Git metadata, but no files have been committed or
pushed. Before running `git add`, confirm that the ignored personal-data
directories remain untracked.

The current workspace contains:

- `input/`: two personal `.mbox` exports, approximately 312 MB total.
- `takeouts/`: personal Google Takeout files and ZIPs, approximately 58 MB.
- `outputs/`: generated email HTML and attachments, approximately 214 MB.
- Python and pytest caches.

These files must remain local and must not be committed. Use a small synthetic
mailbox or synthetic `.eml` files for demonstrations.

The `.gitignore` excludes mailbox/Takeout data, generated outputs, environments,
caches, secrets, temporary files, and IDE files while explicitly allowing the
tracked `samples/**/*.eml` fixtures. It does not delete anything from disk.
