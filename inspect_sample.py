import argparse
import json
from email import policy
from email.parser import BytesParser
from pathlib import Path

from parser.feature_extractor import extract_email_features


def extract_from_file(path):
    message = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
    body = message.get_body(preferencelist=("plain", "html"))
    body_text = body.get_content() if body else ""
    html_body = body_text if body and body.get_content_type() == "text/html" else ""
    plain_body = body_text if not html_body else ""
    return extract_email_features(message, plain_body, html_body)


def main():
    parser = argparse.ArgumentParser(
        description="Print features for synthetic .eml demonstration files."
    )
    parser.add_argument("emails", nargs="+", type=Path)
    args = parser.parse_args()

    for path in args.emails:
        print(f"\n--- {path} ---")
        print(json.dumps(extract_from_file(path), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
