from dataclasses import asdict, dataclass, field


@dataclass
class ChatMessage:
    role: str
    content: str
    tokens: int = 0


@dataclass
class Chunk:
    id: str
    text: str
    score: float = 0.0


@dataclass
class Session:
    model: str = "qwen-plus"
    messages: list = field(default_factory=list)


class ChatSession:
    def __init__(self, model: str = "qwen-plus"):
        self.model = model
        self.messages: list[dict] = []

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def payload(self) -> dict:
        return {"model": self.model, "messages": self.messages}


if __name__ == "__main__":
    m = ChatMessage("user", "解释RAG")
    print(m)
    print(m == ChatMessage("user", "解释RAG"))
    print(asdict(m))
    s = ChatSession()
    s.add("user", "你好")
    print(s.payload())