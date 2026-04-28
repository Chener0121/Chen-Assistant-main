from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings

from src.config import settings

llm = init_chat_model(
    model="qwen-flash",
    model_provider="openai",
    api_key=settings.DASHSCOPE_API_KEY,
    base_url=settings.DASHSCOPE_BASE_URL,
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-v1",
    api_key=settings.DASHSCOPE_API_KEY,
    base_url=settings.DASHSCOPE_BASE_URL,
)
