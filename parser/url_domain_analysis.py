import csv
import ipaddress
import re
from difflib import SequenceMatcher
from urllib.parse import urlparse


URL_SHORTENERS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "rebrand.ly",
    "cutt.ly",
}
SUSPICIOUS_URL_KEYWORDS = {
    "account",
    "confirm",
    "credential",
    "invoice",
    "login",
    "password",
    "recover",
    "secure",
    "signin",
    "suspend",
    "unlock",
    "verify",
}
LOOKALIKE_BRANDS = {
    "amazon",
    "apple",
    "facebook",
    "google",
    "linkedin",
    "microsoft",
    "netflix",
    "paypal",
}


def _normalise_domain(domain):
    return (domain or "").lower().strip(".").removeprefix("www.")


def registered_domain(domain):
    labels = _normalise_domain(domain).split(".")
    if len(labels) <= 2:
        return ".".join(labels) if labels and labels[0] else ""
    return ".".join(labels[-2:])


def _is_ip(hostname):
    try:
        ipaddress.ip_address(hostname.strip("[]"))
        return True
    except ValueError:
        return False


def _domain_parts(hostname):
    normalized = _normalise_domain(hostname)
    if _is_ip(normalized):
        return normalized, normalized, ""
    root = registered_domain(normalized)
    if root and normalized.endswith("." + root):
        subdomain = normalized[: -(len(root) + 1)]
    else:
        subdomain = ""
    return normalized, root, subdomain


def _lookalike(domain):
    root = registered_domain(domain)
    label = root.rsplit(".", 1)[0] if "." in root else root
    if not label:
        return 0.0, False, ""

    folded = label.translate(str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t"}))
    best_brand = ""
    best_similarity = 0.0
    for brand in LOOKALIKE_BRANDS:
        similarity = SequenceMatcher(None, folded, brand).ratio()
        if similarity > best_similarity:
            best_similarity = similarity
            best_brand = brand

    if best_brand and 0.75 <= best_similarity < 1.0:
        reason = f"Domain label resembles {best_brand} after character normalization"
        return round(best_similarity, 3), True, reason
    return 0.0, False, ""


def _popularity_score(rank):
    if rank is None or rank < 1:
        return 0.0
    return round(1.0 / rank, 8)


class TrancoLookup:
    def __init__(self, path=None):
        self.ranks = {}
        if path:
            self._load(path)

    def _load(self, path):
        with open(path, newline="", encoding="utf-8-sig") as file:
            rows = csv.reader(file)
            for row in rows:
                if len(row) < 2:
                    continue
                try:
                    rank = int(row[0].strip())
                except ValueError:
                    continue
                domain = _normalise_domain(row[1])
                if domain:
                    self.ranks[domain] = rank

    def lookup(self, domain):
        domain = _normalise_domain(domain)
        rank = self.ranks.get(domain)
        return {
            "domain_in_tranco": rank is not None,
            "tranco_rank": rank,
            "domain_popularity_score": _popularity_score(rank),
        }


def analyze_url(url, tranco=None):
    candidate = url if url.startswith(("http://", "https://")) else "https://" + url
    parsed = urlparse(candidate)
    hostname = (parsed.hostname or "").lower()
    domain, root_domain, subdomain = _domain_parts(hostname)
    path = parsed.path or ""
    query = parsed.query or ""
    keywords = sorted(
        keyword for keyword in SUSPICIOUS_URL_KEYWORDS
        if keyword in candidate.lower()
    )
    lookalike_score, lookalike_match, lookalike_reason = _lookalike(root_domain)
    is_ip = _is_ip(hostname)
    is_punycode = any(label.startswith("xn--") for label in hostname.split("."))
    is_shortener = domain in URL_SHORTENERS
    suspicious_characters = (
        any(character in url for character in ("@", "\\", "<", ">", "\"", "'", "`"))
        or any(character.isspace() for character in url)
    )
    suspicious_domain = bool(
        lookalike_match
        or root_domain.rsplit(".", 1)[-1] in {
            "xyz", "top", "loan", "click", "bid", "club", "tk", "ga", "cf", "ml"
        }
    )
    url_feature = {
        "url": url,
        "scheme": parsed.scheme.lower(),
        "hostname": hostname,
        "domain": domain,
        "registered_domain": root_domain,
        "subdomain": subdomain,
        "url_length": len(url),
        "hostname_length": len(hostname),
        "path_length": len(path),
        "query_length": len(query),
        "dot_count": hostname.count("."),
        "subdomain_count": len(subdomain.split(".")) if subdomain else 0,
        "is_ip_address": is_ip,
        "has_suspicious_characters": suspicious_characters,
        "is_punycode": is_punycode,
        "is_shortener": is_shortener,
        "suspicious_keywords": keywords,
        "suspicious_keyword": bool(keywords),
        "suspicious_url": bool(is_ip or is_punycode or is_shortener or keywords or suspicious_characters),
        "suspicious_domain": suspicious_domain,
        "lookalike_score": lookalike_score,
        "lookalike_match": lookalike_match,
        "lookalike_reason": lookalike_reason,
    }
    url_feature.update((tranco or TrancoLookup()).lookup(root_domain))
    return url_feature


def analyze_urls(urls, tranco=None):
    tranco = tranco or TrancoLookup()
    url_features = [analyze_url(url, tranco) for url in urls]
    domain_features = []
    seen = set()
    for feature in url_features:
        domain = feature["registered_domain"]
        if domain and domain not in seen:
            seen.add(domain)
            domain_feature = {
                "domain": domain,
                "normalized_domain": domain,
                "registered_domain": domain,
                "domain_in_tranco": feature["domain_in_tranco"],
                "tranco_rank": feature["tranco_rank"],
                "domain_popularity_score": feature["domain_popularity_score"],
                "lookalike_score": feature["lookalike_score"],
                "lookalike_match": feature["lookalike_match"],
                "lookalike_reason": feature["lookalike_reason"],
                "suspicious_domain": feature["suspicious_domain"],
            }
            domain_features.append(domain_feature)
    return url_features, domain_features
