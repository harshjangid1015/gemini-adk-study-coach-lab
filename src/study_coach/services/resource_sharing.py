"""URL generation utilities for sharing individual learning resources."""

from urllib.parse import quote_plus


def generate_share_text(resource_title: str, provider: str) -> str:
    """Generates concise, privacy-safe text describing the resource without user or session data."""
    clean_title = resource_title.strip()
    clean_provider = provider.strip()
    return f"Studying '{clean_title}' by {clean_provider} for Google Cloud Generative AI certification!"


def get_linkedin_share_url(resource_url: str) -> str:
    """Generates a standard, correctly encoded LinkedIn sharing URL."""
    encoded_url = quote_plus(str(resource_url).strip())
    return f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}"


def get_x_twitter_share_url(resource_url: str, text: str | None = None) -> str:
    """Generates a standard X/Twitter web intent sharing URL."""
    encoded_url = quote_plus(str(resource_url).strip())
    encoded_text = quote_plus(
        (text or "Recommended Generative AI learning resource:").strip()
    )
    return f"https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_text}"


def get_facebook_share_url(resource_url: str) -> str:
    """Generates a standard Facebook sharer URL."""
    encoded_url = quote_plus(str(resource_url).strip())
    return f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}"


def get_email_share_url(resource_url: str, resource_title: str, provider: str) -> str:
    """Generates a standard mailto: link for sharing via email."""
    subject = quote_plus(f"Learning Resource: {resource_title}")
    body = quote_plus(
        f"Hi,\n\nI recommend checking out this resource for Google Cloud Generative AI study:\n\n"
        f"{resource_title} (by {provider})\n{resource_url}\n"
    )
    return f"mailto:?subject={subject}&body={body}"
