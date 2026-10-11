"""Reusable thumbnail-based learning resource cards and grid components for Streamlit."""

import html
import re
from urllib.parse import parse_qs, urlparse

import streamlit as st

from study_coach.models.learning_resource import LearningResource

# YouTube ID pattern: exactly 11 characters of [a-zA-Z0-9_-]
YOUTUBE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{11}$")


def extract_youtube_video_id(url: str) -> str | None:
    """Parses supported YouTube URLs and extracts an 11-character video ID.

    Supported patterns:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID&t=10s
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    """
    if not url:
        return None

    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()

        # Handle youtu.be shortlinks: hostname is youtu.be, path is /<video_id>
        if hostname == "youtu.be" or hostname.endswith(".youtu.be"):
            video_id = parsed.path.lstrip("/").split("/")[0]
            if YOUTUBE_ID_PATTERN.match(video_id):
                return video_id
            return None

        # Handle standard youtube.com domains
        if "youtube.com" in hostname:
            # 1. Query parameter ?v=
            query_params = parse_qs(parsed.query)
            if query_params.get("v"):
                video_id = query_params["v"][0]
                if YOUTUBE_ID_PATTERN.match(video_id):
                    return video_id

            # 2. Path formats /embed/VIDEO_ID or /v/VIDEO_ID
            path_parts = [p for p in parsed.path.split("/") if p]
            if len(path_parts) >= 2 and path_parts[0] in ("embed", "v"):
                video_id = path_parts[1]
                if YOUTUBE_ID_PATTERN.match(video_id):
                    return video_id

        return None
    except (ValueError, AttributeError, IndexError):
        return None


def get_youtube_thumbnail_url(url: str) -> str | None:
    """Returns the official YouTube HQ thumbnail URL for a valid YouTube video."""
    video_id = extract_youtube_video_id(url)
    if video_id:
        return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    return None


def generate_fallback_svg_thumbnail(res: LearningResource) -> str:
    """Generates a sleek, 16:9 branded SVG data URI placeholder when no remote thumbnail is available."""
    # Palette styling based on official or community status
    bg_gradient_start = "#1a237e" if res.is_official else "#1e293b"
    bg_gradient_end = "#0d47a1" if res.is_official else "#0f172a"
    badge_bg = "#4285F4" if res.is_official else "#38bdf8"
    badge_label = "OFFICIAL GOOGLE" if res.is_official else "COMMUNITY GUIDE"

    safe_title = html.escape(res.title[:55] + ("..." if len(res.title) > 55 else ""))
    safe_provider = html.escape(res.provider)
    safe_type = html.escape(res.resource_type.upper())

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
      <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="{bg_gradient_start}"/>
          <stop offset="100%" stop-color="{bg_gradient_end}"/>
        </linearGradient>
      </defs>
      <rect width="640" height="360" rx="12" fill="url(#grad)"/>
      <rect x="30" y="30" width="160" height="28" rx="6" fill="{badge_bg}" opacity="0.9"/>
      <text x="40" y="49" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="bold" fill="#ffffff">{badge_label}</text>
      <rect x="200" y="30" width="140" height="28" rx="6" fill="#334155" opacity="0.9"/>
      <text x="210" y="49" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">{safe_type}</text>
      <text x="30" y="180" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="24" font-weight="bold" fill="#f8fafc">{safe_title}</text>
      <text x="30" y="225" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="16" font-weight="normal" fill="#94a3b8">Provider: {safe_provider}</text>
      <text x="30" y="315" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="500" fill="#38bdf8">⏱️ ~{res.estimated_minutes} min | Level: {res.experience_level.title()}</text>
    </svg>"""
    return f"data:image/svg+xml;utf8,{svg}"


def get_resource_thumbnail_url(res: LearningResource) -> str:
    """Resolves the 16:9 thumbnail for a resource.

    Order of precedence:
    1. YouTube HQ thumbnail if URL is a verified YouTube video.
    2. Explicit verified thumbnail_url from resource metadata if available.
    3. Self-contained 16:9 branded SVG placeholder.
    """
    url_str = str(res.url)
    yt_thumb = get_youtube_thumbnail_url(url_str)
    if yt_thumb:
        return yt_thumb

    if res.thumbnail_url:
        return str(res.thumbnail_url)

    return generate_fallback_svg_thumbnail(res)


def render_resource_card(
    res: LearningResource,
    enable_video_embed: bool = True,
) -> None:
    """Renders a polished, responsive 16:9 thumbnail-based resource card."""
    with st.container(border=True):
        # 1. 16:9 Thumbnail Image
        thumbnail_url = get_resource_thumbnail_url(res)
        st.image(thumbnail_url, use_container_width=True)

        # 2. Status & Classification Badges
        col_badge1, col_badge2 = st.columns([2, 1])
        with col_badge1:
            badge_icon = "⭐" if res.is_official else "🌐"
            badge_text = "Official Google" if res.is_official else "Community"
            st.caption(f"{badge_icon} **{badge_text}** • `{res.resource_type}`")
        with col_badge2:
            if res.requires_paid_access:
                st.badge("Paid / Account", icon="💳")
            elif res.requires_login:
                st.badge("Free (Login)", icon="🔑")
            else:
                st.badge("100% Free", icon="🟢")

        # 3. Title & Provider Metadata
        st.markdown(f"##### {res.title}")
        st.caption(
            f"🏢 **{res.provider}** | ⏱️ ~{res.estimated_minutes} min | Level: **{res.experience_level.title()}**"
        )

        # 4. Short Description
        st.write(res.short_description)

        # 5. Primary Action: Open Resource Link
        st.link_button(
            f"🔗 Open {res.resource_type.title()}",
            str(res.url),
            use_container_width=True,
        )

        # 6. Optional Embedded Video Player
        yt_id = extract_youtube_video_id(str(res.url))
        if yt_id and enable_video_embed:
            with st.expander("▶️ Watch Embedded Video", expanded=False):
                st.video(str(res.url))


def render_resource_grid(
    resources: list[LearningResource],
    columns: int = 2,
    enable_video_embed: bool = True,
) -> None:
    """Renders a collection of resources in a balanced multi-column grid."""
    if not resources:
        st.info("No resources available for this selection.")
        return

    cols = st.columns(columns)
    for idx, res in enumerate(resources):
        with cols[idx % columns]:
            render_resource_card(res, enable_video_embed=enable_video_embed)
