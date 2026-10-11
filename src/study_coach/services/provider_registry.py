"""Provider registry and URL classification services for learning resources."""

from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml
from pydantic import BaseModel, Field

PROVIDERS_REGISTRY_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "resource_providers.yaml"
)


class ProviderInfo(BaseModel):
    """Metadata describing a recognized learning resource publisher or platform."""

    provider_id: str = Field(..., description="Unique slug for the provider")
    display_name: str = Field(..., description="Human-readable brand name")
    accepted_domains: list[str] = Field(
        ..., description="List of accepted domain or wildcard patterns"
    )
    icon_asset: str = Field(..., description="Filename of the icon SVG asset")
    icon_alt: str = Field(..., description="Accessible description for the icon")
    icon_license_or_source: str = Field(
        ..., description="Attribution / license notice for the icon asset"
    )
    fallback_icon: str = Field(
        default="external-resource.svg",
        description="Fallback icon filename if primary asset fails",
    )


# Default fallback provider for arbitrary third-party domains
FALLBACK_PROVIDER = ProviderInfo(
    provider_id="external_resource",
    display_name="External Resource",
    accepted_domains=[],
    icon_asset="external-resource.svg",
    icon_alt="External resource icon",
    icon_license_or_source="Lucide Icons (ISC License)",
    fallback_icon="external-resource.svg",
)


@lru_cache(maxsize=1)
def load_provider_registry() -> list[ProviderInfo]:
    """Loads and validates all provider entries from the YAML registry."""
    if not PROVIDERS_REGISTRY_PATH.is_file():
        return [FALLBACK_PROVIDER]

    with open(PROVIDERS_REGISTRY_PATH, "r", encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}

    raw_list: list[dict[str, Any]] = data.get("providers", [])
    return [ProviderInfo.model_validate(p) for p in raw_list]


def extract_url_hostname(url: str) -> str | None:
    """Extracts, validates, and normalizes the lowercase hostname from a URL.

    Rejects empty, malformed, or unsupported URL schemes (must be http or https).
    """
    if not url or not isinstance(url, str):
        return None

    cleaned_url = url.strip()
    try:
        parsed = urlparse(cleaned_url)
        if parsed.scheme.lower() not in ("http", "https"):
            return None
        hostname = (parsed.hostname or "").lower().strip()
        return hostname if hostname else None
    except (ValueError, AttributeError):
        return None


def match_domain_pattern(hostname: str, pattern: str) -> bool:
    """Matches a normalized hostname against an exact domain or wildcard pattern.

    Examples:
    - Exact: 'cloud.google.com' == 'cloud.google.com'
    - Wildcard subdomain: '*.google.com' matches 'ai.google.com' and 'cloud.google.com',
      but NOT 'phishing-google.com' or 'google.com'
    - Wildcard TLD/entity: '*.google' matches 'ai.google' and 'deepmind.google'
    """
    p = pattern.lower().strip()
    if p.startswith("*."):
        suffix = p[1:]  # e.g. '.google.com'
        return hostname.endswith(suffix) and len(hostname) > len(suffix)
    return hostname == p


def resolve_provider_for_url(url: str) -> ProviderInfo:
    """Deterministically identifies the learning provider for a given URL using exact/subdomain matching.

    Ensures that spoofed/lookalike hostnames (e.g. googlecloud.phishing.com) never match.
    """
    hostname = extract_url_hostname(url)
    if not hostname:
        return FALLBACK_PROVIDER

    providers = load_provider_registry()
    for provider in providers:
        for domain_pattern in provider.accepted_domains:
            if match_domain_pattern(hostname, domain_pattern):
                return provider

    return FALLBACK_PROVIDER
