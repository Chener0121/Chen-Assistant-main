# 🎓 知识图谱智学助手(Chen-Assistant)

基于上传的学习笔记，通过大模型 API 与 LangChain Chain 实现知识抽取、检索及智能问答，结合 Chroma 向量库自动识别薄弱知识点并推送关联内容，辅助高效学习。

*Here is a dream.*

---

## ✨ 已完成功能

### 📄 文档管理
- PDF / DOCX 上传与解析（PyPDFLoader、Docx2txtLoader）
- 中文标点优先的智能切片（RecursiveCharacterTextSplitter）
- Chunk 级增量去重（MD5 hash），只 embedding 变化部分
- 自动学科识别（LLM 从固定列表中匹配，防止多余输出）
- 文档列表查询（含 chunk 数量）、详情查看、删除

### 🤖 智能问答
- LangChain Chain 驱动（prompt | llm.with_structured_output，1 次 LLM 调用）
- 代码自动判断意图：笔记检索 / 薄弱点查询，无需 Agent 决策
- 学科过滤检索，避免跨学科内容干扰
- 笔记纠错：自动指出笔记中的错误并给出正确解释
- 笔记缺失提醒：笔记中没有的知识点会提示补充
- 多轮对话（thread_id 会话隔离）
- 闲聊支持：非学习问题正常回答，不污染学习数据
- LaTeX 公式 + Markdown 渲染

### 📊 学习分析
- 薄弱知识点自动识别（高频提问 + 笔记缺失 + 笔记纠错）
- 时间衰减机制（30/60 天分级降级）
- 对话中可查询薄弱项（代码关键词匹配 → 直接查数据）
- 近 14 天 / 14 小时提问趋势统计（按学科分组堆叠柱状图）

### 🕸️ 知识图谱
- 自动构建学科 → 文档 → 知识点三层图谱
- 知识点共现关联（同一问题中出现的知识点自动连边）
- 支持 ECharts 直接渲染

### 🎨 前端界面
- Layout 骨架（64px 侧边栏 + 顶部栏 + 可滚动内容区）
- 数据面板：统计卡片 + 提问趋势图 + 文档上传/列表 + 薄弱知识点
- 智能问答：左侧会话列表（新建/切换/删除）+ 右侧消息气泡 + LaTeX 渲染
- 会话持久化（Pinia + localStorage）

---

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | Vue 3 + TypeScript + Vite |
| UI 组件库 | Element Plus |
| 状态管理 | Pinia |
| 图表 | ECharts |
| 公式渲染 | KaTeX + Marked |
| 图标 | Lucide Vue Next |
| Web 框架 | FastAPI |
| AI 框架 | LangChain 1.0+ |
| LLM | 阿里百炼（Qwen） |
| Embedding | DashScope Embeddings |
| 向量数据库 | Chroma（嵌入式） |
| 文档解析 | PyPDFLoader、Docx2txtLoader |

---

## 🚀 快速开始

```bash
# 后端
cd backend
uv sync
python main.py

# 前端
cd frontend
npm install
npm run dev
```

后端 API 文档：http://127.0.0.1:8000/docs
前端开发地址：http://localhost:5173

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
│   │   ├── ai/               # Chain / 检索 / Prompt / 向量库
│   │   └── utils/            # 通用工具
│   ├── docs/                 # 接口文档
│   ├── chroma_db/            # Chroma 持久化数据
│   └── tests/                # 测试
└── frontend/                 # 前端界面
    └── src/
        ├── apis/             # API 接口层
        ├── stores/           # Pinia 状态管理
        ├── views/            # 页面组件
        ├── components/layout/ # 布局组件
        └── assets/css/       # 全局样式 + CSS 变量
```

---

## 🗺️ 下一阶段

- 🌊 前端流式输出（SSE + token-by-token 渲染）
- 🕸️ 知识图谱可视化页面（ECharts 力导向图）
- 📈 学习仪表盘优化（学科覆盖率、复习建议）