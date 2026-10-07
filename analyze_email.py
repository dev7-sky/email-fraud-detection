import argparse
from email import policy
from email.parser import BytesParser
from pathlib import Path

from parser.feature_extractor import extract_email_features
from parser.feature_vector import features_to_vector
from parser.risk_engine import calculate_risk


def analyze_file(path):
    message = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
    body = message.get_body(preferencelist=("plain", "html"))
    body_text = body.get_content() if body else ""
    html_body = body_text if body and body.get_content_type() == "text/html" else ""
    plain_body = body_text if not html_body else ""
    features = extract_email_features(message, plain_body, html_body)
    feature_names, feature_vector = features_to_vector(features)
    risk = calculate_risk(features)
    return features, feature_names, feature_vector, risk


def _yes_no(value):
    return "YES" if value else "NO"


def format_analysis(path, features, risk):
    auth = features.get("auth") or {}
    urls = features.get("url_features") or []
    return "\n".join(
        [
            "EMAIL FRAUD ANALYSIS",
            "====================",
            f"File: {path}",
            "",
            f"Classification: {risk['classification']}",
            f"Risk Score: {risk['risk_score']}/100",
            "",
            "Authentication",
            f"SPF: {(auth.get('spf_status') or 'unknown').upper()}",
            f"DKIM: {(auth.get('dkim_status') or 'unknown').upper()}",
            f"DMARC: {(auth.get('dmarc_status') or 'unknown').upper()}",
            "",
            "URL / DOMAIN",
            f"Suspicious URL: {_yes_no(any(item.get('suspicious_url') for item in urls))}",
            f"Suspicious Domain: {_yes_no(any(item.get('suspicious_domain') for item in urls))}",
            f"Look-alike: {_yes_no(any(item.get('lookalike_match') for item in urls))}",
            f"IP-based URL: {_yes_no(any(item.get('is_ip_address') for item in urls))}",
            "",
            "CONTENT",
            f"Credential Request: {_yes_no(features.get('screens_for_credential_request'))}",
            f"Urgency Score: {features.get('urgency_score', 0)}",
            "",
            "Reasons:",
            *[f"- {reason}" for reason in risk["reasons"]],
        ]
    )


def main():
    parser = argparse.ArgumentParser(
        description="Analyze one .eml file with the existing feature pipeline."
    )
    parser.add_argument("email", type=Path, help="Path to an .eml file")
    args = parser.parse_args()

    features, _, _, risk = analyze_file(args.email)
    print(format_analysis(args.email, features, risk))


if __name__ == "__main__":
    main()
