"""Compact learning resource cards with real provider brand logos for Streamlit."""

import html
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st

from study_coach.models.learning_resource import LearningResource

# Assets directory for provider brand SVG logos
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "provider_icons"

# In-memory cache for SVG markup to avoid repeated disk reads
_SVG_CACHE: dict[str, str] = {}


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


def get_provider_icon_name(url: str) -> str:
    """Maps a validated URL hostname to a trusted provider logo asset name.

    Strict hostname-based rules:
    - cloud.google.com -> google-cloud
    - developers.google.com -> google-developers
    - google.com & verified *.google.com / *.google subdomains -> google
    - youtube.com, www.youtube.com, m.youtube.com, youtu.be, *.youtube.com -> youtube
    - github.com, *.github.com -> github
    - huggingface.co, *.huggingface.co -> huggingface
    - linkedin.com, *.linkedin.com -> linkedin
    - Any other domain or invalid scheme -> external-resource (neutral fallback)
    """
    hostname = extract_url_hostname(url)
    if not hostname:
        return "external-resource"

    # 1. Google Cloud exact / subdomains
    if hostname == "cloud.google.com" or hostname.endswith(".cloud.google.com"):
        return "google-cloud"

    # 2. Google Developers exact
    if hostname == "developers.google.com":
        return "google-developers"

    # 3. YouTube domains
    if hostname in ("youtube.com", "youtu.be") or hostname.endswith(
        (".youtube.com", ".youtu.be")
    ):
        return "youtube"

    # 4. GitHub domains
    if hostname == "github.com" or hostname.endswith(".github.com"):
        return "github"

    # 5. Hugging Face domains
    if hostname == "huggingface.co" or hostname.endswith(".huggingface.co"):
        return "huggingface"

    # 6. LinkedIn domains
    if hostname == "linkedin.com" or hostname.endswith(".linkedin.com"):
        return "linkedin"

    # 7. Other verified Google subdomains (e.g. ai.google, deepmind.google, www.google.com)
    if hostname == "google.com" or hostname.endswith((".google.com", ".google")):
        return "google"

    # Neutral fallback for arbitrary / external domains
    return "external-resource"


def get_provider_logo_svg(icon_name: str) -> str:
    """Loads and caches authentic SVG icon markup for the given icon name."""
    if icon_name in _SVG_CACHE:
        return _SVG_CACHE[icon_name]

    icon_path = ASSETS_DIR / f"{icon_name}.svg"
    if not icon_path.is_file():
        # Fall back to neutral external resource icon
        icon_path = ASSETS_DIR / "external-resource.svg"

    try:
        svg_content = icon_path.read_text(encoding="utf-8").strip()
        _SVG_CACHE[icon_name] = svg_content
        return svg_content
    except (OSError, UnicodeDecodeError):
        # Ultimate inline fallback if filesystem fails
        fallback_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" '
            'fill="none" stroke="#60A5FA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>'
            '<path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>'
            "</svg>"
        )
        return fallback_svg


def render_resource_card(res: LearningResource) -> None:
    """Renders a clean, compact learning resource card with genuine provider logo.

    Card contains ONLY:
    - Genuine provider brand logo (approx 28px)
    - Resource title immediately beside the logo
    - Provider, resource type, and official/community classification
    - Free / access label badge
    - Concise short description (maximum two lines)
    - Clickable resource link button
    """
    with st.container(border=True):
        url_str = str(res.url)
        icon_name = get_provider_icon_name(url_str)
        svg_markup = get_provider_logo_svg(icon_name)

        # 1. Header line: Authentic Provider Logo (~28px) + Resource Title
        st.markdown(
            f'<div style="display: flex; align-items: flex-start; gap: 10px; margin-bottom: 6px;">'
            f'<div style="flex-shrink: 0; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;" '
            f'aria-label="{html.escape(res.provider)} logo" title="{html.escape(res.provider)}">'
            f"{svg_markup}"
            f"</div>"
            f'<div style="flex-grow: 1; font-size: 16px; font-weight: 600; line-height: 1.3;">'
            f"{html.escape(res.title)}"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # 2. Status & Classification Badges / Metadata
        col_meta, col_badge = st.columns([3, 2])
        with col_meta:
            official_label = "⭐ Official Google" if res.is_official else "🌐 Community"
            st.caption(f"{official_label} • **{res.provider}** • `{res.resource_type}`")
        with col_badge:
            if res.requires_paid_access:
                st.badge("Paid / Account", icon="💳")
            elif res.requires_login:
                st.badge("Free (Login)", icon="🔑")
            else:
                st.badge("100% Free", icon="🟢")

        # 3. Short description (capped, concise, max 2 lines)
        desc = res.short_description or ""
        st.caption(
            f"⏱️ ~{res.estimated_minutes} min | Level: {res.experience_level.title()}"
        )
        st.write(desc)

        # 4. Clickable Resource Link
        st.link_button(
            f"🔗 Open {res.resource_type.title()}",
            url_str,
            use_container_width=True,
        )


def render_resource_grid(
    resources: list[LearningResource],
    columns: int = 2,
) -> None:
    """Renders a collection of resources in a balanced multi-column compact grid."""
    if not resources:
        st.info("No resources available for this selection.")
        return

    cols = st.columns(columns)
    for idx, res in enumerate(resources):
        with cols[idx % columns]:
            render_resource_card(res)
