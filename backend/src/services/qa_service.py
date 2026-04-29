from langchain_core.messages import HumanMessage

from src.ai.agents.qa_agent import qa_agent
from src.ai.vectorstores import chroma_store


def ask(question: str, thread_id: str = "default") -> dict:
    """智能问答：调用 Agent 检索笔记 + 多轮对话 + 结构化输出"""
    response = qa_agent.invoke(
        {"messages": [HumanMessage(content=question)]},
        config={"configurable": {"thread_id": thread_id}},
    )

    result = response["structured_response"].model_dump()

    # 只有学习相关问题（有知识点或学科）才保存 QA 记录
    is_learning = bool(result.get("subject") or result.get("knowledge_points"))
    if is_learning:
        chroma_store.save_qa_record(question, result)

    return result
