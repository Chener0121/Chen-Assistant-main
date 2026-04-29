from src.ai.chains.qa_chain import qa_chain
from src.ai.tools.search import _search
from src.ai.vectorstores import chroma_store
from src.services import analytics_service

# 薄弱点查询触发关键词
_WEAK_POINT_KEYWORDS = ["薄弱", "弱点", "学得不好", "需要复习", "掌握不好", "不熟练"]


def _build_context(question: str) -> str:
    """根据问题内容构建上下文：笔记检索 + 按需查薄弱点"""
    parts = []

    # 笔记检索（每次都做）
    results = _search(question)
    if results:
        note_parts = [f"[学科：{r['subject']}]\n{r['content']}" for r in results]
        parts.append("【用户学习笔记】\n" + "\n\n".join(note_parts))
    else:
        parts.append("（未找到相关笔记内容）")

    # 薄弱点查询（关键词触发）
    if any(kw in question for kw in _WEAK_POINT_KEYWORDS):
        weak_data = analytics_service.list_weak_points()
        if weak_data:
            weak_parts = []
            for w in weak_data:
                weak_parts.append(
                    f"- {w['knowledge_point']}（{w['subject']}，等级：{w['level']}，提问{w['ask_count']}次）"
                )
            parts.append("【用户薄弱知识点】\n" + "\n".join(weak_parts))
        else:
            parts.append("【用户薄弱知识点】\n暂无薄弱点记录")

    return "\n\n".join(parts)


def ask(question: str, thread_id: str = "default") -> dict:
    """Chain 模式：代码判断意图 → 构建上下文 → 1 次 LLM 调用 → 结构化输出"""
    context = _build_context(question)
    result = qa_chain.invoke({"context": context, "question": question})
    result_dict = result.model_dump()

    is_learning = bool(result_dict.get("subject") or result_dict.get("knowledge_points"))
    if is_learning:
        chroma_store.save_qa_record(question, result_dict)

    return result_dict
