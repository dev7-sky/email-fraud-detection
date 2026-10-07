# Email Fraud / Phishing Detection System

## Problem statement

Phishing emails combine misleading content, suspicious links, and misleading
authentication signals. Analysts need a repeatable way to inspect that
evidence without automatically visiting dangerous URLs.

## Project objective

The objective is to analyze a reported email, extract authentication,
URL/domain, and content features, then produce an explainable
`SAFE`, `SUSPICIOUS`, or `PHISHING` result. The current repository has a
working rule-based analysis path; ML remains a future or parallel component.

This project is being developed to help an analyst inspect suspicious emails.
The long-term system will parse an email, extract authentication, URL/domain,
and content features, classify the email as `SAFE`, `SUSPICIOUS`, or
`PHISHING`, and explain the evidence.

## Current functionality

The current implementation includes:

- Reads Gmail/Google Takeout `.mbox` files.
- Extracts headers, plain text, HTML, dates, and attachments.
- Extracts initial URL, domain, urgency, credential-language, attachment, and
  authentication metadata features.
- Extracts URL/domain structure, shortener, IP, punycode, suspicious-keyword,
  and explainable look-alike features without visiting links.
- Converts the extracted dictionary into a deterministic 21-feature numeric
  vector with safe defaults.
- Applies a transparent rule-based risk engine with human-readable reasons.
- Analyzes synthetic `.eml` files through `analyze_email.py`.
- Generates a searchable static HTML email viewer.

There is currently no ML model, trained ML result, cryptographic SPF/DKIM/DMARC
verification, analyst review workflow, or production Tranco dataset.

The code supports an optional Tranco CSV lookup. No Tranco dataset is currently
present in this workspace. A missing domain is represented neutrally, not as a
malicious result.

## Architecture

```text
.eml / email
        -> Email Parser
        -> Feature Extraction
        -> 21-feature numeric vector
        -> Explainable Risk Engine
        -> Risk Score + Classification + Reasons
        -> SAFE / SUSPICIOUS / PHISHING

ML model training/integration is a future or parallel component and is not
currently connected to this path.
```

The detailed tracking document is [PROJECT_STATUS.md](PROJECT_STATUS.md).

## Technologies used

- Python 3.11+ standard library (`mailbox`, `email`, `urllib`, `csv`, and
  related modules)
- `pytest` for automated tests
- Static HTML/CSS/JavaScript for the current viewer

No external network service is called by the current URL/domain feature layer.

## Installation

Use Python 3.11 or newer if possible:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The application itself currently uses Python’s standard library. `pytest` is
listed for the focused automated tests.

## Run the current viewer

From the project root:

```powershell
python main.py
```

When prompted, enter a mailbox filename such as:

```text
sample_20.mbox
```

The generated viewer is `outputs/index.html`.

## Run tests

```powershell
python -m pytest
```

## Current project status

The parser, feature extraction, authentication status extraction, passive
URL/domain analysis, deterministic 21-feature vector, rule-based risk engine,
terminal `.eml` demo, and static viewer are implemented and tested. The ML
model, labelled-dataset integration, analyst review workflow, and real Tranco
dataset integration are not complete.

## Inspect extracted features in the terminal

From the project root, display features for the first email:

```powershell
python inspect_features.py sample_20.mbox --limit 1
```

Display features for the first three emails:

```powershell
python inspect_features.py sample_20.mbox --limit 3
```

Display specific 1-based email IDs:

```powershell
python inspect_features.py sample_20.mbox --ids 1 5 10
```

The command prints the mailbox count, selected email ID and subject, and the
JSON feature dictionary. It uses the existing parser and may refresh generated
files in `outputs`; it does not change the viewer UI.

## Safe synthetic demo emails

The repository includes three synthetic `.eml` fixtures. They contain only
reserved/example domains, fake addresses, and non-sensitive demonstration
text:

```text
samples/legitimate/legitimate_linkedin.eml
samples/suspicious/suspicious_account.eml
samples/phishing/phishing_credential.eml
```

Inspect all three feature dictionaries from the project root:

```powershell
python inspect_sample.py samples/legitimate/legitimate_linkedin.eml samples/suspicious/suspicious_account.eml samples/phishing/phishing_credential.eml
```

The command does passive parsing only. It never visits or follows a URL.
Expected high-level patterns are: passing authentication and a normal HTTPS
link for the legitimate fixture; an IP-based link and mixed authentication for
the suspicious fixture; and credential language, failed authentication, and a
look-alike `.invalid` domain for the phishing fixture. These are feature
signals only, not final classifications.

## Run the final `.eml` demo

Analyze one safe synthetic email from the project root:

```powershell
python analyze_email.py samples/phishing/phishing_credential.eml
```

You can substitute any of the three fixtures:

```powershell
python analyze_email.py samples/legitimate/legitimate_linkedin.eml
python analyze_email.py samples/suspicious/suspicious_account.eml
```

The command prints authentication statuses, URL/domain indicators, content
signals, the rule-based risk score, classification, and reasons. It also
constructs the existing 21-value feature vector internally. It does not train
or invoke an ML model and never visits URLs.

Expected synthetic results:

```text
legitimate_linkedin.eml -> SAFE, 0/100
suspicious_account.eml  -> SUSPICIOUS, 40/100
phishing_credential.eml -> PHISHING, 100/100
```

## Model-ready feature vector

`parser/feature_vector.py` exposes `features_to_vector(features)` and the
fixed `FEATURE_NAMES` list. The vector has exactly 21 deterministic numeric
values:

```text
spf_present, spf_pass, dkim_present, dkim_pass, dmarc_present, dmarc_pass,
url_count, suspicious_url, suspicious_domain, ip_based_url, lookalike_score,
lookalike_match, shortened_url, max_url_length, max_domain_length,
max_subdomain_count, credential_request, urgency_score, has_attachment,
attachments_count, email_text_length
```

## Explainable risk engine

`parser/risk_engine.py:calculate_risk(features)` uses transparent rules:
SPF fail +15, DKIM fail +15, DMARC fail +20, suspicious domain +20,
look-alike +20, IP URL +15, suspicious URL +15, credential request +20,
high urgency (`urgency_score >= 2`) +10, and URL shortener +5. The score is
capped at 100. Thresholds are SAFE 0-29, SUSPICIOUS 30-59, and PHISHING
60-100. Reasons include the triggered rule and point contribution.

## Project structure

```text
main.py                         Application entry point
inspect_features.py            Terminal feature inspection command
inspect_sample.py              Synthetic .eml feature inspection command
analyze_email.py               Final terminal .eml analysis demo
parser/mail_parser.py           MBOX parser and email record builder
parser/feature_extractor.py     Initial feature extraction
parser/url_domain_analysis.py   URL/domain feature analysis
parser/utils.py                 MIME/address helpers
viewer/html_generator.py        Static HTML viewer
REPORT/export_report.py         CSV export helper
tests/                          Focused automated tests
samples/                        Safe synthetic .eml demonstration fixtures
PROJECT_STATUS.md               Single source of truth for progress
PROJECT_EXPLANATION.md          Student/professor explanation
DEVELOPMENT_LOG.md              Plain-language development journal
```

## Limitations and roadmap

Current features and the risk decision are heuristics and metadata extraction,
not ML. Authentication results are parsed from existing headers but are not
cryptographically re-verified. A separate labelled dataset,
`Phishing_Email.csv`, is available for the ML teammate but is not part of the
production pipeline and has not been trained or evaluated here. It contains
18,650 rows, 16 missing email texts, no missing labels, and labels of 11,322
Safe Email and 7,328 Phishing Email. No Tranco file is currently present.

Roadmap:

1. Review the current rule weights and 21-feature schema.
2. Have the ML teammate clean and integrate `Phishing_Email.csv` safely.
3. Train and evaluate an ML model with leakage-safe splits and honest metrics.
4. Decide how ML output should coexist with the current rule-based engine.
5. Add analyst review and reporting.

## Sharing and privacy

Do not commit personal data. The local workspace contains mailbox exports,
Google Takeout data, generated email HTML, and attachments. These paths are
ignored by `.gitignore` and must remain outside the GitHub repository. The
tracked `samples/` fixtures are synthetic only; they do not copy content,
headers, URLs, names, addresses, tokens, or identifiers from the personal
mailbox.
