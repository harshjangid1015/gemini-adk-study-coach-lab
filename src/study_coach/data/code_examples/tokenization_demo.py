"""Word and subword tokenization demonstration."""


def tokenize_text_demo(text: str) -> dict[str, object]:
    """Demonstrates basic whitespace/punctuation tokenization and vocabulary lookup simulation.

    Args:
        text: Input string to tokenize.

    Returns:
        Dictionary containing tokens, token count, and simulated integer token IDs.
    """
    import re

    # Match alphanumeric words and individual punctuation marks
    tokens = re.findall(r"\w+|[^\w\s]", text)

    # Deterministic token ID mapping for illustration
    simulated_ids = [abs(hash(t)) % 10000 + 100 for t in tokens]

    return {
        "original_text": text,
        "tokens": tokens,
        "token_count": len(tokens),
        "token_ids": simulated_ids,
    }


def tokenization_demo(text: str) -> list[str]:
    """Returns list of token strings from input text."""
    import re

    return [t.lower() for t in re.findall(r"\w+|[^\w\s]", text)]


if __name__ == "__main__":
    sample = "Hello Vertex AI! Transformers predict the next word."
    result = tokenize_text_demo(sample)
    print("Tokens:", result["tokens"])
    print("Token IDs:", result["token_ids"])
