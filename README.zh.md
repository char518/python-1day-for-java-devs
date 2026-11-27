# Java 后端 → AI 应用开发：Python 1 天 8 小时最小必要集

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Code: verified](https://img.shields.io/badge/code-verified-brightgreen.svg)](#验证)

**面向 10 年 Java 经验、Python 零基础的工程师：8 小时，从语法差异一路搭到一个能跑的 FastAPI + LLM + RAG 问答服务。**

目标不是"学会 Python"，而是更窄也更实用的三件事：**能读懂 AI 代码、能写 LLM 应用、能测试**。每个知识点都映射到 Java 对应物，每段代码都实际运行过并贴出真实输出，全天贯穿同一个案例。

📖 **[完整课程（中文）](course.zh.md)** · [HTML 阅读版](https://char518.github.io/python-1day-for-java-devs/) · [配套代码](code/) · [English](README.md)

## 适合谁

- 5 年以上 Java / 后端经验，Python 零基础
- 转向 AI **应用**开发（LLM API、RAG、Agent），不是模型训练
- 要最小必要集，不要 300 页语言 tour

## 差异化

- **Java 锚定**：Maven→uv、Lombok→`@dataclass`、Jackson→pydantic、OkHttp→httpx、Spring Boot→FastAPI、JUnit→pytest；肌肉记忆坑逐个点名（`==`/`is`、可变默认参数、NumPy 视图、阻塞事件循环）。
- **实测而非示意**：✅ = 在 Python 3.12 真实运行过的代码，输出为真实结果；🔑 = 需要真实 API Key 的路径，接线已验证、网络调用未执行，诚实标注。
- **无 Key 也能跑**：鸭子类型 mock LLM + mock embedding，整条 RAG 管道离线可跑；`export LLM_API_KEY=...` 即切换任意 OpenAI 兼容厂商（通义 / DeepSeek / OpenAI）——SDK 像 JDBC：同一套 API，驱动可插拔。
- **坑驱动**：全天 34 条常见坑汇总 + 29 项自测清单。

## 8 小时路线

| 小时 | 模块 | Java 类比 |
|---|---|---|
| 1 | 环境（uv）+ 语法差异 | JDK / Maven |
| 2 | 类型标注 + 数据结构 + 推导式 | 泛型 / Stream API |
| 3 | 函数、装饰器、类、dataclass | Lambda / AOP / Lombok |
| 4 | 文件 JSON、httpx、async/await | Jackson / OkHttp / CompletableFuture |
| 5 | NumPy（Pandas 选学） | "数组版 Stream" |
| 6 | LLM API、embedding、最小 RAG | JDBC 式兼容协议 |
| 7 | FastAPI + pytest | Spring Boot / JUnit |
| 8 | 综合项目：FastAPI + LLM + RAG 服务 | — |

## 快速开始（配套代码）

需要 [uv](https://docs.astral.sh/uv/)。无需 API Key，服务以 mock 模式启动。

```bash
cd code
uv sync                            # 锁定依赖；uv 自动准备 Python 3.12
uv run pytest -q                   # 9 个测试
uv run uvicorn app:app --reload    # 打开 http://127.0.0.1:8000/docs
```

```bash
curl -s http://127.0.0.1:8000/ask -H 'Content-Type: application/json' \
     -d '{"question":"什么是RAG"}'
# -> {"answer": "...", "sources": [{"text": "...", "score": 0.408}, ...]}
```

切换真实 LLM（任意 OpenAI 兼容厂商）：

```bash
export LLM_API_KEY=你的Key
export LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
export LLM_MODEL=qwen-plus
uv run uvicorn app:app             # /health 显示 OpenAILLM
```

## 仓库结构

```
course.zh.md        完整 8 小时课程（中文，主交付物）
docs/index.html     带样式 HTML 阅读版（GitHub Pages 在线版）
code/               已验证配套代码
  rag.py            embedding + 余弦检索 + 最小 RAG（mock/真实双实现）
  chat_app.py       P7：最小 FastAPI /chat 接口
  app.py            P8 综合项目：/ask 返回 answer + sources
  test_*.py         pytest 测试（TestClient ≈ MockMvc）
  pyproject.toml    锁定依赖（uv.lock）
```

## 验证

- 环境：macOS（arm64）/ Python 3.12（uv 管理）/ uv 0.7.19。
- ✅ 代码均实际运行，文中输出为真实结果。复现：`cd code && uv sync && uv run pytest -q`。
- 🔑 代码（真实 LLM/embedding 网络调用）：客户端构造与接线已验证，未发起付费调用；设置 `LLM_API_KEY` 即可自行运行。
- mock embedding 是字符哈希向量，只演练管道形状，**不代表语义**；真实检索效果需真实 embedding 模型（代码形状不变）。

## 许可证

[MIT](LICENSE)