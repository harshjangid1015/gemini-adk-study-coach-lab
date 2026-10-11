"""Retrieval-Augmented Generation (RAG) conceptual pipeline simulation."""


def simulate_rag_pipeline(
    query: str,
    knowledge_base: list[dict[str, str]],
) -> dict[str, object]:
    """Demonstrates passage retrieval, prompt augmentation, and grounded response synthesis.

    Args:
        query: User search or question.
        knowledge_base: List of documents with 'id' and 'text'.

    Returns:
        Dictionary with retrieved passages and augmented prompt.
    """
    query_words = set(query.lower().split())

    # Simple lexical keyword matching simulation
    scored_docs: list[tuple[int, dict[str, str]]] = []
    for doc in knowledge_base:
        overlap = len(query_words.intersection(set(doc["text"].lower().split())))
        if overlap > 0:
            scored_docs.append((overlap, doc))

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    top_matches = [d[1] for d in scored_docs[:2]]

    retrieved_text = (
        "\n".join(f"- {d['text']}" for d in top_matches)
        if top_matches
        else "No facts found."
    )

    augmented_prompt = (
        f"Context Information:\n{retrieved_text}\n\n"
        f"User Question: {query}\n\n"
        "Instructions: Answer strictly based on the provided context."
    )

    return {
        "query": query,
        "retrieved_count": len(top_matches),
        "retrieved_sources": [d["id"] for d in top_matches],
        "augmented_prompt": augmented_prompt,
    }


def rag_simulation_demo() -> str:
    """Runs a standard sample RAG simulation and returns formatted output."""
    docs = [
        {
            "id": "doc1",
            "text": "Gemini 2.5 Flash is designed for high-frequency low-latency generative tasks.",
        },
        {
            "id": "doc2",
            "text": "Vertex AI Search provides enterprise-grade grounding with managed vector search.",
        },
    ]
    res = simulate_rag_pipeline("How does Vertex AI Search provide grounding?", docs)
    return (
        f"Retrieved Knowledge Sources: {res['retrieved_sources']}\n"
        f"Augmented Prompt for Grounding in facts:\n{res['augmented_prompt']}"
    )


if __name__ == "__main__":
    print(rag_simulation_demo())
