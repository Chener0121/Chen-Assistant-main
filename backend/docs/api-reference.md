# Chen-Assistant API 接口文档

Base URL: `http://127.0.0.1:8000`

在线 Swagger 文档: `http://127.0.0.1:8000/docs`

---

## 统一响应格式

所有接口（除 204 无内容外）统一使用以下 JSON 结构：

```json
{
  "code": 200,
  "msg": "success",
  "data": ...
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | HTTP 状态码 |
| msg | string | 状态描述 |
| data | any | 业务数据，具体结构见各接口 |

### 错误响应

```json
{
  "code": 404,
  "msg": "文档不存在",
  "data": null
}
```

---

## 1. 文档管理

### 1.1 上传文档

`POST /api/v1/documents`

上传 PDF / DOCX 学习笔记，自动解析、切片、增量去重、向量化入库。

**请求**

- Content-Type: `multipart/form-data`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | PDF 或 DOCX 文件 |

**响应**

文件内容有变化时返回 `201`：

```json
{
  "code": 201,
  "msg": "success",
  "data": {
    "file_id": "高数笔记_第一章",
    "subject": "数学",
    "added": 12,
    "skipped": 3,
    "deleted": 1
  }
}
```

文件内容未变化时返回 `200`：

```json
{
  "code": 200,
  "msg": "文件内容未变化，跳过处理",
  "data": {
    "file_id": "高数笔记_第一章",
    "subject": "数学",
    "added": 0,
    "skipped": 15,
    "deleted": 0
  }
}
```

**data 字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| file_id | string | 文档唯一标识（文件名去掉扩展名） |
| subject | string | 自动识别的学科（数学、语文、英语等） |
| added | int | 本次新增的 chunk 数量 |
| skipped | int | 已存在未变化的 chunk 数量 |
| deleted | int | 本次被移除的旧 chunk 数量 |

---

### 1.2 获取文档列表

`GET /api/v1/documents`

**请求**：无参数

**响应**

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "file_id": "高数笔记_第一章",
      "subject": "数学"
    },
    {
      "file_id": "英语笔记_Unit3",
      "subject": "英语"
    }
  ]
}
```

**data 字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| file_id | string | 文档唯一标识 |
| subject | string | 所属学科 |

---

### 1.3 获取文档详情

`GET /api/v1/documents/{file_id}`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| file_id | string | 文档唯一标识 |

**响应**

成功（200）：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "file_id": "高数笔记_第一章",
    "subject": "数学",
    "chunk_count": 15
  }
}
```

文件不存在（404）：

```json
{
  "code": 404,
  "msg": "文档不存在",
  "data": null
}
```

**data 字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| file_id | string | 文档唯一标识 |
| subject | string | 所属学科 |
| chunk_count | int | 文档的 chunk（切片）数量 |

---

### 1.4 删除文档

`DELETE /api/v1/documents/{file_id}`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| file_id | string | 文档唯一标识 |

**响应**

- 成功：HTTP `204`，无响应体
- 文件不存在：HTTP `404`

```json
{
  "code": 404,
  "msg": "文档不存在",
  "data": null
}
```

---

## 2. 智能问答

### 2.1 提问

`POST /api/v1/qa`

基于向量检索 + Agent 的智能问答，支持多轮对话。

**请求**

- Content-Type: `application/json`

```json
{
  "question": "极限的定义是什么？",
  "thread_id": "default"
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| question | string | 是 | - | 用户提问内容 |
| thread_id | string | 否 | "default" | 会话 ID，用于多轮对话隔离 |

**响应**

学习相关问题：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "subject": "数学",
    "answer": "这个问题你的笔记里有提到哦～极限的定义是：对于任意给定的 ε > 0，存在 δ > 0...",
    "knowledge_points": ["极限的定义", "ε-δ语言"],
    "note_corrections": [],
    "used_note": true
  }
}
```

笔记有纠错时：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "subject": "数学",
    "answer": "你的笔记里关于极限的部分有一个小错误哦，帮你纠正一下～",
    "knowledge_points": ["极限的定义"],
    "note_corrections": [
      {
        "original": "极限就是无限接近但不等于",
        "corrected": "极限是与 ε 和 δ 相关的精确定义，不是简单的'无限接近'"
      }
    ],
    "used_note": true
  }
}
```

闲聊问题：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "subject": "",
    "answer": "北京好玩的地方可多啦！故宫、长城、颐和园都值得去～",
    "knowledge_points": [],
    "note_corrections": [],
    "used_note": false
  }
}
```

**data 字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| subject | string | 问题所属学科，闲聊为空字符串 |
| answer | string | 回答内容，口语化风格 |
| knowledge_points | string[] | 提取的知识点列表，闲聊为空数组 |
| note_corrections | array | 笔记纠错列表，无纠错为空数组 |
| note_corrections[].original | string | 笔记中的原始错误内容 |
| note_corrections[].corrected | string | 正确的内容 |
| used_note | bool | 是否使用了笔记内容回答 |

---

## 3. 知识图谱

### 3.1 获取知识图谱

`GET /api/v1/graph`

返回知识点节点与关联关系，包含学科、文档、知识点三类节点。

**请求**：无参数

**响应**

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "nodes": [
      {
        "id": "subject:数学",
        "label": "数学",
        "type": "subject"
      },
      {
        "id": "doc:高数笔记_第一章",
        "label": "高数笔记_第一章",
        "type": "document"
      },
      {
        "id": "kp:极限的定义",
        "label": "极限的定义",
        "type": "knowledge_point",
        "count": 5
      }
    ],
    "edges": [
      {
        "source": "subject:数学",
        "target": "doc:高数笔记_第一章",
        "type": "belongs_to"
      },
      {
        "source": "subject:数学",
        "target": "kp:极限的定义",
        "type": "contains"
      },
      {
        "source": "kp:极限的定义",
        "target": "kp:ε-δ语言",
        "type": "related"
      }
    ]
  }
}
```

**节点类型**

| type | id 格式 | 说明 | 额外字段 |
|------|---------|------|----------|
| subject | `subject:{学科名}` | 学科节点 | 无 |
| document | `doc:{file_id}` | 文档节点 | 无 |
| knowledge_point | `kp:{知识点}` | 知识点节点 | count（出现次数） |

**边类型**

| type | 说明 |
|------|------|
| belongs_to | 学科 → 文档（文档属于某学科） |
| contains | 学科 → 知识点（学科包含某知识点） |
| related | 知识点 ↔ 知识点（共现关联） |

**前端渲染建议**：节点 id 带 `subject:` / `doc:` / `kp:` 前缀，可用于区分颜色和样式。ECharts 的 graph 类型可直接使用 nodes / edges 数据。

---

## 4. 学习分析

### 4.1 获取薄弱知识点

`GET /api/v1/analytics/weak-points`

根据问答记录分析薄弱知识点，按等级排序（high > medium > low），带时间衰减。

**请求**：无参数

**响应**

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "knowledge_point": "极限的定义",
      "subject": "数学",
      "ask_count": 8,
      "missing_count": 2,
      "correction_count": 1,
      "last_active": "2026-04-28T15:30:00",
      "level": "high"
    },
    {
      "knowledge_point": "导数的应用",
      "subject": "数学",
      "ask_count": 5,
      "missing_count": 3,
      "correction_count": 0,
      "last_active": "2026-04-25T10:00:00",
      "level": "medium"
    },
    {
      "knowledge_point": "定积分",
      "subject": "数学",
      "ask_count": 4,
      "missing_count": 0,
      "correction_count": 0,
      "last_active": "2026-04-20T09:15:00",
      "level": "low"
    }
  ]
}
```

无数据时：

```json
{
  "code": 200,
  "msg": "success",
  "data": []
}
```

**data 字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| knowledge_point | string | 知识点名称 |
| subject | string | 所属学科 |
| ask_count | int | 提问次数 |
| missing_count | int | 笔记中缺失该知识点的次数 |
| correction_count | int | 笔记纠错次数 |
| last_active | string | 最后活跃时间（ISO 8601） |
| level | string | 薄弱等级：`high` / `medium` / `low` |

**等级判定规则**

| 条件 | 等级 |
|------|------|
| 有笔记纠错（correction_count > 0） | high |
| 笔记缺失（missing_count > 0） | medium |
| 反复提问（ask_count >= 3） | low |

**时间衰减规则**

| 距上次活跃 | 处理 |
|------------|------|
| 30 天内 | 保持当前等级 |
| 30 ~ 60 天 | 降一级（high → medium → low → 移除） |
| 超过 60 天 | 从薄弱知识点中移除 |

---

### 4.2 提问统计

`GET /api/v1/analytics/daily-stats`

返回按学科分组的提问次数统计，支持按天或按小时聚合。

**请求参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| mode | string | 否 | "daily" | 聚合模式：`daily`（近14天）、`hourly`（近14小时） |

**响应（daily 模式）**

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "dates": ["04-16", "04-17", "04-18", "04-19", "04-20", "04-21", "04-22", "04-23", "04-24", "04-25", "04-26", "04-27", "04-28", "04-29"],
    "subjects": ["数学", "英语"],
    "series": {
      "数学": [0, 1, 3, 2, 0, 0, 1, 0, 2, 0, 1, 3, 2, 1],
      "英语": [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0]
    }
  }
}
```

**响应（hourly 模式）**

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "dates": ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"],
    "subjects": ["数学"],
    "series": {
      "数学": [0, 1, 0, 2, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    }
  }
}
```

无数据时：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "dates": ["04-16", "04-17", "04-18", "04-19", "04-20", "04-21", "04-22", "04-23", "04-24", "04-25", "04-26", "04-27", "04-28", "04-29"],
    "subjects": [],
    "series": {}
  }
}
```

**data 字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| dates | string[] | 时间标签数组，固定 14 个元素 |
| subjects | string[] | 出现过的学科列表（已排序） |
| series | object | 每个学科对应一个数组，顺序与 dates 对应，值为该时段的提问次数 |

---

### 4.3 清空问答记录

`DELETE /api/v1/analytics/qa-records`

清空所有问答记录，不影响文档向量数据。

**请求**：无参数

**响应**

- 成功：HTTP `204`，无响应体

---

## 5. 系统

### 5.1 健康检查

`GET /health`

**响应**

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "status": "ok"
  }
}
```

### 5.2 根路由

`GET /`

**响应**

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "message": "Chen-Assistant API"
  }
}
```

---

## 状态码汇总

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功（文档上传且有新增内容） |
| 204 | 操作成功，无返回内容（删除操作） |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
