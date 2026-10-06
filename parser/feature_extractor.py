import re
from urllib.parse import urlparse
from .url_domain_analysis import analyze_urls


CREDENTIAL_KEYWORDS = [
    "password",
    "verify your account",
    "confirm your account",
    "reset your password",
    "login",
    "sign in",
    "bank account",
    "credentials",
    "security alert",
    "update your details",
    "suspicious activity",
    "urgent action required",
    "click here",
]

URGENT_KEYWORDS = [
    "urgent",
    "immediately",
    "today",
    "asap",
    "act now",
    "limited time",
    "final warning",
    "within 24 hours",
    "expires today",
    "important",
]

SUSPICIOUS_TLDS = {"xyz", "top", "loan", "click", "info", "bid", "club", "tk", "ga", "cf", "ml"}
AUTH_STATUSES = {"pass", "fail", "softfail", "neutral", "none", "temperror", "permerror"}


def _normalise_text(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def _extract_urls(text):
    if not text:
        return []
    matches = re.findall(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", text, flags=re.IGNORECASE)
    urls = []
    for match in matches:
        cleaned = match.rstrip(".,;:)")
        if cleaned not in urls:
            urls.append(cleaned)
    return urls


def _domain_from_url(url):
    try:
        parsed = urlparse(url if url.startswith(("http://", "https://")) else "https://" + url)
        return parsed.netloc.lower().replace("www.", "")
    except Exception:
        return ""


def _detect_suspicious_domain(domain):
    if not domain:
        return False
    domain = domain.lower().strip(".")
    if any(part in domain for part in ["bit.ly", "tinyurl", "goo.gl", "t.co", "dropbox", "drive.google"]):
        return False
    if re.search(r"(\w)\1{3,}", domain):
        return True
    if domain.count(".") >= 2:
        return True
    tld = domain.split(".")[-1]
    if tld in SUSPICIOUS_TLDS:
        return True
    return False


def _count_urgent_language(text):
    text = _normalise_text(text)
    return sum(1 for keyword in URGENT_KEYWORDS if keyword in text)


def _count_credential_terms(text):
    text = _normalise_text(text)
    return sum(1 for keyword in CREDENTIAL_KEYWORDS if keyword in text)


def _authentication_status(auth_results, header_value, mechanism):
    sources = [auth_results, header_value]
    pattern = re.compile(
        rf"\b{re.escape(mechanism)}\s*=\s*({'|'.join(sorted(AUTH_STATUSES, key=len, reverse=True))})\b",
        flags=re.IGNORECASE,
    )
    for source in sources:
        match = pattern.search(source or "")
        if match:
            return match.group(1).lower()
    return "unknown"


def _authentication_pass_value(status):
    if status == "pass":
        return True
    if status == "unknown":
        return None
    return False


def extract_email_features(message, body_text="", html_body="", attachments=None, tranco=None):
    text_blob = body_text or html_body or ""
    urls = _extract_urls(text_blob)
    domains = []
    for url in urls:
        domain = _domain_from_url(url)
        if domain:
            domains.append(domain)

    unique_domains = []
    for domain in domains:
        if domain not in unique_domains:
            unique_domains.append(domain)

    subject = message.get("Subject") or ""
    sender = message.get("From") or ""
    headers = message.keys() if hasattr(message, "keys") else []
    auth_result_values = message.get_all("Authentication-Results", []) if hasattr(message, "get_all") else []
    auth_results = "\n".join(auth_result_values) or (message.get("Authentication-Results") or "")
    dkim_header = message.get("DKIM-Signature") or ""
    spf_header = message.get("Received-SPF") or ""
    spf_status = _authentication_status(auth_results, spf_header, "spf")
    dkim_status = _authentication_status(auth_results, dkim_header, "dkim")
    dmarc_status = _authentication_status(auth_results, "", "dmarc")

    url_features, domain_features = analyze_urls(urls, tranco)
    features = {
        "subject": subject,
        "sender": sender,
        "has_link": bool(urls),
        "url_count": len(urls),
        "urls": urls,
        "url_features": url_features,
        "domain_features": domain_features,
        "domains": unique_domains,
        "suspicious_domain_count": sum(1 for d in unique_domains if _detect_suspicious_domain(d)),
        "screens_for_credential_request": _count_credential_terms(text_blob + " " + subject) > 0,
        "credential_keywords_found": [kw for kw in CREDENTIAL_KEYWORDS if kw in _normalise_text(text_blob + " " + subject)],
        "urgency_score": _count_urgent_language(text_blob + " " + subject),
        "has_attachment": bool(attachments),
        "attachments_count": len(attachments or []),
        "auth": {
            "spf_present": bool(spf_header or re.search(r"\bspf\s*=", auth_results, re.IGNORECASE)),
            "spf_status": spf_status,
            "spf_pass": _authentication_pass_value(spf_status),
            "dkim_present": bool(dkim_header or re.search(r"\bdkim\s*=", auth_results, re.IGNORECASE)),
            "dkim_status": dkim_status,
            "dkim_pass": _authentication_pass_value(dkim_status),
            "dmarc_present": bool(re.search(r"\bdmarc\s*=", auth_results, re.IGNORECASE)),
            "dmarc_status": dmarc_status,
            "dmarc_pass": _authentication_pass_value(dmarc_status),
            "auth_results": auth_results,
            "header_keys": list(headers),
        },
        "email_text_length": len(text_blob),
    }

    return features
