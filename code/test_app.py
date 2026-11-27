from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_ask_returns_sources():
    r = client.post("/ask", json={"question": "什么是RAG"})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"]
    assert len(body["sources"]) == 2
    assert "RAG" in body["sources"][0]["text"]


def test_ask_validation():
    assert client.post("/ask", json={"question": ""}).status_code == 422
    assert client.post("/ask", json={"question": "hi", "top_k": 99}).status_code == 422


def test_health():
    assert client.get("/health").json()["status"] == "ok"