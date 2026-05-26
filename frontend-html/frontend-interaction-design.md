# 舆情研判与舆论引导系统 —— 前端页面交互设计文档

> 本文档描述每个页面的核心交互逻辑、需调用的后端 API、状态流转和异常处理。
> 后端地址：`http://localhost:5001`

---

## 1. 舆情仪表盘 `/`

### 页面定位
系统首页，展示全局运行状态和快捷入口。

### 交互元素

| 元素 | 交互 | 说明 |
|------|------|------|
| **KPI 卡片×3** | 静态展示 | 进行中的研判数 / 已完成模拟数 / Agent 总数。初次加载时从 `/api/simulation/history` 统计得出 |
| **系统状态栏** | 实时指示灯 | 三个状态灯：LLM 连接（调 `/health`）、Zep Cloud（调 `/api/graph/project/list` 看是否报错）、后端服务 |
| **最近项目列表** | 表格展示 | 调用 `GET /api/simulation/history?limit=5`，展示项目名称、状态 badge、创建时间 |
| **快捷操作按钮** | 点击跳转 | "新建研判" → `/project/new`；"查看历史" → `/history` |
| **项目行点击** | 进入详情 | 根据项目当前状态跳转到对应页面：若 ontology 未生成 → `/project/:id/ontology`；若 graph 未构建 → `/project/:id/graph`；若未模拟 → `/project/:id/simulation/config` |

### 状态流转
```
加载 → 调 /health 确认后端在线 → 调 /history 获取列表 → 渲染
```

### 异常处理
- 后端离线：KPI 显示 "--"，状态灯变红，提示"后端服务未启动"
- 空状态：显示"暂无研判项目，点击新建开始"

---

## 2. 新建研判项目 `/project/new`

### 页面定位
创建新的舆情推演项目，上传种子材料并描述推演需求。

### 交互元素

| 元素 | 交互 | 说明 |
|------|------|------|
| **项目名称输入框** | 文本输入 | 必填，限制 50 字 |
| **模拟需求文本域** | 文本输入 | 必填，描述"如果 XX 发生，舆论会如何演变"，带示例占位符 |
| **文件上传区** | 拖拽/点击上传 | 支持 PDF/TXT/MD，可多文件。显示已选文件列表和大小 |
| **提交按钮** | 点击提交 | 调 `POST /api/graph/ontology/generate`（multipart/form-data）|
| **加载状态** | 转圈/进度条 | 上传和 LLM 分析过程可能持续 10~30 秒 |

### API 调用
```http
POST /api/graph/ontology/generate
Content-Type: multipart/form-data

files: [File, File, ...]
simulation_requirement: "如果这所高校严格执行新管理规定，校园舆论会如何演变？"
project_name: "高校管理条例舆情测试"
```

### 状态流转
```
填写表单 → 验证必填 → 调 API → 等待响应（显示"AI 正在分析材料，提取实体与关系..."）
→ 成功 → 跳转 /project/:id/ontology
→ 失败 → 显示错误信息（如 API Key 失效、文件格式不支持）
```

### 异常处理
- 文件过大：前端限制单个 10MB，总计 50MB
- API Key 无效：显示 "LLM 服务连接失败，请检查系统设置"
- 文件解析失败：显示具体文件名和错误

---

## 3. 本体生成结果 `/project/:id/ontology`

### 页面定位
展示 LLM 从材料中提取的实体类型和关系类型，让用户确认后再构建图谱。

### 交互元素

| 元素 | 交互 | 说明 |
|------|------|------|
| **分析摘要卡片** | 静态展示 | 显示 `analysis_summary`，概括材料核心内容 |
| **实体类型列表** | 可折叠面板 | 每个实体类型展示：名称、描述、属性列表、示例。可展开/收起 |
| **关系类型列表** | 可折叠面板 | 每个关系展示：名称、描述、源→目标实体类型 |
| **确认构建按钮** | 点击提交 | 调 `POST /api/graph/build`，进入构建流程 |
| **重新生成按钮** | 点击 | 返回新建项目页，重新上传材料 |

### API 调用
```http
# 页面加载时获取项目详情
GET /api/graph/project/:project_id

# 点击"确认构建"
POST /api/graph/build
{"project_id": "proj_xxx", "graph_name": "用户输入或默认项目名称"}
```

### 状态流转
```
加载 → 调 /project/:id 获取详情 → 渲染本体定义
→ 用户点击"确认构建" → 调 /build → 返回 task_id → 跳转 /project/:id/graph
```

### 异常处理
- 项目不存在：404，跳转仪表盘
- 未生成本体：项目状态为 created，提示"请先完成本体生成"

---

## 4. 知识图谱构建 `/project/:id/graph`

### 页面定位
异步构建 Zep 知识图谱，实时展示进度。

### 交互元素

| 元素 | 交互 | 说明 |
|------|------|------|
| **进度条** | 动态更新 | 0%~100%，显示当前阶段文字 |
| **构建日志** | 实时滚动 | 类似终端输出，展示当前操作（"正在分块...""正在创建图谱..."）|
| **阶段指示器** | 步骤高亮 | 4 个阶段：文本分块 → 创建图谱 → 设置本体 → 添加文本 → 等待处理 |
| **图谱预览** | 可选 | 构建完成后，调 `GET /api/graph/data/:graph_id` 获取节点/边数据，用力导向图展示 |
| **继续按钮** | 点击跳转 | 构建完成后，跳转 `/project/:id/simulation/config` |
| **取消/重试** | 按钮 | 构建失败时显示"重试"，调 `/project/:id/reset` 后重新 /build |

### API 调用
```http
# 轮询任务进度（每 2 秒）
GET /api/graph/task/:task_id

# 构建完成后获取图谱数据
GET /api/graph/data/:graph_id
```

### 状态流转
```
加载 → 调 /project/:id 检查状态
  → 若 status == "graph_building": 开始轮询 /task/:task_id
  → 若 status == "ontology_generated": 自动调 /build
  → 若 status == "graph_completed": 直接展示结果
→ 轮询中：更新进度条和日志
→ 完成：展示图谱预览 + "进入模拟配置"按钮
→ 失败：显示错误 + 重试按钮
```

### 异常处理
- Zep Key 无效：构建任务失败，日志显示 "Zep API Key 无效"
- 网络中断：轮询失败时自动重试 3 次，之后提示"连接中断，请刷新重试"

---

## 5. 模拟环境配置 `/project/:id/simulation/config`

### 页面定位
选择参与模拟的实体、平台（Twitter/Reddit），创建模拟实例。

### 交互元素

| 元素 | 交互 | 说明 |
|------|------|------|
| **实体筛选列表** | 复选框 | 调 `GET /api/simulation/entities/:graph_id`，按类型分组展示，用户勾选要参与模拟的实体 |
| **实体统计** | 动态更新 | 实时显示已选实体数量 |
| **平台选择** | 开关/复选 | Twitter、Reddit 二选一或双选 |
| **模拟需求回显** | 只读文本 | 显示项目创建时的 simulation_requirement |
| **创建模拟按钮** | 点击提交 | 调 `POST /api/simulation/create` |
| **准备环境按钮** | 点击提交 | 调 `POST /api/simulation/prepare`，生成 Agent Profile |

### API 调用
```http
# 获取图谱实体
GET /api/simulation/entities/:graph_id

# 创建模拟
POST /api/simulation/create
{"project_id": "proj_xxx", "graph_id": "mirofish_xxx", "enable_twitter": true, "enable_reddit": false}

# 准备模拟环境
POST /api/simulation/prepare
{"simulation_id": "sim_xxx", "entity_types": ["Student", "MediaOutlet"], "use_llm_for_profiles": true}
```

### 状态流转
```
加载 → 调 /project/:id 获取 graph_id → 调 /entities/:graph_id 获取实体列表
→ 用户选择实体和平台 → 调 /create → 获得 simulation_id
→ 调 /prepare → 获得 task_id → 跳转 /project/:id/simulation/run（准备阶段）
```

### 异常处理
- 未选择实体：前端拦截，提示"请至少选择一个实体"
- Zep 实体读取失败：提示"图谱数据不可用，请检查图谱构建状态"

---

## 6. 舆情模拟运行 `/project/:id/simulation/run`

### 页面定位
核心页面。运行多智能体模拟，实时监控舆论演化过程。

### 交互元素

| 元素 | 交互 | 说明 |
|------|------|------|
| **阶段标签页** | 切换 | 三个标签：准备中 / 运行中 / 已完成 |
| **准备阶段** | 进度监控 | 若状态为 preparing，轮询 `/api/simulation/prepare/status`，显示 Agent Profile 生成进度（"正在生成第 12/50 个人格..."）|
| **运行控制栏** | 按钮组 | "开始模拟"（调 `/start`）、"暂停"（调 `/stop`）、"强制停止" |
| **轮次进度条** | 动态更新 | 当前轮 / 总轮（如 45/120）|
| **实时日志流** | 自动滚动 | 调 `GET /api/simulation/:id/run-status/detail` 或轮询 `actions` 接口，显示 Agent 行为日志 |
| **情感趋势图** | 折线图 | 基于 `GET /api/simulation/:id/timeline` 数据，展示正面/负面/中性情感比例随轮次变化 |
| **帖子流** | 瀑布流 | 调 `GET /api/simulation/:id/posts`，展示 Agent 发布的社交媒体帖子，支持按平台筛选 |
| **评论流** | 嵌套列表 | 调 `GET /api/simulation/:id/comments`，展示帖子下的评论 |
| **词云/热门话题** | 可视化 | 从帖子内容中提取高频词 |
| **Agent 统计** | 图表 | 调 `GET /api/simulation/:id/agent-stats`，展示各 Agent 发帖数、互动数排行 |

### API 调用
```http
# 准备阶段轮询
POST /api/simulation/prepare/status
{"task_id": "task_xxx", "simulation_id": "sim_xxx"}

# 启动模拟
POST /api/simulation/start
{"simulation_id": "sim_xxx", "rounds": 40}

# 运行状态轮询（每 3~5 秒）
GET /api/simulation/:simulation_id/run-status
GET /api/simulation/:simulation_id/run-status/detail

# 行为数据
GET /api/simulation/:simulation_id/actions
GET /api/simulation/:simulation_id/posts?platform=twitter&limit=50
GET /api/simulation/:simulation_id/comments?post_id=xxx
GET /api/simulation/:simulation_id/timeline
GET /api/simulation/:simulation_id/agent-stats
```

### 状态流转
```
加载 → 调 /simulation/:id 获取状态
  → status == "created/preparing": 显示准备阶段，轮询 prepare/status
  → status == "ready": 显示"准备完成，点击开始"
  → status == "running": 显示运行监控，轮询 run-status
  → status == "completed/stopped": 显示结果，解锁"生成报告"按钮
→ 用户点击"开始" → 调 /start → 进入 running 状态
→ 轮询中更新所有面板
→ 完成 → 弹提示"模拟完成" → 解锁报告生成
```

### 异常处理
- 模拟崩溃：run-status 返回 failed，显示错误日志摘要
- OASIS 依赖缺失：准备阶段报错，提示"模拟引擎环境未就绪"

---

## 7. 研判报告 `/project/:id/report`

### 页面定位
展示 AI 生成的舆情研判报告，支持分章节浏览和下载。

### 交互元素

| 元素 | 交互 | 说明 |
|------|------|------|
| **生成报告按钮** | 点击触发 | 若报告未生成，调 `POST /api/report/generate`。异步任务，显示进度 |
| **报告进度条** | 动态更新 | 轮询 `POST /api/report/generate/status`，显示当前生成章节 |
| **报告目录** | 侧边导航 | 点击章节标题跳转对应位置 |
| **Markdown 渲染区** | 滚动阅读 | 调 `GET /api/report/:report_id`，渲染 `markdown_content` |
| **分章节加载** | 增量展示 | 大报告可轮询 `GET /api/report/:id/sections`，逐章展示 |
| **关键发现卡片** | 高亮展示 | 提取报告中的核心结论，置顶显示 |
| **下载按钮** | 点击下载 | 调 `GET /api/report/:id/download`，下载 .md 文件 |
| **与 ReportAgent 对话** | 聊天框 | 底部悬浮输入框，调 `POST /api/report/chat` |

### API 调用
```http
# 触发报告生成
POST /api/report/generate
{"simulation_id": "sim_xxx"}

# 轮询生成进度
POST /api/report/generate/status
{"task_id": "task_xxx"}

# 获取报告详情
GET /api/report/:report_id

# 获取分章节内容
GET /api/report/:report_id/sections
GET /api/report/:report_id/section/:section_index

# 下载
GET /api/report/:report_id/download

# 与 ReportAgent 对话
POST /api/report/chat
{"simulation_id": "sim_xxx", "message": "请解释舆情走向", "chat_history": []}
```

### 状态流转
```
加载 → 调 /check/:simulation_id 检查报告状态
  → has_report == false: 显示"生成报告"按钮
  → has_report == true && status == "completed": 直接展示报告
→ 点击生成 → 调 /generate → 获得 task_id → 轮询进度
→ 完成 → 调 /:report_id 获取内容 → 渲染 Markdown
```

### 异常处理
- 报告生成超时：显示"生成时间较长，请稍后刷新"
- 模拟未完成：拦截，提示"请先完成模拟运行"

---

## 8. 深度交互 `/project/:id/interaction`

### 页面定位
与模拟世界中的特定 Agent 进行一对一对话，或批量访谈。

### 交互元素

| 元素 | 交互 | 说明 |
|------|------|------|
| **Agent 选择器** | 下拉/列表 | 调 `GET /api/simulation/:id/profiles`，展示所有 Agent 名称和人格简介 |
| **Agent 信息卡** | 静态展示 | 选中后展示该 Agent 的详细人设、记忆、立场 |
| **对话窗口** | 聊天界面 | 类微信/ChatGPT 对话样式，用户输入 → 调 `/interview` → 显示 Agent 回复 |
| **批量访谈** | 多选+批量发送 | 选择多个 Agent，调 `/interview/batch`，并行获取回复 |
| **全员访谈** | 一键发送 | 调 `/interview/all`，向所有 Agent 发送同一问题 |
| **访谈历史** | 侧边栏列表 | 调 `/interview/history`，展示过往对话记录 |
| **注入变量** | 输入框 | 可输入假设性事件（如"如果校方道歉了，你会怎么想？"），观察 Agent 反应 |

### API 调用
```http
# 获取 Agent Profile
GET /api/simulation/:simulation_id/profiles?platform=reddit

# 单聊
POST /api/simulation/interview
{"simulation_id": "sim_xxx", "agent_name": "Agent_001", "message": "你对新规怎么看？"}

# 批量访谈
POST /api/simulation/interview/batch
{"simulation_id": "sim_xxx", "agent_names": ["Agent_001", "Agent_002"], "message": "..."}

# 全员访谈
POST /api/simulation/interview/all
{"simulation_id": "sim_xxx", "message": "..."}

# 获取访谈历史
POST /api/simulation/interview/history
{"simulation_id": "sim_xxx", "agent_name": "Agent_001"}
```

### 状态流转
```
加载 → 调 /profiles 获取 Agent 列表 → 用户选择 Agent
→ 用户输入问题 → 调 /interview → 显示回复 → 追加到对话历史
→ 可切换 Agent 继续对话
```

### 异常处理
- Agent 未响应：显示"Agent 思考中..."，超时后提示"该 Agent 暂时无法响应"
- 模拟未运行：提示"模拟环境未激活，请先运行模拟"

---

## 9. 历史项目库 `/history`

### 页面定位
展示所有过往推演项目，支持搜索、筛选、删除。

### 交互元素

| 元素 | 交互 | 说明 |
|------|------|------|
| **搜索框** | 文本输入 | 按项目名称关键词过滤（前端本地过滤）|
| **状态筛选** | 下拉/标签 | 全部 / 进行中 / 已完成 / 失败 |
| **项目卡片网格** | 卡片列表 | 调 `GET /api/simulation/history`，每个卡片展示：项目名称、创建时间、状态 badge、实体数、轮次数 |
| **卡片点击** | 进入详情 | 根据项目状态跳转到对应页面 |
| **删除按钮** | 二次确认 | 调 `DELETE /api/graph/project/:id`，确认后删除 |
| **分页/加载更多** | 滚动/按钮 | limit/offset 或无限滚动 |

### API 调用
```http
GET /api/simulation/history?limit=50
DELETE /api/graph/project/:project_id
```

### 状态流转
```
加载 → 调 /history → 渲染卡片列表
→ 用户搜索/筛选 → 前端过滤渲染
→ 点击卡片 → 跳转到项目对应阶段页面
```

### 异常处理
- 空状态：显示"暂无历史项目"
- 删除失败：提示错误原因

---

## 10. 系统设置 `/settings`

### 页面定位
配置 API Key、模型参数等系统级配置。

### 交互元素

| 元素 | 交互 | 说明 |
|------|------|------|
| **LLM API Key** | 密码输入框 | 当前值从 `.env` 读取（后端不提供查询接口，需前端自行管理或留空）|
| **Base URL** | 文本输入 | 默认 `https://api.deepseek.com/v1` |
| **模型名称** | 文本输入 | 默认 `deepseek-chat` |
| **Zep API Key** | 密码输入框 | 同上 |
| **保存按钮** | 点击 | 调一个自定义后端接口或提示用户手动修改 `.env`（MiroFish 后端没有提供写 `.env` 的接口，需前端提示用户手动配置）|
| **连接测试** | 按钮 | 分别调 `/health` 和尝试调 `/ontology/generate` 测试 LLM；调 `/build` 测试 Zep |

### 异常处理
- 前端可本地存储用户输入的设置（localStorage），但后端 `.env` 仍需手动修改
- 连接测试失败：高亮对应输入框，提示检查 Key

---

## 全局交互规范

### 路由参数
所有 `:id` 参数均为 `project_id`（格式 `proj_xxxx`），模拟相关页面需额外使用 `simulation_id`（格式 `sim_xxxx`）。

### 状态 Badge 映射
```
created              → 灰色"已创建"
ontology_generated   → 蓝色"本体已生成"
graph_building       → 黄色"构建中"
graph_completed      → 绿色"图谱就绪"
ready                → 绿色"准备就绪"
running              → 蓝色"运行中"
completed            → 绿色"已完成"
stopped              → 橙色"已停止"
failed               → 红色"失败"
```

### 轮询策略
- 图谱构建：每 2 秒轮询 `/task/:id`
- 模拟准备：每 2 秒轮询 `/prepare/status`
- 模拟运行：每 3~5 秒轮询 `/run-status`
- 报告生成：每 3 秒轮询 `/generate/status`
- 超时：所有轮询设置 300 秒（5 分钟）上限，超时报错

### 错误统一处理
- 401/403：提示"API Key 无效，请检查设置"
- 404：提示"资源不存在或已被删除"
- 500：提示"服务端错误，请稍后重试"
- 网络错误：自动重试 3 次，之后提示"网络异常"
