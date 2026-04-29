# 🎓 知识图谱智学助手(Chen-Assistant)

基于上传的学习笔记，通过大模型 API 与 LangChain Agent 实现知识抽取、检索及智能问答，结合 Chroma 向量库自动识别薄弱知识点并推送关联内容，辅助高效学习。

*Here is a dream.*

---

## ✨ 已完成功能

### 📄 文档管理
- PDF / DOCX 上传与解析（PyPDFLoader、Docx2txtLoader）
- 中文标点优先的智能切片（RecursiveCharacterTextSplitter）
- Chunk 级增量去重（MD5 hash），只 embedding 变化部分
- 自动学科识别（LLM 判断数学、语文、英语等）
- 文档列表查询、详情查看、删除

### 🤖 智能问答
- LangChain Agent 驱动（create_agent + 结构化输出）
- 学科过滤检索，避免跨学科内容干扰
- 笔记纠错：自动指出笔记中的错误并给出正确解释
- 笔记缺失提醒：笔记中没有的知识点会提示补充
- 多轮对话记忆（thread_id 会话隔离）
- 闲聊支持：非学习问题正常回答，不污染学习数据

### 📊 学习分析
- 薄弱知识点自动识别（高频提问 + 笔记缺失 + 笔记纠错）
- 时间衰减机制（30/60 天分级降级）
- 对话中可查询薄弱项，Agent 结合图谱推荐关联内容

### 🕸️ 知识图谱
- 自动构建学科 → 文档 → 知识点三层图谱
- 知识点共现关联（同一问题中出现的知识点自动连边）
- 支持 ECharts 直接渲染

---

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| Web 框架 | FastAPI |
| AI 框架 | LangChain 1.0+ / LangGraph |
| LLM | 阿里百炼（Qwen） |
| Embedding | DashScope Embeddings |
| 向量数据库 | Chroma（嵌入式） |
| 文档解析 | PyPDFLoader、Docx2txtLoader |

---

## 🚀 快速开始

```bash
cd backend
uv sync
python main.py
```

启动后访问 http://127.0.0.1:8000/docs 查看 API 文档。

---

## 📁 项目结构

```
Chen-Assistant/
├── backend/                  # 后端服务
│   ├── src/
│   │   ├── core/             # 核心基础设施（配置、LLM、中间件）
│   │   ├── api/v1/endpoints/ # RESTful API 路由
│   │   ├── services/         # 业务逻辑层
│   │   ├── models/           # Pydantic 数据模型
│   │   ├── ai/               # Agent / 工具 / Prompt / 向量库
│   │   └── utils/            # 通用工具
│   ├── chroma_db/            # Chroma 持久化数据
│   └── tests/                # 测试
└── frontend/                 # 🚧 下一阶段
```

---

## 🗺️ 下一阶段

- 🎨 前端界面开发（Vue + ECharts 知识图谱可视化）
- 📱 对话式学习界面（多会话窗口、消息气泡）
- 📈 学习仪表盘（薄弱知识点面板、学科覆盖率）
- 🔔 主动推送复习提醒
