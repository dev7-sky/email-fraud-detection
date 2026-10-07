# Project Explanation

## Problem

Phishing emails try to make a person click a link, reveal credentials, open
an attachment, or transfer money. Important evidence is spread across headers,
links, and message wording, so inspecting it manually is slow.

## Current solution

The current system parses an email, extracts structured security and content
signals, creates a deterministic 21-feature numeric vector, and applies a
transparent rule-based risk engine. ML is a separate future or parallel
workstream and is not integrated here.

## Input and processing

The existing parser reads Gmail/Google Takeout `.mbox` files. The terminal
demo accepts an individual `.eml` through `analyze_email.py` using Python's
standard email parser.

1. Parse headers, date, body, HTML, and attachments.
2. Extract SPF, DKIM, DMARC, URL/domain, content, and attachment signals.
3. Convert the feature dictionary with
   `parser/feature_vector.py:features_to_vector` into 21 fixed numeric values.
4. Apply `parser/risk_engine.py:calculate_risk`.
5. Display score, classification, and human-readable reasons.

## Implemented features

- SPF/DKIM/DMARC presence, parsed status, pass values, and raw
  `Authentication-Results`
- URL count, suspicious URL/domain indicators, IP URLs, shorteners,
  look-alike score/match, URL/domain lengths, subdomain count, and passive
  redirect indicators
- Credential keywords, credential-request detection, urgency score, email text
  length, and attachment presence/count
- Static HTML viewer and terminal `.eml` analysis demo

Authentication presence is not the same as cryptographic verification. The
current implementation parses available headers and does not re-verify DNS or
signatures. No URLs are visited.

## Fixed feature vector

The vector has exactly 21 values, in this order:

```text
spf_present, spf_pass, dkim_present, dkim_pass, dmarc_present, dmarc_pass,
url_count, suspicious_url, suspicious_domain, ip_based_url, lookalike_score,
lookalike_match, shortened_url, max_url_length, max_domain_length,
max_subdomain_count, credential_request, urgency_score, has_attachment,
attachments_count, email_text_length
```

Missing values use safe defaults and the output is deterministic.

## Explainable risk engine

The rule engine uses these weights:

- SPF fail +15; DKIM fail +15; DMARC fail +20
- suspicious domain +20; look-alike domain +20
- IP URL +15; suspicious URL +15; URL shortener +5
- credential request +20; high urgency (`urgency_score >= 2`) +10

The score is capped at 100. Classification thresholds are SAFE 0-29,
SUSPICIOUS 30-59, and PHISHING 60-100. Reasons identify each triggered rule
and its contribution. Repeated URL indicators are counted once.

## Demo results

The three synthetic fixtures were manually verified:

```text
samples/legitimate/legitimate_linkedin.eml -> SAFE, 0/100
samples/suspicious/suspicious_account.eml  -> SUSPICIOUS, 40/100
samples/phishing/phishing_credential.eml   -> PHISHING, 100/100
```

Run one with:

```powershell
python analyze_email.py samples/phishing/phishing_credential.eml
```

## ML status

`Phishing_Email.csv` is available to the ML teammate but is not part of the
production pipeline. It contains 18,650 rows, columns `Unnamed: 0`, `Email
Text`, and `Email Type`, with 11,322 `Safe Email` labels and 7,328
`Phishing Email` labels. It has 16 missing email texts and no missing labels.
No ML model has been trained, evaluated, or integrated in this repository, and
no ML accuracy result is claimed.

## Testing

The full suite currently passes with **16 passed**. The three synthetic demos
and demo syntax validation also passed.

## Limitations and next steps

- No cryptographic SPF/DKIM/DMARC verification
- No production Tranco dataset
- No integrated ML model or ML evaluation
- No analyst review workflow
- MBOX parser remains the main mailbox ingestion path

Next, review the current rule weights and coordinate the separate ML
workstream. Do not treat the rule-based score as ML output.
