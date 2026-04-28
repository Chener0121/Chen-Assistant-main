# 项目概述

Chen-Assistant 是基于用户上传的纯文字学习笔记，通过大模型API与LangChain Agent实现知识抽取、检索及智能问答，结合Chroma向量库构建知识图谱，自动识别薄弱知识点并推送关联内容，辅助高效学习。

## 项目结构参考 (Project Overview)

backend/
├── .env                        # 本地开发环境变量（不提交Git）
├── .env.template           
├── .gitignore
├── README.md
├── pyproject.toml              # 项目元数据与依赖管理（UV）
│
├── src/                        # 源代码主目录
│   ├── main.py                 # FastAPI应用入口
│   │
│   ├── utils/                  # 通用工具函数
│   │   └── helpers.py
│   │
│   ├── core/                   # 核心基础设施（数据库连接、LLM客户端、配置等）
│   │   ├── config.py
│   │   ├── llm_client.py       # llm / embeddings 初始化
│   │   ├── exceptions.py       # 全局异常处理
│   │   ├── dependencies.py     # 全局依赖项
│   │   └── middleware.py       # 中间件
│   │
│   ├── api/                    # [表现层] 处理HTTP请求与响应
│   │   └── v1/                 # API版本管理
│   │       ├── endpoints/      # 按业务模块拆分的路由
│   │       │   ├── users.py
│   │       │   └── items.py
│   │       └── router.py       # 版本路由汇总
│   │
│   ├── services/               # [业务逻辑层] 封装核心业务逻辑
│   │
│   ├── models/                 # [数据模型层] 定义数据结构和数据库映射
│   │   ├── schemas.py          # Pydantic模型（请求/响应）
│   │   └── entities.py         # SQLAlchemy ORM实体类
│   │
│   ├── repositories/           # [数据访问层] 封装与数据库的交互
│   │
│   └── ai/                     # [AI核心] LangChain/LangGraph模块
│       ├── agents/             # 智能体定义
│       ├── chains/             # 链式调用逻辑
│       ├── tools/              # 自定义工具
│       ├── memory/             # 记忆管理
│       ├── prompts/            # Prompt模板
│       ├── vectorstores/       # 向量数据库集成
│       └── utils.py            # AI辅助工具
│
├── tests/                      # 测试目录
│   ├── unit/                   # 单元测试
│   └── integration/            # 集成测试
│
└── chroma_db/                  # Chroma存储文件

## 开发准则

Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused.

Don't add features, refactor code, or make "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need extra configurability.

Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs). Don't use backwards-compatibility shims when you can just change the code.

Don't create helpers, utilities, or abstractions for one-time operations. Don't design for hypothetical future requirements. The right amount of complexity is the minimum needed for the current task. Reuse existing abstractions where possible and follow the DRY principle.

## 开发与调试 (Development & Debugging)

本项目在windows下进行开发，请使用windows语言进行开发与调试。


### 后端开发规范

注意：

- Python 代码要符合 Python 的规范，符合 pythonic 风格，尽量使用较新的语法，避免使用旧版本的语法（版本兼容到 3.12+）
- langchain使用较新的语法，避免使用旧版本的语法（参考版本为 v1.2）
- 代码添加合适的注释，采用 RESTful 规范进行开发

**其他**：

- 如果需要新建说明文档（仅开发者可见，非必要不创建），则保存在 `backend/docs/vibe` 文件夹下面
- 代码更新后要检查文档部分是否有需要更新的地方，文档应该更新最新版（`docs/latest`）
