import numpy as np

from rag import KB, FakeLLM, build_index, mock_embed, rag_answer, retrieve, split_text


def test_mock_embed_deterministic():
    a = mock_embed("你好RAG")
    b = mock_embed("你好RAG")
    assert a.shape == (64,)
    assert np.array_equal(a, b)


def test_build_index_shape():
    index = build_index(KB, mock_embed)
    assert index.shape == (len(KB), 64)


def test_retrieve_ranks_rag_first():
    index = build_index(KB, mock_embed)
    hits = retrieve("什么是RAG", KB, index, mock_embed, k=2)
    assert "RAG" in hits[0][0]
    assert hits[0][1] >= hits[1][1]


def test_retrieve_similarity_query():
    index = build_index(KB, mock_embed)
    hits = retrieve("怎么衡量语义相似度", KB, index, mock_embed, k=1)
    assert "embedding" in hits[0][0]


def test_retrieve_empty_query_no_crash():
    index = build_index(KB, mock_embed)
    hits = retrieve("", KB, index, mock_embed, k=2)
    assert len(hits) == 2
    assert all(s == 0.0 for _, s in hits)


def test_rag_answer_with_mock_llm():
    index = build_index(KB, mock_embed)
    answer, hits = rag_answer("什么是RAG", FakeLLM(), mock_embed, KB, index)
    assert answer.startswith("[mock]")
    assert len(hits) == 2


def test_split_text_overlap():
    chunks = split_text("abcdefghij", size=4, overlap=2)
    assert chunks == ["abcd", "cdef", "efgh", "ghij", "ij"]