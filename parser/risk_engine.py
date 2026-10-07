"""Transparent, rule-based risk scoring for extracted email features."""


CLASSIFICATION_THRESHOLDS = (
    (60, "PHISHING"),
    (30, "SUSPICIOUS"),
    (0, "SAFE"),
)


def _has_url_signal(url_features, key):
    return any(feature.get(key) is True for feature in url_features)


def calculate_risk(features):
    """Return a capped score, classification, and evidence reasons.

    Each URL/domain indicator is counted once across all URLs, so repeated
    links do not multiply the score. Authentication only adds points for an
    explicit ``fail`` status; unknown and other non-pass statuses remain
    visible in the original feature dictionary without being treated as fail.
    """
    auth = features.get("auth") or {}
    url_features = features.get("url_features") or []
    score = 0
    reasons = []

    rules = (
        (auth.get("spf_status") == "fail", 15, "SPF authentication failed"),
        (auth.get("dkim_status") == "fail", 15, "DKIM authentication failed"),
        (auth.get("dmarc_status") == "fail", 20, "DMARC authentication failed"),
        (
            _has_url_signal(url_features, "suspicious_domain"),
            20,
            "Suspicious domain detected",
        ),
        (
            _has_url_signal(url_features, "lookalike_match"),
            20,
            "Look-alike domain detected",
        ),
        (
            _has_url_signal(url_features, "is_ip_address"),
            15,
            "URL uses an IP address instead of a domain",
        ),
        (
            _has_url_signal(url_features, "suspicious_url"),
            15,
            "Suspicious URL characteristics detected",
        ),
        (
            features.get("screens_for_credential_request") is True,
            20,
            "Credential request detected",
        ),
        (
            (features.get("urgency_score") or 0) >= 2,
            10,
            "High urgency language detected",
        ),
        (
            _has_url_signal(url_features, "is_shortener"),
            5,
            "URL shortener detected",
        ),
    )

    for condition, points, reason in rules:
        if condition:
            score += points
            reasons.append(f"{reason} (+{points})")

    score = min(score, 100)
    classification = next(
        label for threshold, label in CLASSIFICATION_THRESHOLDS if score >= threshold
    )
    return {
        "risk_score": score,
        "classification": classification,
        "reasons": reasons,
    }
