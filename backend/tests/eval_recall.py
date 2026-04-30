"""
检索召回率评估脚本

使用方法：
1. 在 test_cases 里填写测试问题和对应的相关 chunk 关键词
2. 在 backend/ 目录下运行: python -m tests.eval_recall
"""

import sys
from pathlib import Path

# 确保能导入 src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ai.vectorstores.chroma_store import get_vectorstore


# ==================== 测试用例 ====================
# 每条: question=问题, keywords=相关 chunk 中必须包含的关键词（任一匹配即算命中）
# 请根据你实际上传的笔记内容来编写测试用例
test_cases: list[dict] = [
    # --- 英语 ---
    {
        "question": "倒装句的否定词开头都有哪些？",
        "keywords": ["Never"],
    },
    {
        "question": "写作高分开头句型（众所周知...）怎么写？",
        "keywords": ["acknowledged"],
    },
    {
        "question": "主旨题题型技巧",
        "keywords": ["每段首句"],
    },
    # --- 历史 ---
    {
        "question": "司马迁《史记》是什么体裁？",
        "keywords": ["纪传体"],
    },
    {
        "question": "太平天国的失败原因",
        "keywords": ["局限性"],
    },
    {
        "question": "五四运动的导火索是上面",
        "keywords": ["巴黎和会"],
    },
    # --- 数学 ---
    {
        "question": "极限的有界性具体是怎么说的？",
        "keywords": [ "去心邻域"],
    },
    {
        "question": "第一类间断点有哪两种类型？",
        "keywords": [ "跳跃间断点"],
    },
    # --- 语文 ---
    {
        "question": "初唐四杰都指的是谁？",
        "keywords": ["王勃"],
    },
    {
        "question": "我国最长叙事诗是什么？",
        "keywords": ["《孔雀东南飞》"],
    },
    # --- 书法 ---
    {
        "question": "毛笔按照毫料可以分为哪几种？",
        "keywords": ["兼毫"],
    },
]


def eval_recall(top_k: int = 8) -> None:
    vs = get_vectorstore()

    total_cases = len(test_cases)
    total_relevant = 0
    total_hit = 0

    print(f"\n{'='*60}")
    print(f"  检索召回率评估  |  top_k={top_k}  |  测试集={total_cases} 条")
    print(f"{'='*60}\n")

    for i, case in enumerate(test_cases, 1):
        question = case["question"]
        keywords = case["keywords"]

        docs = vs.similarity_search(question, k=top_k)
        retrieved_texts = [d.page_content for d in docs]

        # 检查：至少有一个关键词出现在检索结果中
        matched_keywords = []
        for kw in keywords:
            if any(kw in text for text in retrieved_texts):
                matched_keywords.append(kw)

        hit = len(matched_keywords) > 0
        total_relevant += 1
        if hit:
            total_hit += 1

        status = "✓ 命中" if hit else "✗ 未命中"
        print(f"  [{i}/{total_cases}] {status}  Q: {question}")
        if hit:
            print(f"         匹配关键词: {matched_keywords}")
        else:
            print(f"         关键词: {keywords} 均未匹配")
            # 打印 top-1 内容帮助调试
            if retrieved_texts:
                preview = retrieved_texts[0][:80].replace("\n", " ")
                print(f"         top-1 内容: {preview}...")
        print()

    recall = total_hit / total_relevant if total_relevant > 0 else 0
    print(f"{'='*60}")
    print(f"  Recall@{top_k} = {total_hit}/{total_relevant} = {recall:.1%}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    eval_recall()
