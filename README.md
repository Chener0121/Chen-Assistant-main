# Chen-Assistant

基于上传的学习笔记，通过大模型 API 与 LangChain 实现知识抽取、检索及智能问答，结合 Chroma 向量库自动识别薄弱知识点并推送关联内容，辅助高效学习。

Here is a dream.

## 项目结构

```
Chen-Assistant/
└── backend/          # 后端服务（FastAPI + LangChain）
```

## 技术栈

- **Web 框架**：FastAPI
- **AI 框架**：LangChain 1.2
- **LLM**：阿里百炼（Qwen）
- **Embedding**：DashScope Embeddings
- **向量数据库**：Chroma（嵌入式）
- **文档解析**：PyPDFLoader、Docx2txtLoader

## 快速开始

```bash
cd backend
uv sync
python main.py
```

启动后访问 http://127.0.0.1:8000/docs 查看 API 文档。
