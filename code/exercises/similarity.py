import numpy as np


def cosine(x: np.ndarray, y: np.ndarray) -> float:
    return float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))


def top_k(query: np.ndarray, docs: np.ndarray, k: int = 2) -> np.ndarray:
    sims = docs @ query / (np.linalg.norm(docs, axis=1) * np.linalg.norm(query) + 1e-10)
    return np.argsort(sims)[::-1][:k]


if __name__ == "__main__":
    query = np.array([1.0, 0.0, 1.0])
    docs = np.array([[1.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.9, 0.1, 0.8]])
    print(top_k(query, docs))   # [0 2]
    rng = np.random.default_rng(42)
    v = rng.random(384).astype(np.float32)
    print("self-cos:", cosine(v, v))   # ≈1，float32 精度