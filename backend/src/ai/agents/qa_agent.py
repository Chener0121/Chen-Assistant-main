from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from src.ai.tools.search import search_notes
from src.ai.tools.weak_points import query_weak_points
from src.ai.tools.qa_history import query_qa_history
from src.ai.prompts.qa_prompt import QA_SYSTEM_PROMPT
from src.core.llm_client import llm
from src.models.schemas import QAResult

# 内存级别的记忆存储（服务重启后清空）
_memory = MemorySaver()

# 创建问答 Agent
qa_agent = create_agent(
    llm,
    tools=[search_notes, query_weak_points, query_qa_history],
    system_prompt=QA_SYSTEM_PROMPT,
    response_format=QAResult,
    checkpointer=_memory,
)
