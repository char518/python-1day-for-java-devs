def estimate_tokens(text: str) -> int:
    return len(text) // 2


def user_texts(messages: list[dict[str, str]]) -> list[str]:
    return [m["content"] for m in messages if m["role"] == "user"]


def token_stats(messages: list[dict[str, str]]) -> tuple[int, float]:
    counts = [estimate_tokens(m["content"]) for m in messages]
    return sum(counts), sum(counts) / len(counts)


def top_k(scored: list[dict], k: int) -> list[dict]:
    return sorted(scored, key=lambda c: c["score"], reverse=True)[:k]


if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "你是Java转AI导师"},
        {"role": "user", "content": "解释一下RAG"},
        {"role": "assistant", "content": "RAG=检索+生成"},
        {"role": "user", "content": "给个代码例子"},
    ]
    print(user_texts(messages))
    print(token_stats(messages))   # (15, 3.75)