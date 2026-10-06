# Project Explanation

## Problem

Phishing emails try to make a person click a link, reveal credentials, open
an attachment, or transfer money. Important evidence is spread across headers,
links, and message wording, so inspecting it manually is slow.

## Solution

We are building an email-analysis system that turns a reported email into
structured evidence. Later, a model and a separate risk engine will combine
that evidence and explain the result to a human analyst.

## Input

The current input is a Gmail/Google Takeout `.mbox` file. Individual `.eml`
support is planned but is not implemented yet.

## Processing

1. The parser reads each message.
2. It extracts headers, date, body, HTML, and attachments.
3. The feature extractor records links, domains, urgency terms,
   credential-request terms, attachment counts, and authentication metadata.
4. The current application displays the email in an HTML viewer.
5. Future components will create a feature vector, make a prediction, score
   risk, and show reasons.

## Features

Current examples include:

- number of URLs
- unique domains
- suspicious-domain heuristic count
- credential keywords
- urgency score
- attachment count
- SPF/DKIM/DMARC header presence and raw authentication results

Presence is not the same as a verified pass. This distinction is part of the
next authentication-analysis step.

## ML

Machine learning may help recognize combinations of signals that are difficult
to capture with individual rules. It cannot be built responsibly until we have
a labelled dataset and a defined feature-vector schema. There is no ML model
in the current project.

## Risk Engine

A separate risk engine is useful because a model probability is not the whole
investigation decision. The engine can combine model output, authentication
results, domain evidence, content signals, and explanations using documented
thresholds. The risk engine is not implemented yet.

## Output

Current output is a searchable HTML email viewer. The future output will
contain a classification, a risk score, and evidence such as:

```text
Risk Score: 91/100
Classification: PHISHING
Reasons:
- DMARC authentication failed
- The link domain resembles a trusted brand
- The message requests credentials
- Urgent language was detected
```

## Example

An email with a subject such as “Urgent: verify your account today”, a
credential-request phrase, and a link to an unfamiliar domain would produce
high content and URL-related feature values. That does not automatically prove
phishing; authentication and domain analysis are also needed.

## Limitations

The current system:

- reads `.mbox`, not `.eml`
- does not verify SPF, DKIM, or DMARC
- has no Tranco or reputation integration
- has no labelled phishing dataset
- has no ML model or risk score
- has no SAFE/SUSPICIOUS/PHISHING classification
- has no analyst review workflow

## Viva Explanation

### 30 seconds

This project analyzes reported emails for phishing evidence. It first parses
the mailbox, extracts email content, links, domains, attachments, and header
metadata, and displays the result in a viewer. The planned system will add
authentication analysis, a trained model, a risk engine, and explanations so
an analyst can understand the final classification.

### 2 minutes

Phishing detection should not depend on one keyword or one blacklist. The
system therefore separates the problem into stages. The parser reads the
email and preserves its headers, body, HTML, and attachments. The feature
extractor converts those raw values into structured evidence, such as URL
count, domains, urgency terms, credential requests, and authentication
metadata. Authentication analysis will distinguish whether SPF, DKIM, and
DMARC are merely present from whether they passed. URL and domain analysis
will later use reputation, popularity, look-alike, and redirect signals.
After a labelled dataset is available, an ML model can learn useful patterns.
A separate risk engine will combine that model output with security evidence,
produce SAFE, SUSPICIOUS, or PHISHING, and list the reasons. A human analyst
remains responsible for the final review. At the current stage, the parser,
initial feature extractor, and HTML viewer work, but the ML and risk layers
do not exist yet.
