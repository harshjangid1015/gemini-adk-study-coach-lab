"""Compact learning resource cards with real provider brand logos and sharing for Streamlit."""

import html
from pathlib import Path

import streamlit as st

from study_coach.models.learning_resource import LearningResource
from study_coach.services.provider_registry import (
    ProviderInfo,
    extract_url_hostname,
    resolve_provider_for_url,
)
from study_coach.services.resource_sharing import (
    generate_share_text,
    get_email_share_url,
    get_facebook_share_url,
    get_linkedin_share_url,
    get_x_twitter_share_url,
)

# Assets directory for provider brand SVG logos
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "provider_icons"

# In-memory cache for SVG markup to avoid repeated disk reads
_SVG_CACHE: dict[str, str] = {}

__all__ = [
    "ASSETS_DIR",
    "extract_url_hostname",
    "get_provider_icon_name",
    "get_provider_logo_svg",
    "render_resource_card",
    "render_resource_grid",
]


def get_provider_icon_name(url: str) -> str:
    """Returns the base SVG icon asset filename for a given URL via the provider registry."""
    provider_info = resolve_provider_for_url(url)
    return provider_info.icon_asset.replace(".svg", "")


def get_provider_logo_svg(icon_asset_filename: str) -> str:
    """Loads and caches authentic SVG icon markup for the given icon asset filename."""
    if icon_asset_filename in _SVG_CACHE:
        return _SVG_CACHE[icon_asset_filename]

    if not icon_asset_filename.endswith(".svg"):
        icon_asset_filename = f"{icon_asset_filename}.svg"

    icon_path = ASSETS_DIR / icon_asset_filename
    if not icon_path.is_file():
        icon_path = ASSETS_DIR / "external-resource.svg"

    try:
        svg_content = icon_path.read_text(encoding="utf-8").strip()
        _SVG_CACHE[icon_asset_filename] = svg_content
        return svg_content
    except (OSError, UnicodeDecodeError):
        fallback_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" '
            'fill="none" stroke="#60A5FA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>'
            '<path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>'
            "</svg>"
        )
        return fallback_svg


def render_resource_card(res: LearningResource) -> None:
    """Renders a clean, compact learning resource card with authentic provider logo and sharing controls.

    Card contains ONLY:
    - Genuine provider brand logo (approx 28px)
    - Resource title immediately beside the logo
    - Provider, resource type, and official/community classification
    - Free / access label badge
    - Concise short description (maximum two lines)
    - Compact action controls: [Open ↗], [Copy Link], and [Share ▾] popover
    """
    with st.container(border=True):
        url_str = str(res.url)
        provider_info: ProviderInfo = resolve_provider_for_url(url_str)
        svg_markup = get_provider_logo_svg(provider_info.icon_asset)

        # 1. Header line: Authentic Provider Logo (~28px) + Resource Title
        st.markdown(
            f'<div style="display: flex; align-items: flex-start; gap: 10px; margin-bottom: 6px;">'
            f'<div style="flex-shrink: 0; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;" '
            f'aria-label="{html.escape(provider_info.icon_alt)}" title="{html.escape(provider_info.display_name)}">'
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

        # 4. Compact Action Controls: [Open ↗], [Copy Link], [Share ▾]
        col_act1, col_act2, col_act3 = st.columns([3, 2, 2])

        with col_act1:
            st.link_button(
                f"🔗 Open {res.resource_type.title()}",
                url_str,
                use_container_width=True,
            )

        with col_act2, st.popover("📋 Copy", use_container_width=True):
            st.caption("Direct Resource URL:")
            st.code(url_str, language="text")

        with col_act3, st.popover("📤 Share ▾", use_container_width=True):
            st.caption("Share Resource:")
            share_text = generate_share_text(res.title, res.provider)

            st.link_button(
                "💼 Share to LinkedIn",
                get_linkedin_share_url(url_str),
                use_container_width=True,
            )
            st.link_button(
                "🐦 Share to X / Twitter",
                get_x_twitter_share_url(url_str, share_text),
                use_container_width=True,
            )
            st.link_button(
                "📘 Share to Facebook",
                get_facebook_share_url(url_str),
                use_container_width=True,
            )
            st.link_button(
                "✉️ Email Resource",
                get_email_share_url(url_str, res.title, res.provider),
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
