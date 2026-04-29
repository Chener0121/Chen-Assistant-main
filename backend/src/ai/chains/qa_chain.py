from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.ai.prompts.qa_prompt import QA_CHAIN_PROMPT
from src.core.llm_client import llm
from src.models.schemas import QAResult

prompt = ChatPromptTemplate.from_messages([
    ("system", QA_CHAIN_PROMPT),
    MessagesPlaceholder("history", optional=True),
    ("human", "{question}"),
])

qa_chain = prompt | llm.with_structured_output(QAResult)
