import numpy as np
import pytest
from fastapi.testclient import TestClient

from chat_app import app
from rag import cosine

client = TestClient(app)


def test_chat_ok():
    r = client.post("/chat", json={"question": "什么是RAG"})
    assert r.status_code == 200
    assert "RAG" in r.json()["answer"]


def test_chat_empty_question_422():
    r = client.post("/chat", json={"question": ""})
    assert r.status_code == 422


def test_chat_temperature_out_of_range_422():
    r = client.post("/chat", json={"question": "hi", "temperature": 9.0})
    assert r.status_code == 422


@pytest.mark.parametrize("question", ["什么是RAG", "你好"])
def test_chat_echoes_question(question):
    r = client.post("/chat", json={"question": question})
    assert question in r.json()["answer"]


def test_cosine_self():
    v = np.array([1.0, 2.0])
    assert cosine(v, v) == pytest.approx(1.0)