# Backend

Chen-Assistant 后端服务，基于 FastAPI + LangChain 构建。

## 启动

```bash
uv sync
python main.py
```

服务地址：http://127.0.0.1:8000
API 文档：http://127.0.0.1:8000/docs

## 项目结构

```
src/
├── main.py                 # FastAPI 应用入口
├── core/                   # 核心基础设施
│   ├── config.py           # 全局配置（.env）
│   ├── llm_client.py       # LLM + Embedding 初始化
│   ├── exceptions.py       # 全局异常处理
│   ├── middleware.py        # 中间件（CORS）
│   └── dependencies.py     # 通用依赖项
├── api/v1/endpoints/       # API 路由
│   ├── documents.py        # 文档上传与管理
│   ├── qa.py               # 智能问答
│   └── graph.py            # 知识图谱
├── services/               # 业务逻辑层
│   └── document_service.py # 文档处理流水线
├── models/                 # 数据模型
│   └── schemas.py          # Pydantic 模型
├── ai/vectorstores/        # 向量数据库
│   └── chroma_store.py     # Chroma 封装
└── repositories/           # 数据访问层
```

## 核心流程

文档上传后自动执行：解析 → 切片 → chunk 级增量去重 → 向量化 → 入库

- 支持格式：PDF、DOCX
- 增量更新：只 embedding 变化的 chunk
- 数据存储：`chroma_db/`（Chroma 持久化目录）

## 配置

复制 `.env.template` 为 `.env`，填入 DashScope API Key：

```
DASHSCOPE_API_KEY=your-key-here
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```
