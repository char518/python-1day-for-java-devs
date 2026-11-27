# Python in 1 Day for Java Developers — AI Application Edition

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Code: verified](https://img.shields.io/badge/code-verified-brightgreen.svg)](#verification)

**An 8-hour crash course that takes a seasoned Java backend engineer to a working LLM + RAG service in Python — in one day.**

The goal is not "learn Python". It is narrower and more useful: **read AI code, write LLM applications, test them.** Every concept is mapped to its Java counterpart, every snippet was executed and its real output is printed in the text, and the whole day builds one running case: a FastAPI service that retrieves knowledge and answers with an LLM.

📖 **[Full course (中文)](course.zh.md)** · [HTML reading version](docs/index.html) · [Companion code](code/)

## Who this is for

- 5+ years of Java / backend experience, zero Python
- Moving into AI **application** development (LLM APIs, RAG, agents) — not model training
- You want the minimum viable Python, not a 300-page language tour

## What makes it different

- **Java-anchored.** Maven → uv, Lombok → `@dataclass`, Jackson → pydantic, OkHttp → httpx, Spring Boot → FastAPI, JUnit → pytest. Muscle-memory traps are called out explicitly: `==` vs `is`, mutable default arguments, NumPy views vs copies, blocking the event loop.
- **Verified, not illustrative.** ✅ marks code actually executed on Python 3.12, with real outputs in the text. 🔑 honestly marks paths that need a real API key: client wiring verified, network call not executed.
- **Runs without an API key.** Duck-typed mock LLM + mock embedding let you run the entire RAG pipeline offline. `export LLM_API_KEY=...` switches to any OpenAI-compatible vendor (DashScope / DeepSeek / OpenAI) — the SDK works like JDBC: same API, swappable drivers.
- **Pitfall-driven.** 34 pitfalls collected across the day, plus a 29-item self-check checklist.

## The 8-hour route

| Hour | Module | Java analogy |
|---|---|---|
| 1 | Environment (uv) + syntax differences | JDK / Maven |
| 2 | Type hints + data structures + comprehensions | Generics / Stream API |
| 3 | Functions, decorators, classes, dataclass | Lambda / AOP / Lombok |
| 4 | Files & JSON, httpx, async/await | Jackson / OkHttp / CompletableFuture |
| 5 | NumPy (Pandas optional) | "Stream for arrays" |
| 6 | LLM API, embeddings, minimal RAG | JDBC-style compatible protocol |
| 7 | FastAPI + pytest | Spring Boot / JUnit |
| 8 | Capstone: FastAPI + LLM + RAG service | — |

## Quickstart (companion code)

Requires [uv](https://docs.astral.sh/uv/). No API key needed — the service starts in mock mode.

```bash
cd code
uv sync                            # locked deps; uv fetches Python 3.12 if needed
uv run pytest -q                   # 9 tests
uv run uvicorn app:app --reload    # open http://127.0.0.1:8000/docs
```

```bash
curl -s http://127.0.0.1:8000/ask -H 'Content-Type: application/json' \
     -d '{"question":"什么是RAG"}'
# -> {"answer": "...", "sources": [{"text": "...", "score": 0.408}, ...]}
```

Switch to a real LLM (any OpenAI-compatible vendor):

```bash
export LLM_API_KEY=your-key
export LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
export LLM_MODEL=qwen-plus
uv run uvicorn app:app             # /health now reports OpenAILLM
```

## Repository layout

```
course.zh.md        Full 8-hour course (Chinese, the main deliverable)
docs/index.html     Styled HTML reading version (GitHub Pages ready)
code/               Verified companion code
  rag.py            Embedding + cosine retrieval + minimal RAG (mock & real)
  chat_app.py       P7: minimal FastAPI /chat endpoint
  app.py            P8 capstone: /ask with answer + sources
  test_*.py         pytest suite (TestClient ≈ MockMvc)
  pyproject.toml    Locked dependencies (uv.lock)
```

## Verification

- Environment: macOS (arm64) / Python 3.12 (uv-managed) / uv 0.7.19.
- ✅ snippets were executed; printed outputs are real run results. Reproduce with `cd code && uv sync && uv run pytest -q`.
- 🔑 snippets (real LLM / embedding network calls): client construction and wiring verified; no paid API call was made. Set `LLM_API_KEY` to run them yourself.
- Mock embedding is a character-hash vector — it rehearses the pipeline shape, **not** semantics. Real retrieval quality requires a real embedding model (the code shape does not change).

## Relationship to the full course

This is the 1-day on-ramp: the minimum Python needed to start building AI applications. It pairs with the author's longer Java-to-AI agent course (8 weeks, project-driven). <!-- TODO: add public course URL -->

## License

[MIT](LICENSE)