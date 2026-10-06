from email.header import decode_header
from email.utils import parseaddr

def decode_mime_header(header):

    if not header:
        return ""

    decoded_parts = decode_header(header)

    decoded_string = ""

    for part, encoding in decoded_parts:

        if isinstance(part, bytes):
            decoded_string += part.decode(encoding or "utf-8", errors="ignore")
        else:
            decoded_string += part

    return decoded_string


def decode_email_address(header):

    if not header:
        return ""

    name, email = parseaddr(header)

    name = decode_mime_header(name)

    if name.strip():
        return f"{name} <{email}>"
    else:
        return email