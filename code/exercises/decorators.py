import time
from functools import wraps


def retry(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        for attempt in range(3):
            try:
                return fn(*args, **kwargs)
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(0.1 * (attempt + 1))
    return wrapper


if __name__ == "__main__":
    calls = {"n": 0}

    @retry
    def fake_llm(prompt: str) -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise TimeoutError("限流")
        return f"回答:{prompt}"

    print(fake_llm("什么是RAG"), "| 尝试次数:", calls["n"], "| 函数名:", fake_llm.__name__)