import chromadb

from src.config import settings

client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
