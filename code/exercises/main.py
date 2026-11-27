model = "qwen-plus"
max_tokens = 1024
temperature = 0.7

messages = [
    {"role": "system", "content": "你是资深Java导师"},
    {"role": "user", "content": "Python的dict相当于Java的什么?"},
]

print(f"model={model}, turns={len(messages)}, temp={temperature}")

for i, msg in enumerate(messages):
    print(f"[{i}] {msg['role']}: {msg['content'][:20]}")

if not messages:
    print("空对话")

a = [{"role": "user"}]
b = [{"role": "user"}]
print(a == b, a is b)

reply = None
if reply is None:
    print("还没调用LLM")


def estimate_tokens(text: str) -> int:
    return len(text) // 2


def estimate_cost(tokens: int, price_per_1k: float) -> float:
    return tokens / 1000 * price_per_1k


print(estimate_tokens("你好世界"))
print(f"cost={estimate_cost(2000, 0.8):.4f}元")