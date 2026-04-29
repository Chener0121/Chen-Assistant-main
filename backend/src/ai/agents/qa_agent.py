from langchain.agents import create_agent

from src.ai.tools.search import search_notes
from src.ai.tools.weak_points import query_weak_points
from src.ai.prompts.qa_prompt import QA_SYSTEM_PROMPT
from src.core.llm_client import llm
from src.models.schemas import QAResult

# 创建问答 Agent
qa_agent = create_agent(
    llm,
    tools=[search_notes, query_weak_points],
    system_prompt=QA_SYSTEM_PROMPT,
    response_format=QAResult,
)
