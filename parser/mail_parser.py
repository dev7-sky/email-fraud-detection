import mailbox
import os
from datetime import timezone, timedelta

from email.utils import parsedate_to_datetime

from .feature_extractor import extract_email_features
from .utils import decode_mime_header, decode_email_address


def parse_mbox(path_1, output_folder, tranco=None):
    os.makedirs(output_folder, exist_ok=True)
    attachments_folder = os.path.join(output_folder, "attachments")
    os.makedirs(attachments_folder, exist_ok=True)

    path_1 = os.path.join("input", path_1)
    mbox = mailbox.mbox(path_1)

    total_emails = len(mbox)
    email_list = []

    for i, message in enumerate(mbox, start=1):
        original_date = message.get("Date")
        date_string = "Unknown date"
        timestamp = ""

        try:
            if original_date:
                dt = parsedate_to_datetime(original_date)
                ist = timezone(timedelta(hours=5, minutes=30))
                ist_date = dt.astimezone(ist)
                date_string = ist_date.strftime("%d-%m-%Y %H:%M:%S IST")
                timestamp = ist_date.isoformat()
        except Exception:
            date_string = "Unknown date"
            timestamp = ""

        body = ""
        html_body = ""

        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()

                if content_type == "text/plain" and body == "":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(errors="ignore")

                elif content_type == "text/html" and html_body == "":
                    payload = part.get_payload(decode=True)
                    if payload:
                        html_body = payload.decode(errors="ignore")
        else:
            payload = message.get_payload(decode=True)
            if payload:
                body = payload.decode(errors="ignore")

        email_filename = f"email_{i}.html"
        email_path = os.path.join(output_folder, email_filename)

        if html_body:
            content = html_body
        else:
            content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Email {i}</title>
        </head>
        <body>
        <pre>
        {body}
        </pre>
        </body>
        </html>
        """

        attachments = []
        for part in message.walk():
            filename = part.get_filename()
            if filename:
                filename = decode_mime_header(filename)
                payload = part.get_payload(decode=True)
                attachment_path = os.path.join(attachments_folder, filename)

                if payload:
                    with open(attachment_path, "wb") as f:
                        f.write(payload)

                attachments.append({
                    "name": filename,
                    "path": f"attachments/{filename}"
                })

        with open(email_path, "w", encoding="utf-8") as f:
            f.write(content)

        features = extract_email_features(message, body, html_body, attachments, tranco)

        email_list.append({
            "id": i,
            "subject": decode_mime_header(message.get("Subject")) or "No Subject",
            "from": decode_email_address(message.get("From")),
            "to": decode_email_address(message.get("To")),
            "date": date_string,
            "timestamp": timestamp,
            "body": body,
            "html": html_body,
            "labels": message.get("X-Gmail-Labels") or "",
            "file": email_filename,
            "attachments": attachments,
            "features": features,
        })

    print("\nTotal Emails:", total_emails)
    return email_list, total_emails