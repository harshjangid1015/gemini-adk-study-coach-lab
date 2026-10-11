"""Compact learning resource cards and grid components for Streamlit."""

import html

import streamlit as st

from study_coach.models.learning_resource import LearningResource

# Mapping provider and domain keywords to compact icons (approx. 28px visual scale)
PROVIDER_ICONS = {
    "google": "☁️",
    "google cloud": "☁️",
    "google cloud platform": "☁️",
    "google developers": "🌐",
    "youtube": "📺",
    "github": "🐙",
    "hugging face": "🤗",
    "3blue1brown": "📺",
}


def get_provider_icon(provider: str, url: str = "") -> str:
    """Returns a recognizable provider emoji icon with a neutral book fallback.

    - Google Cloud / Google -> ☁️ Cloud icon
    - YouTube -> 📺 YouTube/Video icon
    - GitHub -> 🐙 GitHub Octocat/Repo icon
    - Hugging Face -> 🤗 Hugging Face icon
    - Other -> 📖 Neutral book/reading icon
    """
    prov_lower = (provider or "").lower().strip()
    url_lower = (url or "").lower().strip()

    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "📺"
    if "github.com" in url_lower or "github" in prov_lower:
        return "🐙"
    if "huggingface" in url_lower or "hugging face" in prov_lower:
        return "🤗"
    if "google" in prov_lower or "cloud.google" in url_lower:
        return "☁️"

    for key, icon in PROVIDER_ICONS.items():
        if key in prov_lower:
            return icon

    return "📖"


def render_resource_card(res: LearningResource) -> None:
    """Renders a clean, compact learning resource card without any large thumbnails.

    Contains ONLY:
    - Provider icon (~28px font scale) + Title
    - Provider and resource type metadata
    - Official/community classification badge
    - Free/access status badge
    - Short description (maximum two lines)
    - Clickable resource link button
    """
    with st.container(border=True):
        icon = get_provider_icon(res.provider, str(res.url))

        # 1. Header line: Provider Icon (~28px) + Title
        # Title is directly visible at the very top of the card
        st.markdown(
            f'<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">'
            f'<span style="font-size: 26px; line-height: 1;" title="{html.escape(res.provider)}">{icon}</span>'
            f'<span style="font-size: 16px; font-weight: 600; line-height: 1.3;">{html.escape(res.title)}</span>'
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
            str(res.url),
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
