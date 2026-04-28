import chromadb

from src.core.config import settings

client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
