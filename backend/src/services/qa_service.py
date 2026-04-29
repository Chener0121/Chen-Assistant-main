from langchain_core.messages import HumanMessage

from src.ai.agents.qa_agent import qa_agent
from src.ai.vectorstores import chroma_store


def ask(question: str, thread_id: str = "default") -> dict:
    """智能问答：调用 Agent 检索笔记 + 多轮对话 + 结构化输出"""
    response = qa_agent.invoke(
        {"messages": [HumanMessage(content=question)]},
        config={"configurable": {"thread_id": thread_id}},
    )

    # 结构化输出已自动解析为 QAResult
    result = response["structured_response"].model_dump()

    # 保存问答记录，用于薄弱知识点分析
    chroma_store.save_qa_record(question, result)

    return result
