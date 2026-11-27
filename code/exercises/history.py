import json
from dataclasses import asdict
from pathlib import Path

from models import ChatMessage

p = Path("data") / "history.json"
p.parent.mkdir(exist_ok=True)

msgs = [ChatMessage("user", "解释RAG"), ChatMessage("assistant", "RAG=检索+生成")]
p.write_text(json.dumps([asdict(m) for m in msgs], ensure_ascii=False, indent=2), encoding="utf-8")
loaded = [ChatMessage(**d) for d in json.loads(p.read_text(encoding="utf-8"))]
assert loaded == msgs
print("roundtrip ok:", len(loaded), "messages")