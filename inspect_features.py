import argparse
import json
import sys

from parser.mail_parser import parse_mbox


def build_parser():
    parser = argparse.ArgumentParser(
        description="Print extracted features for selected emails in an MBOX file."
    )
    parser.add_argument(
        "mailbox",
        help="Mailbox filename located in the input directory, for example sample_20.mbox",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1,
        help="Number of emails to display from the beginning (default: 1)",
    )
    parser.add_argument(
        "--ids",
        type=int,
        nargs="+",
        help="Specific 1-based email IDs to display, for example --ids 1 5 10",
    )
    return parser


def select_emails(emails, limit, ids):
    if ids:
        requested_ids = set(ids)
        return [email for email in emails if email["id"] in requested_ids]

    if limit < 1:
        raise ValueError("--limit must be at least 1")
    return emails[:limit]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    args = build_parser().parse_args()
    emails, total = parse_mbox(args.mailbox, "outputs")
    selected = select_emails(emails, args.limit, args.ids)

    print(f"Mailbox: {args.mailbox}")
    print(f"Total emails: {total}")
    print(f"Displaying: {len(selected)}")

    for email in selected:
        print(f"\n--- Email {email['id']} ---")
        print(f"Subject: {email['subject']}")
        print(json.dumps(email["features"], indent=2, ensure_ascii=False))

    if not selected:
        print("\nNo matching email IDs were found.")


if __name__ == "__main__":
    main()
