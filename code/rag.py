import os

import numpy as np


def cosine(x: np.ndarray, y: np.ndarray) -> float:
    return float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))


def mock_embed(text: str, dim: int = 64) -> np.ndarray:
    v = np.zeros(dim)
    for ch in text:
        v[ord(ch) % dim] += 1.0
    return v


class FakeLLM:
    def chat(self, messages: list[dict]) -> str:
        return f"[mock] 已收到 {len(messages)} 条消息，最后一条：{messages[-1]['content'][:40]}..."


class OpenAILLM:
    def __init__(self):
        from openai import OpenAI

        self.client = OpenAI(
            api_key=os.environ["LLM_API_KEY"],
            base_url=os.environ.get(
                "LLM_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ),
        )
        self.model = os.environ.get("LLM_MODEL", "qwen-plus")

    def chat(self, messages: list[dict]) -> str:
        resp = self.client.chat.completions.create(model=self.model, messages=messages)
        return resp.choices[0].message.content


def get_llm():
    if os.environ.get("LLM_API_KEY"):
        return OpenAILLM()
    print("⚠️ 未设置 LLM_API_KEY，使用 FakeLLM（管道演练模式）")
    return FakeLLM()


KB = [
    "RAG（检索增强生成）先从知识库检索相关片段，再交给大模型生成回答，能缓解幻觉并注入私有知识。",
    "embedding 把文本映射为定长浮点向量，语义相近的文本向量方向相近，常用余弦相似度衡量。",
    "FastAPI 是 Python 的异步 Web 框架，配合 pydantic 做请求校验，自带 /docs 交互式文档。",
    "今天北京晴，气温 8 摄氏度，适合出门散步。",
]


def build_index(chunks: list[str], embed) -> np.ndarray:
    return np.array([embed(c) for c in chunks])


def retrieve(query: str, chunks: list[str], index: np.ndarray, embed, k: int = 2):
    q = embed(query)
    sims = index @ q / (np.linalg.norm(index, axis=1) * np.linalg.norm(q) + 1e-10)
    top = np.argsort(sims)[::-1][:k]
    return [(chunks[i], float(sims[i])) for i in top]


def rag_answer(question: str, llm, embed, chunks, index) -> tuple[str, list]:
    hits = retrieve(question, chunks, index, embed, k=2)
    context = "\n".join(f"[{i + 1}] {c}" for i, (c, _) in enumerate(hits))
    messages = [
        {"role": "system", "content": "只根据提供的资料回答；资料不足就说不知道。"},
        {"role": "user", "content": f"资料：\n{context}\n\n问题：{question}"},
    ]
    return llm.chat(messages), hits


if __name__ == "__main__":
    llm = get_llm()
    index = build_index(KB, mock_embed)
    for q in ["什么是RAG", "怎么衡量语义相似度"]:
        answer, hits = rag_answer(q, llm, mock_embed, KB, index)
        print(f"\nQ: {q}")
        for c, s in hits:
            print(f"  hit {s:.3f}: {c[:25]}...")
        print("A:", answer)