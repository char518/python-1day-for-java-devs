from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="AI Quickstart")


class FakeLLM:
    def chat(self, messages: list[dict]) -> str:
        return f"[mock] 收到问题：{messages[-1]['content'][:40]}"


llm = FakeLLM()


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class ChatResponse(BaseModel):
    answer: str
    model: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    answer = llm.chat([{"role": "user", "content": req.question}])
    return ChatResponse(answer=answer, model="mock")