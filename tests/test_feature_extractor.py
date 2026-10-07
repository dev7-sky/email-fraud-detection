from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from pathlib import Path

from parser.feature_extractor import extract_email_features
from parser.feature_vector import FEATURE_NAMES, features_to_vector
from parser.url_domain_analysis import TrancoLookup, analyze_url


SAMPLE_ROOT = Path(__file__).parents[1] / "samples"


def load_sample(relative_path):
    path = SAMPLE_ROOT / relative_path
    message = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
    body = message.get_body(preferencelist=("plain", "html"))
    body_text = body.get_content() if body else ""
    return message, extract_email_features(message, body_text)


def make_message():
    message = EmailMessage()
    message["Subject"] = "Urgent: verify your account today"
    message["From"] = "Example <sender@example.com>"
    message["Received-SPF"] = "pass"
    message["DKIM-Signature"] = "v=1; d=example.com"
    message["Authentication-Results"] = "mx.example; spf=pass; dkim=pass; dmarc=pass"
    return message


def test_extracts_urls_domains_and_content_signals():
    message = make_message()
    features = extract_email_features(
        message,
        "Urgent action required. Click here to verify your account: "
        "https://example.com/login",
    )

    assert features["has_link"] is True
    assert features["url_count"] == 1
    assert features["domains"] == ["example.com"]
    assert features["screens_for_credential_request"] is True
    assert "verify your account" in features["credential_keywords_found"]
    assert features["urgency_score"] >= 2
    assert features["url_features"][0]["scheme"] == "https"


def test_url_analysis_handles_ip_punycode_shortener_and_lookalike():
    cases = {
        "http://192.0.2.1/login": ("is_ip_address", True),
        "https://xn--pple-43d.com/verify": ("is_punycode", True),
        "https://bit.ly/abc": ("is_shortener", True),
        "https://paypa1.com/login": ("lookalike_match", True),
    }
    for url, (field, expected) in cases.items():
        assert analyze_url(url)[field] == expected


def test_tranco_lookup_does_not_make_unknown_domains_malicious(tmp_path: Path):
    tranco_path = tmp_path / "tranco.csv"
    tranco_path.write_text("1,linkedin.com\n2,example.com\n", encoding="utf-8")
    lookup = TrancoLookup(str(tranco_path))

    known = analyze_url("https://linkedin.com/help", lookup)
    unknown = analyze_url("https://unknown-example.invalid/login", lookup)

    assert known["domain_in_tranco"] is True
    assert known["tranco_rank"] == 1
    assert known["domain_popularity_score"] > 0
    assert unknown["domain_in_tranco"] is False
    assert unknown["tranco_rank"] is None
    assert unknown["domain_popularity_score"] == 0.0
    assert unknown["suspicious_domain"] is False

    message = EmailMessage()
    integrated = extract_email_features(
        message, "https://linkedin.com/help", tranco=lookup
    )
    assert integrated["domain_features"][0]["tranco_rank"] == 1


def test_multiple_urls_produce_multiple_url_features():
    message = EmailMessage()
    features = extract_email_features(
        message,
        "https://example.com/a https://bit.ly/x https://192.0.2.1/login",
    )
    assert features["url_count"] == 3
    assert len(features["url_features"]) == 3
    assert len(features["domain_features"]) == 3


def test_authentication_metadata_is_recorded_separately_from_results():
    features = extract_email_features(make_message(), "Plain text")

    assert features["auth"]["spf_present"] is True
    assert features["auth"]["spf_status"] == "pass"
    assert features["auth"]["spf_pass"] is True
    assert features["auth"]["dkim_present"] is True
    assert features["auth"]["dkim_status"] == "pass"
    assert features["auth"]["dkim_pass"] is True
    assert features["auth"]["dmarc_present"] is True
    assert features["auth"]["dmarc_status"] == "pass"
    assert features["auth"]["dmarc_pass"] is True
    assert "spf=pass" in features["auth"]["auth_results"]


def test_authentication_statuses_preserve_known_non_pass_results():
    statuses = ("fail", "softfail", "neutral", "none", "temperror", "permerror")

    for status in statuses:
        message = EmailMessage()
        message["Authentication-Results"] = (
            f"mx.example; spf={status}; dkim={status}; dmarc={status}"
        )
        auth = extract_email_features(message)["auth"]

        assert auth["spf_status"] == status
        assert auth["dkim_status"] == status
        assert auth["dmarc_status"] == status
        assert auth["spf_pass"] is False
        assert auth["dkim_pass"] is False
        assert auth["dmarc_pass"] is False


def test_authentication_unknown_is_not_reported_as_failure():
    message = EmailMessage()
    message["DKIM-Signature"] = "v=1; d=example.com"
    auth = extract_email_features(message)["auth"]

    assert auth["dkim_present"] is True
    assert auth["dkim_status"] == "unknown"
    assert auth["dkim_pass"] is None
    assert auth["spf_status"] == "unknown"
    assert auth["spf_pass"] is None


def test_empty_message_has_safe_defaults():
    message = EmailMessage()
    features = extract_email_features(message)

    assert features["has_link"] is False
    assert features["url_count"] == 0
    assert features["domains"] == []
    assert features["attachments_count"] == 0
    assert features["auth"]["spf_status"] == "unknown"
    assert features["auth"]["dkim_status"] == "unknown"
    assert features["auth"]["dmarc_status"] == "unknown"


def test_synthetic_legitimate_sample_has_normal_features():
    message, features = load_sample("legitimate/legitimate_linkedin.eml")

    assert message["Message-ID"] == "<legitimate-demo@example.com>"
    assert features["url_count"] == 1
    assert features["url_features"][0]["domain"] == "example.com"
    assert features["url_features"][0]["suspicious_url"] is False
    assert features["auth"]["spf_status"] == "pass"
    assert features["auth"]["dkim_status"] == "pass"
    assert features["auth"]["dmarc_status"] == "pass"
    assert features["screens_for_credential_request"] is False


def test_synthetic_suspicious_sample_preserves_mixed_auth_and_url_signals():
    _, features = load_sample("suspicious/suspicious_account.eml")

    assert features["urgency_score"] >= 2
    assert features["url_count"] == 1
    assert features["url_features"][0]["is_ip_address"] is True
    assert features["url_features"][0]["suspicious_url"] is True
    assert features["auth"]["spf_status"] == "neutral"
    assert features["auth"]["spf_pass"] is False
    assert features["auth"]["dkim_status"] == "none"
    assert features["auth"]["dmarc_status"] == "unknown"


def test_synthetic_phishing_sample_has_credential_and_failed_auth_signals():
    _, features = load_sample("phishing/phishing_credential.eml")

    assert features["screens_for_credential_request"] is True
    assert features["url_count"] == 1
    assert features["url_features"][0]["lookalike_match"] is True
    assert features["url_features"][0]["suspicious_domain"] is True
    assert features["auth"]["spf_status"] == "fail"
    assert features["auth"]["dkim_status"] == "fail"
    assert features["auth"]["dmarc_status"] == "fail"
    assert "spf=fail" in features["auth"]["auth_results"]


def test_feature_vector_has_stable_numeric_schema_for_extracted_features():
    _, features = load_sample("phishing/phishing_credential.eml")

    names, vector = features_to_vector(features)

    assert names == FEATURE_NAMES
    assert len(names) == len(vector) == 21
    assert all(isinstance(value, float) for value in vector)
    assert vector[names.index("spf_present")] == 1.0
    assert vector[names.index("spf_pass")] == 0.0
    assert vector[names.index("url_count")] == 1.0
    assert vector[names.index("credential_request")] == 1.0
    assert vector[names.index("lookalike_match")] == 1.0


def test_feature_vector_uses_safe_defaults_for_missing_values():
    names, vector = features_to_vector({})

    assert len(names) == len(vector) == 21
    assert vector == [0.0] * 21
