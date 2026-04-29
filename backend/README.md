# Backend

Chen-Assistant 后端服务，基于 FastAPI + LangChain Chain 构建。

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
├── main.py                      # FastAPI 应用入口
├── core/                        # 核心基础设施
│   ├── config.py                # 全局配置（.env）
│   ├── llm_client.py            # LLM + Embedding 初始化
│   ├── exceptions.py            # 全局异常处理
│   ├── middleware.py            # 中间件（CORS）
│   └── dependencies.py         # 通用依赖项
├── api/v1/endpoints/            # API 路由
│   ├── documents.py             # 文档上传与管理
│   ├── qa.py                    # 智能问答
│   ├── conversations.py         # 对话管理（摘要压缩）
│   ├── graph.py                 # 知识图谱
│   └── analytics.py             # 学习分析
├── services/                    # 业务逻辑层
│   ├── document_service.py     # 文档处理流水线
│   ├── qa_service.py           # 问答服务
│   ├── analytics_service.py    # 薄弱知识点分析
│   └── graph_service.py        # 知识图谱构建
├── models/
│   └── schemas.py               # Pydantic 模型
├── ai/                          # AI 核心模块
│   ├── chains/qa_chain.py      # Chain 定义（prompt | llm）
│   ├── tools/
│   │   └── search.py           # 笔记检索
│   ├── prompts/qa_prompt.py    # Prompt 模板
│   └── vectorstores/
│       └── chroma_store.py     # Chroma 向量库封装
└── utils/
    └── helpers.py
```

## 核心流程

### 文档上传

解析 → 切片 → chunk 级增量去重 → 向量化 → 入库

- 支持格式：PDF、DOCX
- 增量更新：只 embedding 变化的 chunk
- 自动学科识别：LLM 判断上传文档的学科

### 智能问答

代码判断意图 → 笔记检索 / 薄弱点查询 → 1 次 LLM 调用 → 结构化输出（学科、回答、知识点、纠错）

- 多轮对话记忆：前端传历史消息 + 摘要压缩（超过 20 条自动压缩旧消息），通过 `thread_id` 隔离会话
- 学科匹配：自动判断问题学科，过滤跨学科干扰
- 闲聊支持：非学习问题正常回答，不入库分析

### 薄弱知识点

基于问答记录自动分析，带时间衰减：

- 30 天内：保持等级
- 30-60 天：降一级
- 60 天以上：移除

等级判定：有纠错 → 高，笔记缺失 → 中，反复提问 → 低

## 配置

复制 `.env.template` 为 `.env`，填入 DashScope API Key：

```
DASHSCOPE_API_KEY=your-key-here
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```
