from langchain.chat_models import init_chat_model
from langchain_community.embeddings import DashScopeEmbeddings

from src.core.config import settings

llm = init_chat_model(
    model="qwen-flash",
    model_provider="openai",
    api_key=settings.DASHSCOPE_API_KEY,
    base_url=settings.DASHSCOPE_BASE_URL,
)

# 使用阿里 DashScope 原生 Embedding
embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=settings.DASHSCOPE_API_KEY,
)
