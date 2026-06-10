"""Domain profiles for tailoring safety engineering workflows."""

from __future__ import annotations

from typing import Any


DOMAIN_PROFILES: dict[str, dict[str, Any]] = {
    "automotive": {
        "id": "automotive",
        "name": "Automotive safety",
        "domain": "Autonomous driving",
        "system_type": "ADAS / automated driving function",
        "standards": ["ISO 26262", "ISO 21448", "ISO 8800", "NCAP", "IIHS"],
        "default_standards": ["ISO 26262", "ISO 21448", "ISO 8800"],
        "review_lens": "Functional safety, SOTIF, AI assurance, ODD coverage, scenario validation, and perception monitoring.",
        "requirement_prefix": "AUTO",
    },
    "railway": {
        "id": "railway",
        "name": "Railway safety",
        "domain": "Railway safety engineering",
        "system_type": "ERTMS / railway control system",
        "standards": ["IEC 62278 / EN 50126", "EN 50128", "EN 50129", "IEC 62425", "ERTMS"],
        "default_standards": ["IEC 62278 / EN 50126", "EN 50128", "EN 50129"],
        "review_lens": "RAMS lifecycle, software safety integrity, safety case evidence, hazard log traceability, and validation evidence.",
        "requirement_prefix": "RAIL",
    },
    "generic": {
        "id": "generic",
        "name": "Generic safety engineering",
        "domain": "Safety engineering",
        "system_type": "Safety-critical system",
        "standards": ["System safety plan", "Hazard analysis", "Verification plan", "Safety case"],
        "default_standards": ["System safety plan", "Hazard analysis", "Verification plan"],
        "review_lens": "Hazard traceability, measurable requirements, verification evidence, approval workflow, and residual risk.",
        "requirement_prefix": "SAFE",
    },
}


def list_domain_profiles() -> list[dict[str, Any]]:
    return list(DOMAIN_PROFILES.values())


def infer_domain_profile(domain: str | None, standards: list[str] | None = None) -> dict[str, Any]:
    text = f"{domain or ''} {' '.join(standards or [])}".lower()
    if any(term in text for term in ["rail", "ertms", "62278", "50126", "50128", "50129", "62425"]):
        return DOMAIN_PROFILES["railway"]
    if any(term in text for term in ["auto", "adas", "aeb", "26262", "21448", "8800", "sotif", "ncap", "iihs"]):
        return DOMAIN_PROFILES["automotive"]
    return DOMAIN_PROFILES["generic"]
