"""Self-attention vector dot-product simulation."""

import math


def simple_attention_demo(
    query: list[float],
    keys: list[list[float]],
) -> list[float]:
    """Computes basic dot-product attention weights over key vectors.

    Args:
        query: Query vector representing target token.
        keys: List of key vectors for each token in context.

    Returns:
        Softmax attention weights representing relevance distribution.
    """
    dim = len(query)
    scores: list[float] = []

    # Scaled dot-product: (Q * K) / sqrt(d)
    for k in keys:
        dot = sum(q_i * k_i for q_i, k_i in zip(query, k))
        scaled_score = dot / math.sqrt(dim)
        scores.append(scaled_score)

    # Softmax exponentiation
    max_score = max(scores)
    exp_scores = [math.exp(s - max_score) for s in scores]
    sum_exp = sum(exp_scores)

    return [round(e / sum_exp, 3) for e in exp_scores]


def attention_demo() -> list[list[float]]:
    """Runs a 3-token self-attention demo and returns the attention weight matrix."""
    tokens = {
        "bank": [0.8, 0.1, 0.5],
        "river": [0.1, 0.9, 0.2],
        "money": [0.9, 0.1, 0.6],
    }
    keys = [tokens["bank"], tokens["river"], tokens["money"]]
    matrix: list[list[float]] = []
    for q in [tokens["bank"], tokens["river"], tokens["money"]]:
        row = simple_attention_demo(q, keys)
        matrix.append(row)
    return matrix


if __name__ == "__main__":
    # 3 tokens in sentence: "bank" (query), "river" (key1), "money" (key2)
    q_bank = [0.8, 0.1, 0.5]
    k_river = [0.1, 0.9, 0.2]
    k_money = [0.9, 0.1, 0.6]

    weights = simple_attention_demo(q_bank, [k_river, k_money])
    print("Attention Weights [river, money]:", weights)
    print("Full Attention Matrix:", attention_demo())
