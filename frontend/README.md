# Frontend

Chen-Assistant 前端，基于 Vue 3 + Vite + TypeScript。

## 启动

```bash
npm install
npm run dev
```

开发地址：http://localhost:5173
API 请求自动代理到后端 http://127.0.0.1:8000

## 项目结构

```
src/
├── main.ts              # 应用入口
├── App.vue              # 根组件
├── router/index.ts      # 路由配置
├── apis/index.ts        # axios 封装（统一拦截）
├── views/               # 页面组件
├── components/          # 通用组件
└── assets/css/
    └── base.css         # 全局样式 + CSS 变量
```

## 技术栈

| 技术 | 用途 |
|------|------|
| Vue 3 | 前端框架 |
| TypeScript | 类型安全 |
| Vite | 构建工具 |
| Vue Router | 路由管理 |
| Pinia | 状态管理 |
| Less | CSS 预处理器 |
| Axios | HTTP 请求 |
| Lucide Vue Next | 图标库 |
