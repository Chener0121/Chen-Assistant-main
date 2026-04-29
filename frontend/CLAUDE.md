# 项目概述

Chen-Assistant 是基于用户上传的纯文字学习笔记，通过大模型API与LangChain Agent实现知识抽取、检索及智能问答，结合Chroma向量库构建知识图谱，自动识别薄弱知识点并推送关联内容，辅助高效学习。

## 开发准则

Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused.

Don't add features, refactor code, or make "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need extra configurability.

Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs). Don't use backwards-compatibility shims when you can just change the code.

Don't create helpers, utilities, or abstractions for one-time operations. Don't design for hypothetical future requirements. The right amount of complexity is the minimum needed for the current task. Reuse existing abstractions where possible and follow the DRY principle.

## 开发与调试 (Development & Debugging)

本项目在windows下进行开发，请使用windows语言进行开发与调试。

### 前端开发规范

注意：

- API 接口规范：所有的 API 接口都应该定义在 `frontend/src/apis` 下面。
- Icon 应该从 @ant-design/icons-vue 或者 lucide-vue-next （推荐，但是需要注意尺寸）。
- Vue 中的样式使用 less，非必要情况必须使用[base.css](frontend/src/assets/css/base.css) 中的颜色变量。
- UI风格要简洁，同时要保持一致性，不要悬停位移，不要过度使用阴影以及渐变色。
- 后端接口文档放在了`backend/docs/api-reference.md`，需要对接后端接口时进行参考。

**其他**：

- 如果需要新建说明文档（仅开发者可见，非必要不创建），则保存在 `frontend/docs/vibe` 文件夹下面
- 代码更新后要检查文档部分是否有需要更新的地方，文档应该更新最新版（`frontend/docs/latest`）
