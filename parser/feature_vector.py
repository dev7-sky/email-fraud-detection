"""Convert extracted email features into a stable numeric model input."""


FEATURE_NAMES = (
    "spf_present",
    "spf_pass",
    "dkim_present",
    "dkim_pass",
    "dmarc_present",
    "dmarc_pass",
    "url_count",
    "suspicious_url",
    "suspicious_domain",
    "ip_based_url",
    "lookalike_score",
    "lookalike_match",
    "shortened_url",
    "max_url_length",
    "max_domain_length",
    "max_subdomain_count",
    "credential_request",
    "urgency_score",
    "has_attachment",
    "attachments_count",
    "email_text_length",
)


def _numeric_bool(value):
    return 1.0 if value is True else 0.0


def _max_url_value(url_features, key):
    return max((feature.get(key, 0) or 0 for feature in url_features), default=0)


def _any_url_value(url_features, key):
    return any(feature.get(key, False) is True for feature in url_features)


def features_to_vector(features):
    """Return ``(FEATURE_NAMES, numeric_values)`` for one feature dictionary.

    Missing or unknown values use conservative numeric defaults. Authentication
    ``None`` values are represented as 0 because this vector has no separate
    unknown category; the original structured features remain available.
    """
    auth = features.get("auth") or {}
    url_features = features.get("url_features") or []
    values = {
        "spf_present": _numeric_bool(auth.get("spf_present", False)),
        "spf_pass": _numeric_bool(auth.get("spf_pass", False)),
        "dkim_present": _numeric_bool(auth.get("dkim_present", False)),
        "dkim_pass": _numeric_bool(auth.get("dkim_pass", False)),
        "dmarc_present": _numeric_bool(auth.get("dmarc_present", False)),
        "dmarc_pass": _numeric_bool(auth.get("dmarc_pass", False)),
        "url_count": features.get("url_count", 0) or 0,
        "suspicious_url": _numeric_bool(_any_url_value(url_features, "suspicious_url")),
        "suspicious_domain": _numeric_bool(_any_url_value(url_features, "suspicious_domain")),
        "ip_based_url": _numeric_bool(_any_url_value(url_features, "is_ip_address")),
        "lookalike_score": max(
            (feature.get("lookalike_score", 0) or 0 for feature in url_features),
            default=0.0,
        ),
        "lookalike_match": _numeric_bool(_any_url_value(url_features, "lookalike_match")),
        "shortened_url": _numeric_bool(_any_url_value(url_features, "is_shortener")),
        "max_url_length": _max_url_value(url_features, "url_length"),
        "max_domain_length": _max_url_value(url_features, "hostname_length"),
        "max_subdomain_count": _max_url_value(url_features, "subdomain_count"),
        "credential_request": _numeric_bool(
            features.get("screens_for_credential_request", False)
        ),
        "urgency_score": features.get("urgency_score", 0) or 0,
        "has_attachment": _numeric_bool(features.get("has_attachment", False)),
        "attachments_count": features.get("attachments_count", 0) or 0,
        "email_text_length": features.get("email_text_length", 0) or 0,
    }
    return FEATURE_NAMES, [float(values[name]) for name in FEATURE_NAMES]
