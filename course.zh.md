# Python 1 天 8 小时最小必要集（Java 后端 → AI 应用开发）

> 面向 10 年 Java 经验、Python 零基础的工程师。目标不是"学会 Python"，而是：**能读懂 AI 代码、能写 LLM 应用、能测试**。
>
> 全天贯穿同一个案例：搭一个「对话 → 调 LLM → 检索知识 → 回答」的服务，每个模块的练习都往这个服务上添一块砖。
>
> **验证标注**：✅ = 实测通过（验证环境见附录）；🔑 = 需要真实 API Key，代码接线已验证、网络调用未实测。
>
> 节奏：每小时约 50 分钟读 + 10 分钟动手。常见坑随阶段分散讲，第 8 阶段汇总。
>
> 配套可运行代码在仓库 `code/` 目录（rag.py / chat_app.py / app.py + 测试）：`cd code && uv sync && uv run pytest -q` 即可复现文中 ✅ 结果。

**结论前置**：你只需要一张映射表 + 一天肌肉记忆纠正：

| 你的 Java 存量 | Python AI 开发对应物 |
|---|---|
| JDK + javac 编译 | CPython 解释器（3.12，无编译步骤） |
| Maven + pom.xml | uv + pyproject.toml |
| Lombok `@Data` | `@dataclass` |
| Jackson | `json` 模块 / pydantic |
| OkHttp / WebClient | httpx |
| Spring Boot | FastAPI |
| JUnit | pytest |
| 泛型 + 编译期检查 | 类型标注 + pyright（**运行时不强制**，这是最大思维转变） |

## 学习路线表（8 小时）

| 小时 | 阶段 | 模块 | Java 类比 | 动手产出 | 必/选 |
|---|---|---|---|---|---|
| 1 | P1 | 环境依赖 + 语法差异 | JDK / Maven | 项目骨架 + 消息处理脚本 | 必学 |
| 2 | P2 | 类型标注 + list/dict/set/tuple + 推导式 | 泛型 / Stream API | 消息过滤与 token 统计 | 必学 |
| 3 | P3 | 函数/装饰器 + 类/dataclass | Lambda / AOP / Lombok | `ChatMessage` dataclass + `@retry` 装饰器 | 必学（带参装饰器选学） |
| 4 | P4 | 文件/JSON + httpx + async | Jackson / OkHttp / CompletableFuture | 对话落盘 + 调真实 HTTP API | 必学（asyncio 深水区选学） |
| 5 | P5 | NumPy / Pandas | 无直接对应，当"数组版 Stream" | 手写余弦相似度 | NumPy 必学，Pandas 选学 |
| 6 | P6 | LLM API + embedding + 最小 RAG | JDBC（兼容协议） | 30 行 numpy 版 RAG | 必学 |
| 7 | P7 | FastAPI + pytest | Spring Boot / JUnit | `/chat` 接口 + 单测 | 必学 |
| 8 | P8 | 综合项目 + 坑汇总 + 自测清单 | — | FastAPI + LLM + RAG 问答服务 | 必学 |

P6 需要一个 OpenAI 兼容 API Key（通义 / DeepSeek / OpenAI 任一）。**没有 Key 不阻塞**：全天代码内置 mock 双实现，无 Key 也能跑通完整管道。

---

## 第 1 阶段（第 1 小时）：环境与依赖 + Python vs Java 差异

### 1.1 环境与依赖【必学，约 25 分钟】

**一句话原理**：Java 依赖全局共享（`~/.m2`），靠每个项目的 classpath 隔离；Python 依赖直接装进"解释器所在目录"，两个项目要用同一个库的不同版本就会打架 → **每个项目自带一个 `.venv`（独立解释器 + 独立依赖目录）**。uv 就是管这一切的 Maven，且比 pip 快一个数量级。

| Java | Python（uv） |
|---|---|
| 装 JDK | 装 Python（uv 自动下载管理，无需手动装） |
| `mvn archetype:generate` | `uv init` |
| pom.xml `<dependencies>` | pyproject.toml `dependencies` |
| 加依赖 + `mvn install` | `uv add httpx` |
| `~/.m2` 全局仓库 | 每项目 `.venv` |
| `mvn exec:java` / `java -jar` | `uv run python main.py` |
| `mvn test` | `uv run pytest` |
| Gradle lockfile | `uv.lock`（自动生成，提交进 git） |

命令（macOS，一次装好全天依赖）：

```bash
brew install uv                       # 已装可跳过；无 brew 用: curl -LsSf https://astral.sh/uv/install.sh | sh
uv init --python 3.12 ai-quickstart   # macOS 系统 Python 常是 3.9，必须显式指定 3.12，uv 会自动下载
cd ai-quickstart
uv add httpx openai fastapi "uvicorn[standard]" numpy pandas pytest
uv run python main.py                 # 铁律：永远 uv run，不要直接 python
```

`uv run` 自动做两件事：定位/创建 `.venv` + 按 `uv.lock` 同步依赖。**不需要**老教程里的 `source .venv/bin/activate`。

pyproject.toml ≈ pom.xml：

```toml
[project]
name = "ai-quickstart"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["httpx>=0.27", "openai>=1.40"]
```

【选学】手动 `python -m venv` + pip（只为看懂老项目/老教程）；pyenv、conda（训练场景常见，AI **应用**开发 uv 足够）。

### 1.2 语法差异【必学，约 25 分钟】

10 条肌肉记忆纠正表：

| # | Java 习惯 | Python 现实 |
|---|---|---|
| 1 | `String s = "x";` | `s = "x"`，无类型声明、无分号 |
| 2 | `{}` 划分代码块 | **缩进就是语法**（4 空格，Tab/空格混用直接报错） |
| 3 | `null` | `None`，判空固定写 `x is None` |
| 4 | `==` 比引用，`equals` 比值 | **正好相反**：`==` 比值，`is` 比引用 |
| 5 | `new Foo()` | `Foo()`，没有 new |
| 6 | camelCase | snake_case（PEP8 规范） |
| 7 | `String.format` / `+` 拼接 | f-string：`f"{model} 轮数={len(msgs)}"` |
| 8 | int 溢出换 long / BigInteger | int 任意精度，随便乘 |
| 9 | `5/2 == 2` | `5/2 == 2.5`（永远 float），整除用 `5//2 == 2` |
| 10 | 编译器兜底 | 无编译，属性名拼错**运行时才炸** → 类型标注 + 测试是你的新兜底 |

可运行示例 ✅（AI 场景：构造 LLM 请求消息）。存为 `main.py`，`uv run python main.py`：

```python
model = "qwen-plus"
max_tokens = 1024
temperature = 0.7

# dict ≈ HashMap，list ≈ ArrayList；字面量长得就是 JSON
messages = [
    {"role": "system", "content": "你是资深Java导师"},
    {"role": "user", "content": "Python的dict相当于Java的什么?"},
]

print(f"model={model}, turns={len(messages)}, temp={temperature}")

# enumerate ≈ IntStream.range + get，一次拿到索引和元素
for i, msg in enumerate(messages):
    print(f"[{i}] {msg['role']}: {msg['content'][:20]}")   # [:20] ≈ substring(0, 20)

# 真值判断：None/0/""/[]/{} 都算 False ≈ 自动帮你做了 null + isEmpty 检查
if not messages:
    print("空对话")

a = [{"role": "user"}]
b = [{"role": "user"}]
print(a == b, a is b)        # True False —— == 是 equals，is 才是 Java 的 ==

reply = None
if reply is None:            # 判空固定写法
    print("还没调用LLM")

# 函数预览（P3 细讲）：def ≈ 方法；标注 ≈ 泛型提示，但运行时不强制
def estimate_tokens(text: str) -> int:
    return len(text) // 2    # 粗估 token 数，顺便演示 // 整除

print(estimate_tokens("你好世界"))   # 2
```

实测输出：

```
model=qwen-plus, turns=2, temp=0.7
[0] system: 你是资深Java导师
[1] user: Python的dict相当于Java的什
True False
还没调用LLM
2
```

注意第 2 条被 `[:20]` 截断了——切片就是 `substring`，这是真实行为不是 bug。

【选学】`match` 语句（≈ switch，3.10+）、海象运算符 `:=`。swap 不用临时变量 `a, b = b, a` 顺手记一下即可。

### 1.3 本阶段常见坑

1. **直接 `python main.py`** → 用到系统老解释器，报 `ModuleNotFoundError` 或语法错。永远 `uv run python main.py`。
2. **Tab/空格混用** → `TabError`。编辑器统一设 4 空格。
3. **`if not x` 误伤**：`0` 和 `""` 也是 falsy。数值判空要显式写 `if x is None`，别照搬 Java 的 `if (x != null)` 肌肉记忆。
4. **用 `is` 比值**：`if reply is "ok"` 因字符串驻留偶尔"能跑"，换个值就错。比值永远 `==`，`is` 只用于 `None`。
5. **没有编译期报错**：Java 里 IDE 红线救你的场景，Python 全拖到运行时 → P2 类型标注、P7 pytest 是必修课不是选修课。

### 动手任务 + 自测（10 分钟）

任务：

1. 跑上面 4 条命令建项目，把示例存进 `main.py` 跑通。
2. 把 `a == b` 改成 `a is b`，先预测输出再验证。
3. 自己写 `estimate_cost(tokens: int, price_per_1k: float) -> float` 返回调用成本，用 f-string 打印结果。

自测（能答上即过关）：

- 为什么 Python 每项目要 `.venv`，而 Java 基本不用？
- `==` 和 `is` 分别对应 Java 的什么？
- `uv run` 帮你做了哪两件事？

---

## 第 2 阶段（第 2 小时）：类型标注 + 数据结构 + 推导式

### 2.1 类型标注【必学，约 15 分钟】

**思维转变（本阶段最重要的一句话）**：Java 的类型由 javac 强制执行，写错编译不过；Python 的标注**运行时完全不管**，它是写给 IDE 和静态检查器看的"合同"。兜底链条变成：标注 + pyright（IDE 红线）+ pytest（P7），而不是编译器。

| Java | Python 标注 | 说明 |
|---|---|---|
| `String s` | `s: str` | 基本类型：`int float bool str bytes` |
| `List<String>` | `list[str]` | 3.9+ 直接用内置泛型 |
| `Map<String, Integer>` | `dict[str, int]` | |
| `Optional<String>` / `@Nullable` | `str \| None` | 3.10+ 写法，AI SDK 里大量出现 |
| `void` | `-> None` | |
| `Object` | `Any`【选学】 | 逃生舱，少用 |

```python
def estimate_tokens(text: str) -> int:
    return len(text) // 2

# 返回 (总数, 平均数)：tuple 多返回值，Java 得专门写个 DTO
def token_stats(msgs: list[dict[str, str]]) -> tuple[int, float]:
    counts = [estimate_tokens(m["content"]) for m in msgs]
    return sum(counts), sum(counts) / len(counts)

def last_reply(msgs: list[dict[str, str]]) -> str | None:   # ≈ Optional<String>
    for m in reversed(msgs):
        if m["role"] == "assistant":
            return m["content"]
    return None
```

工具链：IDE 装 Pylance/pyright ≈ Java IDE 的实时 inspection【必学，装好就行】；mypy 命令行严格模式 ≈ 额外一道 javac【选学】。

【选学，读懂即可】老代码里的 `typing.List / Dict / Optional`（3.9 前写法，等价于内置泛型）；`TypedDict`——给 dict 定形状，运行时仍是普通 dict，≈ 只存在于编译期的 DTO 接口：

```python
from typing import TypedDict
class ChatMessage(TypedDict):
    role: str
    content: str
```

### 2.2 四大容器【必学，约 25 分钟】

选型表（AI 场景直接对号入座）：

| Python | Java | 可变? | AI 应用里装什么 |
|---|---|---|---|
| `list` | ArrayList | 可变 | messages 对话历史、chunks 文档块 |
| `dict` | **LinkedHashMap**（保插入序） | 可变 | 单条消息、JSON 请求体、配置 |
| `tuple` | 不可变 List / record | 不可变 | 多返回值、(model, temp) 参数对 |
| `set` | HashSet | 可变 | 检索结果去重、停用词表 |

```python
# ---- list ≈ ArrayList ----
messages = [{"role": "user", "content": "你好"}]
messages.append({"role": "user", "content": "解释RAG"})  # add
messages[-1]          # 最后一个！Java 要 get(size()-1)
messages[1:3]         # subList(1,3)，含头不含尾
len(messages)         # size()

# ---- dict ≈ LinkedHashMap ----
msg = {"role": "user", "content": "你好"}
msg["role"]                 # 取值；键不存在直接抛 KeyError（不是返回 null！）
msg.get("tool_calls")       # ≈ map.get，缺失返回 None
msg.get("role", "user")     # ≈ getOrDefault
msg["temperature"] = 0.7    # put
for k, v in msg.items():    # entrySet()
    print(k, v)

# ---- tuple：不可变，可当 dict 的键（≈ 重写 hashCode/equals 的值对象）----
total, avg = token_stats(messages)     # 解构 ≈ record 模式匹配

# ---- set ≈ HashSet ----
chunks = [{"id": "c1"}, {"id": "c2"}, {"id": "c1"}]
unique_ids = {c["id"] for c in chunks}       # 去重，in 判断 O(1)
print("c1" in unique_ids)                    # contains
```

引用与拷贝（和 Java 语义一致，但写法新）✅：

```python
a = [1, 2]
b = a          # 引用赋值，改 b 就是改 a（Java 同款）
c = a[:]       # 浅拷贝 ≈ new ArrayList<>(a)；也可 list(a) / a.copy()
b.append(3)
print(a, c)    # [1, 2, 3] [1, 2]
```

### 2.3 推导式 = 压缩版 Stream API【必学，约 15 分钟】

对照表（把 Stream 三段式压成一行）：

| Java Stream | Python |
|---|---|
| `.map(f).collect(toList())` | `[f(x) for x in xs]` |
| `.filter(p).collect(toList())` | `[x for x in xs if p(x)]` |
| `.mapToInt(f).sum()` | `sum(f(x) for x in xs)` |
| `.anyMatch(p)` / `.allMatch(p)` | `any(p(x) for x in xs)` / `all(...)`（同样短路） |
| `.collect(toMap(k, v))` | `{k(x): v(x) for x in xs}` |
| `.collect(toSet())` | `{x for x in xs}` |
| `.flatMap(...)` | `[y for x in xs for y in x]`（从左往右读就是嵌套 for） |
| `Comparator.comparing(f).reversed()` | `sorted(xs, key=f, reverse=True)` |

AI 实战四连 ✅：

```python
messages = [
    {"role": "system", "content": "你是Java转AI导师"},
    {"role": "user", "content": "解释一下RAG"},
    {"role": "assistant", "content": "RAG=检索+生成"},
    {"role": "user", "content": "给个代码例子"},
]

# filter + map：只留用户发言
user_texts = [m["content"] for m in messages if m["role"] == "user"]
# ['解释一下RAG', '给个代码例子']

# anyMatch：对话里有没有工具调用
has_tool = any(m["role"] == "tool" for m in messages)   # False

# toMap：RAG 的 chunk 索引 id → text（重复键后者覆盖前者，≈ toMap 的 merge）
index = {c["id"]: c["text"] for c in chunks}

# RAG top-k：按相似度排序取前 2（P6 的核心动作，今天先混个脸熟）
scored = [{"text": "RAG定义", "score": 0.9},
          {"text": "无关内容", "score": 0.2},
          {"text": "RAG流程", "score": 0.8}]
top2 = sorted(scored, key=lambda c: c["score"], reverse=True)[:2]
# ['RAG定义', 'RAG流程']
```

`sum(...)` 里那个不带方括号的叫**生成器表达式**：惰性求值，不建中间列表——Stream 流水线本身也是惰性的，同一个思想。`lambda` 先当"单行匿名函数"用，P3 细讲。

flatMap 式嵌套【必学，RAG 切块会用】：`[chunk for doc in docs for chunk in doc["chunks"]]`。

【选学】`zip(a, b)` 把两个列表按位配对（≈ 手写 IntStream 拉链）；`enumerate` 你在 P1 已用过。

### 2.4 本阶段常见坑

1. **`msg["缺失键"]` 抛 KeyError**，不像 Java `map.get` 返回 null。不确定有没有的键一律 `.get()`。
2. **标注不校验**：`estimate_tokens(123)` 运行时照样传进去，直到 `len(123)` 才炸。边界校验靠 P7 的 pydantic，标注只防君子。
3. **`[[]] * 3` 是 3 个引用指向同一个 list**（实测：`grid[0].append(1)` 后三个全变 `[[1],[1],[1]]`）。≈ `Arrays.fill` 填了同一个对象。要独立副本写 `[[] for _ in range(3)]`。
4. **`b = a` 不是拷贝**；浅拷贝 `a[:]` 也只拷外壳，嵌套结构要 `copy.deepcopy`【选学】。
5. **set 去重会丢顺序**；要保序去重用 `list(dict.fromkeys(xs))`【选学 trick】。
6. **dict 保插入序**（3.7+），别拿 HashMap 的"无序"直觉来推理。

### 动手任务 + 自测（10 分钟）

任务：在项目里新建 `chat_stats.py`，自己实现三个函数并跑通——

1. `user_texts(messages) -> list[str]`：filter+map 只留用户发言
2. `token_stats(messages) -> tuple[int, float]`：总 token 与平均 token（用上面的粗估法）
3. `top_k(scored: list[dict], k: int) -> list[dict]`：按 score 取前 k

对答案：用文中 messages，`token_stats` 应输出 `(15, 3.75)`。

自测：

- Python 标注和 Java 泛型的本质区别？各由谁检查？
- `msg["x"]` 和 `msg.get("x")` 哪个才对应 Java 的 `map.get`？
- 把 `[f(x) for x in xs if p(x)]` 翻译成 Stream 调用链。
- 为什么 `[[]] * 3` 会共享同一个 list？

---

## 第 3 阶段（第 3 小时）：函数/装饰器 + 类/dataclass

### 3.1 函数：一等公民【必学，约 20 分钟】

**思维转变**：Java 方法必须寄生在类里，函数式能力是受限的 Lambda；Python 函数本身就是对象，能赋值、传参、返回、被包一层再还回来——装饰器全靠这个能力。

| Java | Python |
|---|---|
| 方法重载（同名不同参） | **没有重载**！用默认参数 + 关键字参数替代 |
| Builder 一堆 setter | `def f(x, model="qwen-plus", temp=0.7)` 默认参数 |
| `varargs Object...` | `*args`（收位置参数成 tuple） |
| `Map<String,Object> options` | `**kwargs`（收关键字参数成 dict） |
| `Function<T,R>` / 策略模式 | 直接把函数当参数传 |
| 单表达式 Lambda | `lambda x: x + 1` |

```python
# 默认参数 + 关键字参数 ≈ 重载 + Builder 合体
def build_messages(prompt: str, system: str = "你是AI助手",
                   history: list | None = None) -> list[dict]:
    if history is None:          # 为什么不用 history=[]？见下方头号大坑
        history = []
    return [{"role": "system", "content": system},
            *history,            # * 解包 ≈ addAll
            {"role": "user", "content": prompt}]

# **kwargs：调用方随意追加选项；{**a, **b} 合并 dict ≈ putAll（后者覆盖）
def make_params(prompt: str, **options) -> dict:
    return {"model": "qwen-plus", "messages": build_messages(prompt), **options}

make_params("解释RAG", temperature=0.1, max_tokens=512)
# 实测输出：{'model': 'qwen-plus', 'messages': [...], 'temperature': 0.1, 'max_tokens': 512}
```

这不是玩具写法——P6 调 LLM 就是 `client.chat.completions.create(**params)`，把 dict 解包成关键字参数。今天先练熟。

```python
# 函数当参数 ≈ 策略模式，不用定义接口
def estimate_tokens(text: str) -> int:
    return len(text) // 2

def count(text: str, counter) -> int:   # counter 标注 Callable[[str], int]【选学】
    return counter(text)

count("你好世界", estimate_tokens)      # 2
```

**头号大坑现场演示** ✅：

```python
def bad_append(msg, history=[]):    # 默认值在 def 时创建一次，所有调用共享！
    history.append(msg)
    return history

bad_append("a")    # ['a']
bad_append("b")    # ['a', 'b']  ← 上次的残留！≈ Java 用 static 字段当默认值
```

修复固定式：默认值写 `None`，函数体内 `if history is None: history = []`。

### 3.2 装饰器：5 行写出一个 AOP 切面【必学；带参装饰器选学，约 15 分钟】

**和 Java 注解的本质区别**：`@Transactional` 是 passive 元数据，靠 Spring 框架扫描才生效；Python 装饰器是**主动的函数包装**，`@retry` 等价于 `f = retry(f)`，定义当场生效，不需要任何框架。你写的每个 `@app.get`、`@pytest.fixture` 都是这个原理。

LLM 调用天天遇到限流/超时，手写一个重试切面 ✅（`try/except ≈ try/catch`，`raise ≈ throw`，P4 细讲）：

```python
import time
from functools import wraps

def retry(fn):                          # 收一个函数
    @wraps(fn)                          # 保留原函数名/文档，FastAPI、pytest 靠它做内省
    def wrapper(*args, **kwargs):       # 还一个包装后的函数（闭包 ≈ 捕获变量的 lambda）
        for attempt in range(3):
            try:
                return fn(*args, **kwargs)
            except Exception:
                if attempt == 2:
                    raise               # 最后一次仍失败，原样抛出
                time.sleep(0.1 * (attempt + 1))   # 生产用指数退避 0.5 * 2**attempt
    return wrapper

calls = {"n": 0}

@retry
def fake_llm(prompt: str) -> str:
    calls["n"] += 1
    if calls["n"] < 3:
        raise TimeoutError("限流")
    return f"回答:{prompt}"

fake_llm("什么是RAG")
# 实测：回答:什么是RAG | 尝试次数: 3 | 函数名: fake_llm
```

标准库白送一个实用装饰器——embedding 结果缓存（≈ Guava Cache 包方法）：

```python
from functools import cache

@cache
def embed(text: str) -> tuple:    # 相同 text 只算一次，重复命中缓存
    ...
```

【选学，读懂即可】带参装饰器 `@retry(times=5)` 是三层嵌套（再包一层收参数）。你不需要会写，但要认识：FastAPI 的 `@app.get("/chat")`、pytest 的 `@pytest.mark.parametrize` 全是它。

### 3.3 类与 dataclass【必学，约 20 分钟】

普通类 ≈ 去掉 Lombok 的 POJO，`self` ≈ 显式写出来的 `this`：

```python
class ChatSession:
    def __init__(self, model: str = "qwen-plus"):   # ≈ 构造器
        self.model = model                          # ≈ this.model = model
        self.messages: list[dict] = []

    def add(self, role: str, content: str) -> None: # 实例方法第一个参数永远是 self
        self.messages.append({"role": role, "content": content})

s = ChatSession()        # 没有 new
s.add("user", "你好")

class RAGSession(ChatSession):          # ≈ extends
    def __init__(self, model="qwen-plus", top_k=3):
        super().__init__(model)         # ≈ super(model)
        self.top_k = top_k
```

**鸭子类型**：没有 `implements`。只要对象有 `complete` 方法就能传进去，≈ 结构化接口——"长得像鸭子就行，不用出示鸭子证书"。mock LLM 做测试（P7）全靠它：

```python
class FakeLLM:
    def complete(self, prompt: str) -> str:
        return "fake:" + prompt

def ask(llm, prompt: str) -> str:   # 不声明任何接口类型
    return llm.complete(prompt)
```

**dataclass ≈ Lombok `@Data`**，AI 代码里 DTO 的标准写法 ✅：

```python
from dataclasses import dataclass, field, asdict

@dataclass
class ChatMessage:
    role: str
    content: str
    tokens: int = 0

m = ChatMessage("user", "解释RAG")
print(m)                              # 自动 __repr__ ≈ toString
print(m == ChatMessage("user", "解释RAG"))   # 自动 __eq__ ≈ equals → True
print(asdict(m))                      # ≈ Jackson convertValue 成 Map，P4 接 JSON
# 实测：{'role': 'user', 'content': '解释RAG', 'tokens': 0}

@dataclass
class Session:
    model: str = "qwen-plus"
    messages: list = field(default_factory=list)   # 可变默认值必须用工厂！
```

要点：

- `@dataclass` 自动生成 `__init__` / `__repr__` / `__eq__` ≈ `@Data` 三件套；`@dataclass(frozen=True)` ≈ record / `@Value` 不可变。
- 可变默认值直接写 `messages: list = []` 会**报错**（dataclass 替你挡了 3.1 的头号坑），必须 `field(default_factory=list)`——每个实例拿到独立新 list（实测 `s1` append 后 `s2.messages` 仍是 `[]`）。
- 双下划线方法 ≈ Object 的协议方法：`__str__`≈toString、`__eq__`≈equals、`__len__`≈让 `len()` 生效。【选学：`__enter__/__exit__` 上下文管理器 ≈ try-with-resources，P4 文件会用到】

选型一句话：**纯数据载体 → dataclass；有状态的服务对象（session、client 封装）→ 普通类；HTTP 边界要校验的输入输出 → pydantic（P7）**。

### 3.4 本阶段常见坑

1. **可变默认参数** `def f(x=[])`：所有调用共享同一个 list（3.1 已演示）。固定式：`None` 哨兵。
2. **没有重载**：写两个同名 `def`，后一个静默覆盖前一个，不报错。用默认参数。
3. **忘写 self**：`def add(role, content)` 调用时 `s.add("user","hi")` → `TypeError: takes 2 positional arguments but 3 given`。实例方法第一个参数永远是 self。
4. **类属性可变共享** ≈ static 字段：`class Bad: items = []`，实测 `b1.items.append(1)` 后 `b2.items` 也是 `[1]`。实例数据放 `__init__` 里。
5. **装饰器忘 `@wraps`**：函数名变成 `wrapper`，FastAPI 路由内省、pytest 报告全乱。包装函数固定加。

### 动手任务 + 自测（10 分钟）

任务：新建 `models.py` + `decorators.py`——

1. `models.py`：`ChatMessage`、`Chunk(id, text, score=0.0)` 两个 dataclass；`ChatSession` 类带 `add()` 和 `payload()`（返回可直接发给 LLM 的 dict）。
2. `decorators.py`：默写 `@retry`（不看上文），用"前两次抛异常、第三次成功"的假函数验证。
3. 用 `asdict()` 把一条 `ChatMessage` 转成 dict 打印。

自测：

- Java 注解和 Python 装饰器的本质区别？`@retry` 等价于哪行赋值？
- `def f(msgs=[])` 相当于 Java 里犯了什么错？固定修法？
- `@dataclass` 自动生成哪三个方法？对应 Lombok 什么？
- 为什么 dataclass 的可变默认值必须 `default_factory`？

---

## 第 4 阶段（第 4 小时）：文件/JSON + httpx + async

### 4.1 文件与 JSON【必学，约 15 分钟】

| Java | Python |
|---|---|
| `Paths.get("data", "a.json")` | `Path("data") / "a.json"`（`/` 运算符拼路径） |
| `Files.createDirectories` | `p.parent.mkdir(exist_ok=True)` |
| `Files.readString / writeString` | `p.read_text() / p.write_text()` |
| try-with-resources | `with open(...) as f:`（自动 close） |
| Jackson `ObjectMapper` | `json.dumps()`（写）/ `json.loads()`（读） |

对话落盘 + 读回 ✅（串起 P3 的 dataclass）：

```python
from pathlib import Path
import json
from dataclasses import asdict

p = Path("data") / "history.json"
p.parent.mkdir(exist_ok=True)

msgs = [ChatMessage("user", "解释RAG"), ChatMessage("assistant", "RAG=检索+生成")]

# 存：dataclass → dict → JSON 字符串 ≈ writeValueAsString
p.write_text(json.dumps([asdict(m) for m in msgs], ensure_ascii=False, indent=2),
             encoding="utf-8")

# 取：JSON → dict → dataclass（** 解包就是 P3 学的字典解包）
loaded = [ChatMessage(**d) for d in json.loads(p.read_text(encoding="utf-8"))]
print(loaded[0] == msgs[0])    # True，dataclass 自动 __eq__
```

**必记坑**：`json.dumps` 默认 `ensure_ascii=True`，中文全变转义（实测）：

```python
json.dumps({"q": "你好"})                     # {"q": "\u4f60\u597d"}
json.dumps({"q": "你好"}, ensure_ascii=False)  # {"q": "你好"}  ← 永远加这个
```

【必学小知识点】JSONL：一行一个 JSON，AI 数据集/对话日志的通用格式，追加写友好：

```python
with open(p, "a", encoding="utf-8") as f:    # "a" 追加；with ≈ try-with-resources
    f.write(json.dumps(asdict(m), ensure_ascii=False) + "\n")
```

### 4.2 httpx 调 API【必学，约 20 分钟】

≈ OkHttp 的手感 + RestTemplate 的便利，同步异步都支持（requests 的现代替代，AI 项目标配）。

```python
import httpx

r = httpx.get("https://httpbin.org/get", params={"q": "rag"}, timeout=10)
r.raise_for_status()        # 4xx/5xx 抛 HTTPStatusError；不写这行则和 OkHttp 一样不抛！
print(r.json()["args"])     # 实测：{'q': 'rag'}；.json() ≈ Jackson readValue 成 Map

# POST JSON —— 这就是 LLM 请求的形状；json= 自动序列化并设 Content-Type
r = httpx.post("https://api.example.com/v1/chat/completions",
               json={"model": "qwen-plus",
                     "messages": [{"role": "user", "content": "hi"}]},
               headers={"Authorization": "Bearer sk-..."},
               timeout=60)  # httpx 默认超时只有 5 秒！LLM 慢响应必须显式调大
```

复用连接 ≈ OkHttpClient 单例/连接池：

```python
with httpx.Client(timeout=30) as client:
    r1 = client.get(url1)
    r2 = client.get(url2)
```

异常处理 ≈ try/catch，一分钟对照：`except httpx.TimeoutException as e` ≈ `catch (IOException e)`；`raise` ≈ `throw`；**没有 checked exception**，不用声明不用强制接。

```python
try:
    httpx.get(url, timeout=5).raise_for_status()
except httpx.HTTPStatusError as e:
    print(e.response.status_code)     # 实测捕获 500
except httpx.TimeoutException:
    print("超时")                      # 实测捕获
```

真实 API 练习目标（可直连、无需 Key）：`https://wttr.in/Beijing?format=j1` 返回 JSON（示例输出 `temp_C: "8"`）——动手任务用它练"取外部数据给 LLM 当工具结果"。

环境注：httpx 默认读 `HTTP_PROXY/HTTPS_PROXY/NO_PROXY` 环境变量（JVM 可不会）。若报代理/`InvalidURL` 错（某些沙箱/CI 会注入畸形 NO_PROXY），先查环境变量，或 `httpx.Client(trust_env=False)` 绕过。

### 4.3 async/await【必学：会读会写简单并发；asyncio 深水区选学，约 15 分钟】

**心智模型（最重要）**：asyncio 是**单线程事件循环**——所有任务在同一根线程上轮流跑，只在 `await` 处让出控制权。≈ Netty 的 IO 线程：IO 并发极强，但谁阻塞这根线程，全体请求一起死。

| Java | Python |
|---|---|
| 返回 `CompletableFuture<T>` 的方法 | `async def f() -> T` |
| `.join()`（阻塞当前线程） | `await`（让出控制权，不阻塞线程） |
| `allOf(f1, f2).join()` | `await asyncio.gather(f1(), f2())` |
| `SpringApplication.run` | `asyncio.run(main())` |
| 阻塞任务丢线程池 | 用异步库；`run_in_executor`【选学】 |

```python
import asyncio

async def fake_embed(text: str) -> list[float]:
    await asyncio.sleep(0.3)          # 模拟网络 IO
    return [len(text) * 0.1]

async def main():
    results = await asyncio.gather(fake_embed("你好"), fake_embed("RAG"))
    print(results)

asyncio.run(main())
# 实测：[[0.2], [0.30000000000000004]]，总耗时 0.30s（串行要 0.6s）
```

真实形态（对本地慢接口实测：gather 0.34s vs 串行 0.62s）：

```python
async with httpx.AsyncClient(timeout=30) as client:
    rs = await asyncio.gather(client.get(url1), client.get(url2))
```

**阻塞事件循环现场** ✅：把上面的 `await asyncio.sleep(0.3)` 换成 `time.sleep(0.3)`，gather 两个任务耗时 **0.61s**——并发全废，因为同步 sleep 霸占了唯一的事件循环线程。这就是"Netty IO 线程上 Thread.sleep"的 Python 版。

选型一句话：脚本/批处理用同步 httpx 足够；FastAPI 服务（P7）用 async。CPU 密集计算 asyncio 帮不了你（GIL），丢进程池【选学】。

### 4.4 本阶段常见坑

1. **`ensure_ascii=True` 默认值**：中文变 `\u4f60\u597d`。dumps 永远加 `ensure_ascii=False`。
2. **不写 `encoding="utf-8"`**：open/read_text 默认编码跟平台走（Windows 是 GBK），跨平台必炸。显式写。
3. **json 不认识 dataclass**：`json.dumps(m)` 直接 TypeError，先 `asdict()`；`loads` 回来的是 dict 不是对象，用 `**` 解包还原（或 P7 pydantic）。
4. **忘 `raise_for_status()`**：500 的错误体被 `.json()` 当正常数据解析，静默脏数据。RestTemplate 肌肉记忆的人会忘。
5. **httpx 默认超时 5s**：LLM 响应经常超，显式 `timeout=60`；流式响应更大或按读超时单独设。
6. **async def 里放同步阻塞**（time.sleep / 同步 httpx / 大循环计算）：整个事件循环冻结，实测并发退化为串行。

### 动手任务 + 自测（10 分钟）

任务：

1. `history.py`：用 pathlib + json 把 P3 的 `ChatMessage` 列表落盘再读回，断言往返相等。
2. `weather.py`：httpx 取 `https://wttr.in/Beijing?format=j1`，提取 `current_condition[0]["temp_C"]` 打印——这是 P6"工具结果喂给 LLM"的原型。
3. async 版并发取北京 + 上海（`wttr.in/Shanghai?format=j1`）天气，对比串行耗时。

自测：

- `with open` ≈ Java 的什么？保证了什么？
- `json.dumps` 为什么必须加 `ensure_ascii=False`？
- `await` 和 `Thread.sleep` 的本质区别？为什么后者会杀死并发？
- 调 LLM 为什么必须显式调大 timeout？

---

## 第 5 阶段（第 5 小时）：NumPy 必学 / Pandas 选学

### 5.1 为什么是 NumPy【必学，5 分钟】

embedding 就是一个 float 数组（向量），RAG 的核心动作是"算向量相似度"。用 list 算要写循环，NumPy 一行搞定且底层是 C——**类比：`double[]` + 整数组运算符 + JNI 原生数学库的速度，但零胶水代码**。Java 没有直接对应物，把它当"数组版 Stream"学。

### 5.2 ndarray 基础【必学，约 20 分钟】

```python
import numpy as np

a = np.array([1.0, 2.0, 3.0])     # ≈ double[] 字面量
a.shape                            # (3,) ≈ length；多维时是 (行, 列)
a.dtype                            # float64 ≈ 组件类型

m = np.array([[1, 2, 3], [4, 5, 6]])   # ≈ double[][]
m[:, 1]        # 取第 1 列 [2 5]！Java 要写循环；: 表示"这一维全要"
m[0, 2]        # ≈ m[0][2]
```

整数组运算 ≈ 不用写 lambda 的 `map` ✅：

```python
b = np.array([4.0, 5.0, 6.0])
a + b      # [5. 7. 9.]   逐元素加
a * b      # [4. 10. 18.] 逐元素乘（注意！不是矩阵乘）
a * 2      # [2. 4. 6.]   标量广播到每个元素
a @ b      # 32.0         点积/矩阵乘用 @
```

聚合 ≈ Stream 终结操作 ✅：

```python
a.sum()     # 6.0  ≈ mapToDouble().sum()
a.mean()    # 2.0  ≈ averagingDouble
a.argmax()  # 2    最大值的下标 —— RAG 选 top-1 就靠它
```

布尔索引 ≈ filter，不用 lambda ✅：

```python
scores = np.array([0.9, 0.2, 0.8])
scores[scores > 0.5]        # [0.9 0.8]
np.argsort(scores)[::-1]    # [0 2 1] 按值降序的"下标"；[::-1] 是反转切片
```

【必学一行】真实 embedding 常用 `dtype=np.float32`（省一半内存）：`rng.random(384).astype(np.float32)`。

### 5.3 手写余弦相似度【必学，约 15 分钟】——RAG 的数学地基

公式：`cos(a,b) = a·b / (|a|×|b|)`。生活类比：两支箭头方向越接近，语义越像。**类比边界**：余弦只看方向不看长度（所以忽略文档长短），而"方向能否代表语义"完全取决于 embedding 模型的质量——余弦本身不懂语义。

```python
def cosine(x: np.ndarray, y: np.ndarray) -> float:
    return float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))
    # @ = 点积 ≈ 手写 sum(x[i]*y[i])；norm = L2 范数 ≈ sqrt(平方和)
```

**批量版：一个 query 对全部 chunks 一次算完**——这就是 P6 RAG 检索的核心三行 ✅：

```python
query = np.array([1.0, 0.0, 1.0])
docs = np.array([
    [1.0, 0.0, 1.0],    # chunk0: RAG 定义
    [0.0, 1.0, 0.0],    # chunk1: 无关内容
    [0.9, 0.1, 0.8],    # chunk2: RAG 流程
])
sims = docs @ query / (np.linalg.norm(docs, axis=1) * np.linalg.norm(query))
# 实测：[1.0, 0.0, 0.99484975]
top2 = np.argsort(sims)[::-1][:2]    # 实测：[0 2]
```

`axis=1` ≈ "沿每一行各算一个范数"——axis 就是"选哪个维度做循环"，0 是跨行（按列），1 是跨列（按行）。P6 会把这里的手造向量换成真实 embedding，代码形状一模一样。

### 5.4 Pandas【整节选学，10 分钟混脸熟】

类比：**内存里的 SQL 表**（≈ `List<Map<String,Object>>` + groupBy）。AI 应用里它出现在：看评测数据集、清洗 CSV 语料、统计调用日志。最小 RAG 路径用不到，但你会在别人的代码里天天见到这五招：

```python
import pandas as pd

df = pd.DataFrame([{"query": "什么是RAG", "score": 0.9},
                   {"query": "天气", "score": 0.3},
                   {"query": "RAG流程", "score": 0.8}])
df["score"]                                  # SELECT score
df[df["score"] > 0.5]                        # WHERE score > 0.5（实测返回 RAG 两行）
df["score"].mean()                           # AVG(score) → 0.667
df.sort_values("score", ascending=False).head(2)   # ORDER BY score DESC LIMIT 2
pd.read_csv("eval.csv")                      # 读 CSV 一行搞定
```

选型：AI **应用**开发 90% 是 NumPy；Pandas 在"看数据/做评测集"时才上场；训练/数据工程岗才需要深学【超出本课】。

### 5.5 本阶段常见坑（全部实测复现）

1. **`*` 是逐元素乘，`@` 才是点积**：余弦写成 `a*b` 不报错、结果静默错。最危险的一个。
2. **切片是视图不是拷贝**：和 list 正好相反！`v = arr[1:3]; v[0]=99` 实测把原数组改成 `[1 99 3 4]`。要独立副本写 `arr[1:3].copy()`。
3. **int 数组静默截断**：`xi = np.zeros(3, dtype=int); xi[0]=0.9` → 实测 `[0 0 0]`，≈ 强转 (int) 不报错。存 embedding 永远 float。
4. **shape 广播静默扩维**：`(3,) * (3,1)` 实测得到 `(3,3)` 矩阵。结果不对先 `print(x.shape)`。
5. **argsort 返回下标不是值**；降序要 `[::-1]`。
6. **浮点精度**：实测 `cosine(v,v)` float64 得 `0.9999999999999998`，float32 得 `1.0000001`。断言别写 `== 1.0`，用近似比较（P7 的 `pytest.approx`）。

### 动手任务 + 自测（10 分钟）

任务：

1. `similarity.py`：默写 `cosine` + 批量版，对文中 3 个 chunk 算 top-2，答案应为 `[0 2]`。
2. 用 `np.random.default_rng(42).random(384)` 造一个"假 embedding"，验证自相似 ≈ 1，并解释为什么不精确等于 1。
3. 【选学】把 P4 的天气结果存成 CSV，用 pandas 读回并过滤。

自测：

- `a*b` 和 `a@b` 各是什么？余弦公式用哪个？
- NumPy 切片和 list 切片的本质区别？
- `axis=1` 是什么意思？
- 为什么不能断言 `cosine(v,v) == 1.0`？

---

## 第 6 阶段（第 6 小时）：LLM API 调用 + embedding + 最小 RAG

### 6.1 OpenAI 兼容协议与 SDK【必学，约 15 分钟】

**类比：OpenAI SDK ≈ JDBC API**。各家厂商（通义 / DeepSeek / OpenAI / 月之暗面）≈ 数据库驱动，只要支持"OpenAI 兼容协议"，同一套代码换 `base_url` + `model` + `api_key` 就能跑。这是 AI 应用开发最重要的选型事实：**先按兼容协议写，厂商可插拔**。

| Java | Python LLM 调用 |
|---|---|
| JDBC API | `openai` SDK |
| MySQL/PG 驱动 | 通义 / DeepSeek / OpenAI 兼容端点 |
| JDBC URL | `base_url` |
| 方言 | `model` 参数 |
| 强类型 ResultSet DTO | `resp.choices[0].message.content`（SDK 内部就是 pydantic） |

真实调用 🔑（接线已验证，网络调用需 Key）：

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["LLM_API_KEY"],   # 密钥走环境变量，绝不写进代码/文档/git
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 通义；DeepSeek 换 https://api.deepseek.com/v1
)

resp = client.chat.completions.create(
    model="qwen-plus",
    messages=[{"role": "user", "content": "用一句话解释RAG"}],
    temperature=0.7,
    max_tokens=512,
)
print(resp.choices[0].message.content)
```

流式输出【选学，但产品里常见】🔑：`stream=True` 后迭代 chunk，≈ SSE / `Flux<String>`：

```python
stream = client.chat.completions.create(model="qwen-plus", messages=messages, stream=True)
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

错误处理：`openai.RateLimitError` / `openai.APITimeoutError` 都是普通异常，直接套 P3 的 `@retry`（生产配指数退避）。

### 6.2 密钥管理 + mock 双实现【必学，约 10 分钟】

规则：**Key 只从环境变量读**（`os.environ`），代码/文档/git 里永远不出现真实 Key。配合 P3 鸭子类型，写"有 Key 走真实、没 Key 走 mock"的双实现，全天练习不阻塞 ✅：

```python
class FakeLLM:
    def chat(self, messages: list[dict]) -> str:
        return f"[mock] 已收到 {len(messages)} 条消息，最后一条：{messages[-1]['content'][:40]}..."

class OpenAILLM:
    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(
            api_key=os.environ["LLM_API_KEY"],
            base_url=os.environ.get("LLM_BASE_URL",
                                    "https://dashscope.aliyuncs.com/compatible-mode/v1"),
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
```

两个类没有共同基类——鸭子类型，`llm.chat(messages)` 对两者都成立。测试里 mock ≈ Mockito，但零框架。

### 6.3 embedding【必学，约 10 分钟】

概念：文本 → 定长 float 向量；语义相近 → 方向相近（P5 余弦的用武之地）。

真实调用 🔑：

```python
resp = client.embeddings.create(model="text-embedding-v3", input=["文本1", "文本2"])
vecs = np.array([d.embedding for d in resp.data])   # shape (2, 1024)
```

模型选型（以厂商当前文档为准）：通义 `text-embedding-v3`（1024 维）、OpenAI `text-embedding-3-small`（1536 维）。维度和模型绑定，**换模型必须全量重建索引**。

无 Key 演练用 mock embedding ✅（字符哈希，确定性）：

```python
def mock_embed(text: str, dim: int = 64) -> np.ndarray:
    v = np.zeros(dim)
    for ch in text:
        v[ord(ch) % dim] += 1.0
    return v
```

**边界（必须清楚）**：字符哈希只度量"字符重叠"，不是语义。它只用于跑通管道形状；真实语义效果必须换真实 embedding 模型，代码形状完全不变。

### 6.4 最小 RAG【必学，约 20 分钟】——全天核心

RAG = Retrieval-Augmented Generation。生活类比：**开卷考试**——LLM 是考生，检索是翻教材找到相关段落，带着段落答题。为什么用它：缓解幻觉、注入私有知识、比微调便宜。**边界**：检索质量决定上限，查不到就答不对（garbage in, garbage out）。

管道五步：切块 → embedding → 存索引（numpy 矩阵）→ 检索 top-k → 塞进 prompt。

`rag.py` 核心代码 ✅（实测，mock 模式）。完整文件 = 文件头 `import os` + `import numpy as np` + 6.2 的双实现 + 6.3 的 `mock_embed` + 本节代码：

```python
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
    top = np.argsort(sims)[::-1][:k]        # +1e-10 防零向量除零
    return [(chunks[i], float(sims[i])) for i in top]

def rag_answer(question: str, llm, embed, chunks, index) -> tuple[str, list]:
    hits = retrieve(question, chunks, index, embed, k=2)
    context = "\n".join(f"[{i + 1}] {c}" for i, (c, _) in enumerate(hits))
    messages = [
        {"role": "system", "content": "只根据提供的资料回答；资料不足就说不知道。"},
        {"role": "user", "content": f"资料：\n{context}\n\n问题：{question}"},
    ]
    return llm.chat(messages), hits
```

实测输出（mock 模式，检索排序正确）：

```
Q: 什么是RAG
  hit 0.408: RAG（检索增强生成）先从知识库检索相关片段，再交...
  hit 0.235: FastAPI 是 Python 的异步 Web ...
Q: 怎么衡量语义相似度
  hit 0.451: embedding 把文本映射为定长浮点向量，语义...
  hit 0.296: RAG（检索增强生成）先从知识库检索相关片段，再交...
```

切块【必学概念，实现选学】：demo 用现成短句；真实文档要切。最简定长滑窗：

```python
def split_text(text: str, size: int = 200, overlap: int = 50) -> list[str]:
    return [text[i:i + size] for i in range(0, len(text), size - overlap)]
```

overlap 防止句子被拦腰切断丢语义；真实项目按段落/标题切更好。

### 6.5 本阶段常见坑

1. **Key 硬编码**：进代码/文档/git 就泄露。只走 `os.environ`；`.env` 文件进 `.gitignore`。
2. **把 mock 当语义**：字符哈希的"相似度"只是字符重叠，演示完必须换真实模型再评估效果。
3. **零向量除零**：空文本 embedding 是全零，norm=0。分母加 `1e-10`。
4. **context 塞太多**：top-k 过大/chunk 过长 → token 爆炸 + 模型"中间遗忘"。k 取 2~5，chunk 200~500 字起步。
5. **资料是指令吗？不是**：塞进 prompt 的检索内容是**数据**，system prompt 明确"只根据资料回答"。警惕资料里夹带"忽略以上指令"类注入文本。
6. **换 embedding 模型忘重建索引**：维度/语义空间都变了，旧向量全废。

### 动手任务 + 自测（10 分钟）

任务：

1. 把 `rag.py` 敲进项目跑通（无 Key 即 mock 模式），确认两个 query 的 top-1 命中正确。
2. 给 KB 加一条你自己的知识，验证能被检索到。
3. 有 Key：`export LLM_API_KEY=...` 后重跑，对比真实回答与 mock。

自测：

- OpenAI 兼容协议为什么像 JDBC？换厂商要改哪三个东西？
- RAG 五步管道是什么？余弦在哪一步？
- mock embedding 的边界是什么？
- 为什么 system prompt 要写"只根据资料回答"？

---

## 第 7 阶段（第 7 小时）：FastAPI + pytest

### 7.1 FastAPI ≈ Spring Boot【必学，约 25 分钟】

| Spring Boot | FastAPI |
|---|---|
| `@RestController` | `app = FastAPI()` |
| `@PostMapping("/chat")` | `@app.post("/chat")` |
| `@RequestBody @Valid` DTO | pydantic `BaseModel` 参数 |
| `@NotBlank` / `@Size` | `Field(min_length=1, max_length=2000)` |
| 内嵌 Tomcat | uvicorn |
| SpringDoc / Swagger | 自带 `/docs`（零配置） |
| `@Autowired` | `Depends()`【选学，认识即可】 |
| `application.yml` | 环境变量 / `.env`【选学】 |

**pydantic = DTO + Bean Validation + Jackson 三合一**：声明模型即完成序列化与校验，校验失败自动返回 422 ≈ `MethodArgumentNotValidException`。

`chat_app.py` ✅：

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="AI Quickstart")

class FakeLLM:
    def chat(self, messages: list[dict]) -> str:
        return f"[mock] 收到问题：{messages[-1]['content'][:40]}"

llm = FakeLLM()

class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)      # ≈ @NotBlank @Size
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)   # ≈ @DecimalMin/@DecimalMax

class ChatResponse(BaseModel):
    answer: str
    model: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    answer = llm.chat([{"role": "user", "content": req.question}])
    return ChatResponse(answer=answer, model="mock")
```

运行 ≈ `spring-boot:run` + devtools 热重载：

```bash
uv run uvicorn chat_app:app --reload --port 8000
# 浏览器开 http://127.0.0.1:8000/docs —— 交互式 Swagger，直接点着玩
curl -s http://127.0.0.1:8000/chat -H 'Content-Type: application/json' \
     -d '{"question":"什么是RAG"}'
```

**async def vs def（P4 规则落地）**：`async def` 上事件循环，里面别放阻塞 IO；同步函数写 `def`，FastAPI 自动丢线程池 ≈ `@Async`。本例 FakeLLM 无 IO 所以 async 安全；P8 调真实同步 SDK 时改用 `def`。

### 7.2 pytest ≈ JUnit【必学，约 25 分钟】

| JUnit | pytest |
|---|---|
| `@Test` | `def test_xxx():`（文件名 `test_*.py` 自动发现） |
| `Assertions.assertEquals` | 裸 `assert x == y` |
| `@BeforeEach` | `@pytest.fixture` |
| `@ParameterizedTest` | `@pytest.mark.parametrize` |
| `assertEquals(a, b, delta)` | `pytest.approx` |
| `Mockito.mock` | 鸭子类型 fake / `monkeypatch` |
| `MockMvc` | `fastapi.testclient.TestClient` |

`test_chat_app.py` ✅（实测 9 passed，含 P8 的 3 个）：

```python
import numpy as np
import pytest
from fastapi.testclient import TestClient

from chat_app import app
from rag import cosine

client = TestClient(app)          # ≈ MockMvc，不起真实端口，直接打 ASGI 应用

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
    assert cosine(v, v) == pytest.approx(1.0)   # P5 浮点坑的官方解法
```

运行 ≈ `mvn test`：

```bash
uv run pytest -q
# 实测：9 passed in 0.69s
```

### 7.3 本阶段常见坑

1. **async def 里调同步 SDK**：真实 LLM 调用是阻塞 IO，会冻结事件循环（P4）。用 `def` 端点或 `AsyncOpenAI`【选学】。
2. **422 不是 bug**：pydantic 校验失败的标准响应，前端要按 422 处理参数错误。
3. **TestClient 依赖 httpx**：`uv add httpx` 别忘了（P1 已装）。
4. **`--reload` 只用于开发**：生产 `uvicorn app:app --workers 4` ≈ 多实例部署。

### 动手任务 + 自测（10 分钟）

任务：

1. 跑起 `chat_app.py`，在 `/docs` 里手动发一次请求、故意发空 question 看 422。
2. 默写 3 个测试：正常、空 question、temperature 越界。
3. 给 P5 的 `cosine` 补一个 `pytest.approx` 测试。

自测：

- pydantic 一个库干了 Java 哪三个组件的活？
- `TestClient` ≈ Spring 的什么？要起真实端口吗？
- 同步 LLM SDK 应该放 `async def` 还是 `def` 端点？为什么？

---

## 第 8 阶段（第 8 小时）：综合项目 + 坑汇总 + 自测清单

### 8.1 综合项目：FastAPI + LLM + RAG 问答服务【必学】

把全天积木拼起来：`POST /ask` → 检索 top-k → 组 prompt → LLM（真实/mock 自动切换）→ 返回 **answer + sources**（RAG 回答必须可溯源）。

`app.py` ✅（实测：TestClient + 真实 uvicorn + curl 全通过）：

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

from rag import KB, build_index, get_llm, mock_embed, retrieve

app = FastAPI(title="Java→AI 最小 RAG 服务")

llm = get_llm()                          # 有 LLM_API_KEY 走真实，否则 mock
index = build_index(KB, mock_embed)      # 启动时建索引；大知识库要持久化/向量库（见 8.4）

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
def ask(req: AskRequest) -> AskResponse:        # 注意：def 不是 async def！
    hits = retrieve(req.question, KB, index, mock_embed, k=req.top_k)
    context = "\n".join(f"[{i + 1}] {c}" for i, (c, _) in enumerate(hits))
    messages = [
        {"role": "system", "content": "只根据提供的资料回答；资料不足就说不知道。"},
        {"role": "user", "content": f"资料：\n{context}\n\n问题：{req.question}"},
    ]
    answer = llm.chat(messages)                 # 同步 SDK 是阻塞 IO → def 端点，FastAPI 丢线程池
    return AskResponse(
        answer=answer,
        sources=[Source(text=c, score=s) for c, s in hits],
    )

@app.get("/health")
def health():
    return {"status": "ok", "llm": type(llm).__name__}
```

`test_app.py` ✅：

```python
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
```

运行与实测：

```bash
uv run uvicorn app:app --reload --port 8000
curl -s http://127.0.0.1:8000/ask -H 'Content-Type: application/json' \
     -d '{"question":"什么是RAG"}'
```

curl 实测返回（mock 模式）：

```json
{
  "answer": "[mock] 已收到 2 条消息，最后一条：资料：\n[1] RAG（检索增强生成）先从知识库检索相关片段，再交给大模型生成回...",
  "sources": [
    {"text": "RAG（检索增强生成）先从知识库检索相关片段，再交给大模型生成回答，能缓解幻觉并注入私有知识。", "score": 0.408},
    {"text": "FastAPI 是 Python 的异步 Web 框架，配合 pydantic 做请求校验，自带 /docs 交互式文档。", "score": 0.235}
  ]
}
```

`/health` → `{"status":"ok","llm":"FakeLLM"}`；`/docs` → 200；空 question → 422。`uv run pytest -q` → 9 passed。

切换真实 LLM 🔑：

```bash
export LLM_API_KEY=你的Key
export LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1   # 或 DeepSeek/OpenAI
export LLM_MODEL=qwen-plus
uv run uvicorn app:app --port 8000    # /health 会显示 OpenAILLM
```

设计决策回顾（都是前面学过的规则落地）：

- `def ask` 而非 `async def`：同步 OpenAI SDK 是阻塞 IO，P4 规则 → 线程池。
- 返回 sources：可溯源是 RAG 产品的底线。
- 索引启动时建：4 条 KB 无所谓；真实规模见 8.4。

### 8.2 全天常见坑汇总表

| # | 阶段 | 坑 | 正确姿势 |
|---|---|---|---|
| 1 | P1 | 直接 `python xxx.py` 用到系统老解释器 | 永远 `uv run` |
| 2 | P1 | Tab/空格混用 | 统一 4 空格 |
| 3 | P1 | `if not x` 把 0/"" 当空 | 数值判空 `is None` 显式写 |
| 4 | P1 | `is` 比值 | `==` 比值，`is` 只用于 None |
| 5 | P1 | 指望编译器兜底 | 标注 + pyright + pytest |
| 6 | P2 | `msg[缺失键]` 抛 KeyError | `.get()` |
| 7 | P2 | 以为标注会校验 | 边界校验靠 pydantic |
| 8 | P2 | `[[]] * 3` 共享引用 | `[[] for _ in range(3)]` |
| 9 | P2 | `b = a` 当拷贝 | `a[:]` / `a.copy()` |
| 10 | P2 | set 去重丢顺序 | `dict.fromkeys` 保序 |
| 11 | P3 | 可变默认参数跨调用共享 | `None` 哨兵 |
| 12 | P3 | 写重载被静默覆盖 | 默认参数 |
| 13 | P3 | 实例方法忘 self | 第一个参数永远 self |
| 14 | P3 | 类属性可变共享 ≈ static | 实例数据放 `__init__` |
| 15 | P3 | 装饰器忘 `@wraps` | 固定加 |
| 16 | P4 | dumps 中文变转义 | `ensure_ascii=False` |
| 17 | P4 | 不写 encoding | 显式 `utf-8` |
| 18 | P4 | json 不认识 dataclass | `asdict()` / `**` 解包 |
| 19 | P4 | 忘 `raise_for_status()` | 固定加 |
| 20 | P4 | httpx 默认 5s 超时 | LLM 调用 `timeout=60` |
| 21 | P4 | async 里同步阻塞 | await 异步库 |
| 22 | P5 | `*` 当点积 | 点积用 `@` |
| 23 | P5 | numpy 切片当拷贝 | 视图！要 `.copy()` |
| 24 | P5 | int 数组存小数被截断 | float dtype |
| 25 | P5 | 广播静默扩维 | 先 `print(shape)` |
| 26 | P5 | 浮点 `== 1.0` | `pytest.approx` |
| 27 | P6 | Key 硬编码 | 只走环境变量 |
| 28 | P6 | mock embedding 当语义 | 真实模型再评估 |
| 29 | P6 | 零向量除零 | 分母 `+1e-10` |
| 30 | P6 | context 塞太多 | k=2~5，chunk 200~500 字 |
| 31 | P6 | 换 embedding 模型不重建索引 | 全量重建 |
| 32 | P7 | async def 调同步 SDK | `def` 端点 / AsyncOpenAI |
| 33 | P7 | `--reload` 上生产 | `--workers N` |
| 34 | P8 | RAG 不返回 sources | answer + sources 一起回 |

### 8.3 自测清单（能全勾上 = 达标）

环境与语法（P1）：

- [ ] 能解释 .venv 为什么存在，`uv run` 做了哪两件事
- [ ] 能说清 `==`/`is` 与 Java 的对应关系
- [ ] 能解释真值判断为什么会误伤 0
- [ ] 项目里所有运行都走 `uv run`

类型与容器（P2）：

- [ ] 能写 `list[dict[str, str]]`、`str | None` 标注并解释运行时不强制
- [ ] 能默写 filter+map 推导式并翻译成 Stream
- [ ] 能解释 `[[]] * 3` 为什么错
- [ ] `token_stats` 练习输出 (15, 3.75)

函数与类（P3）：

- [ ] 能默写 `@retry`（含 @wraps）
- [ ] 能解释装饰器与 Java 注解的本质区别
- [ ] 能写 dataclass + `field(default_factory=list)` + `asdict`
- [ ] 能解释可变默认参数坑的修法

IO 与并发（P4）：

- [ ] 对话落盘/读回往返相等
- [ ] httpx 取到 wttr.in 温度并打印
- [ ] 能解释 await vs Thread.sleep，gather 实测快于串行
- [ ] 记得 `ensure_ascii=False` 和 `raise_for_status()`

向量（P5）：

- [ ] 手写 cosine 批量版 top-2 = [0 2]
- [ ] 能解释 `*` vs `@`、视图 vs 拷贝
- [ ] 能解释自相似为什么不精确等于 1

LLM 与 RAG（P6）：

- [ ] 能解释 OpenAI 兼容协议 ≈ JDBC，换厂商改哪三样
- [ ] rag.py 两个 query top-1 命中正确
- [ ] 能背出 RAG 五步管道
- [ ] 能解释 mock embedding 的边界

服务与测试（P7）：

- [ ] /docs 里手动调通 /chat，空 question 得 422
- [ ] 默写 3 个 pytest 用例全过
- [ ] 能解释 pydantic 三合一、TestClient ≈ MockMvc

综合（P8）：

- [ ] uvicorn 起服务，curl /ask 拿到 answer + sources
- [ ] `uv run pytest -q` 全绿
- [ ] （有 Key）切真实 LLM 后 /health 显示 OpenAILLM 且回答真实

### 8.4 下一步选型地图（1 天之后往哪走）

| 方向 | 最小选择 | 何时升级 |
|---|---|---|
| 流式输出 | SSE + `AsyncOpenAI` stream | 前端要打字机效果时 |
| 向量存储 | numpy 手写（本课） | 万级 chunk 以上 → Chroma（嵌入式）/ pgvector（复用 PG） |
| 编排框架 | 手写（本课，最透明） | 多步复杂编排再上 LangChain / LlamaIndex |
| 评估 | pytest + 自制评测集 | 系统化评估 → ragas |
| 部署 | uvicorn --workers + Docker | 异步深水区：TaskGroup / 限流信号量 |

---

## 附录：验证环境与方法

- 验证环境：macOS（arm64）/ Python 3.12（uv 管理）/ uv 0.7.19。
- 标注 ✅ 的代码均在上述环境实际运行，文中输出为真实运行结果。
- 标注 🔑 的代码（真实 LLM/embedding 网络调用）验证了客户端构造与接线，未消耗真实 Key 发起调用。
- 沙箱/CI 若注入畸形 `NO_PROXY`（如含 `[::1]`）会导致 httpx 解析崩溃：`trust_env=False` 或清理环境变量。
- 依赖清单：`uv add httpx openai fastapi "uvicorn[standard]" numpy pandas pytest`。