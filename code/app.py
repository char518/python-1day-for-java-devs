from fastapi import FastAPI
from pydantic import BaseModel, Field

from rag import KB, build_index, get_llm, mock_embed, retrieve

app = FastAPI(title="Java→AI 最小 RAG 服务")

llm = get_llm()
index = build_index(KB, mock_embed)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=2, ge=1, le=5)


class Source(BaseModel):
    text: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    hits = retrieve(req.question, KB, index, mock_embed, k=req.top_k)
    context = "\n".join(f"[{i + 1}] {c}" for i, (c, _) in enumerate(hits))
    messages = [
        {"role": "system", "content": "只根据提供的资料回答；资料不足就说不知道。"},
        {"role": "user", "content": f"资料：\n{context}\n\n问题：{req.question}"},
    ]
    answer = llm.chat(messages)
    return AskResponse(
        answer=answer,
        sources=[Source(text=c, score=s) for c, s in hits],
    )


@app.get("/health")
def health():
    return {"status": "ok", "llm": type(llm).__name__}