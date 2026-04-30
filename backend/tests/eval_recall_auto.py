"""
自动检索召回率评估：从 Chroma 中随机采样 chunk，用 LLM 生成问题，再验证检索是否命中。

使用方法：
  cd backend
  uv run python -m tests.eval_recall_auto
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ai.vectorstores.chroma_store import get_vectorstore
from src.core.llm_client import llm


NUM_CASES = 42  # 生成测试用例数量
TOP_K = 8


def pick_keyword(text: str) -> str:
    """让 LLM 从 chunk 中挑一个最具辨识度的关键词"""
    prompt = (
        "从以下文本中挑出一个最能代表核心知识点的关键词或短语（2-6个字），只输出这个词，不要解释。\n\n"
        + text[:500]
    )
    resp = llm.invoke(prompt)
    return resp.content.strip().strip('"').strip("'").strip("「」")


def generate_question(chunk_text: str) -> str:
    """让 LLM 根据 chunk 内容生成一个自然语言问题"""
    prompt = (
        "根据以下学习笔记内容，生成一个学生会问的自然语言问题。"
        "问题不要直接包含笔记中的专有名词原文，要换一种说法来问。"
        "只输出问题本身，不要输出其他内容。\n\n"
        + chunk_text[:600]
    )
    resp = llm.invoke(prompt)
    return resp.content.strip()


def main() -> None:
    vs = get_vectorstore()

    # 拉取所有 chunk
    results = vs.get(include=["documents", "metadatas"])
    all_docs = results["documents"] or []
    all_metas = results["metadatas"] or []

    if len(all_docs) < NUM_CASES:
        print(f"Chroma 中只有 {len(all_docs)} 条 chunk，不足 {NUM_CASES} 条")
        return

    # 随机采样，尽量覆盖不同学科
    sampled = random.sample(list(range(len(all_docs))), NUM_CASES)

    test_cases: list[dict] = []
    print(f"正在生成 {NUM_CASES} 条测试用例...\n")

    for idx in sampled:
        text = all_docs[idx]
        if not text or len(text.strip()) < 30:
            continue

        keyword = pick_keyword(text)
        question = generate_question(text)

        test_cases.append({
            "question": question,
            "keyword": keyword,
            "chunk_preview": text[:80].replace("\n", " "),
        })
        print(f"  [{len(test_cases)}/{NUM_CASES}] Q: {question}")
        print(f"           关键词: {keyword}")
        print(f"           来源: {all_metas[idx].get('subject', '?')} - {text[:50]}...")
        print()

    # 跑检索评估
    print(f"\n{'='*60}")
    print(f"  检索召回率评估  |  top_k={TOP_K}  |  测试集={len(test_cases)} 条")
    print(f"{'='*60}\n")

    total_hit = 0
    for i, case in enumerate(test_cases, 1):
        docs = vs.similarity_search(case["question"], k=TOP_K)
        retrieved_texts = [d.page_content for d in docs]
        keyword = case["keyword"]

        hit = any(keyword in t for t in retrieved_texts)
        if hit:
            total_hit += 1

        status = "✓" if hit else "✗"
        print(f"  [{i}/{len(test_cases)}] {status}  {case['question'][:40]}  → 关键词: {keyword}")

    recall = total_hit / len(test_cases) if test_cases else 0
    print(f"\n{'='*60}")
    print(f"  Recall@{TOP_K} = {total_hit}/{len(test_cases)} = {recall:.1%}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
