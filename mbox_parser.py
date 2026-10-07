import mailbox
import os

def parse_mbox_file(mbox_path):
    parsed_emails = []
    if not os.path.exists(mbox_path):
        return parsed_emails
    
    mbox = mailbox.mbox(mbox_path)
    for i, message in enumerate(mbox):
        subject = message['subject'] or "No Subject"
        sender = message['from'] or "Unknown Sender"
        
        # Extract body text
        body = ""
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode('errors="ignore"')
        else:
            payload = message.get_payload(decode=True)
            if payload:
                body = payload.decode('errors="ignore"')
                
        parsed_emails.append({
            "id": f"REP-{100+i}",
            "sender": sender,
            "subject": subject,
            "body": body[:200] # snippet
        })
        if len(parsed_emails) >= 20:  # Demo ke liye top 20 le lo
            break
    return parsed_emails