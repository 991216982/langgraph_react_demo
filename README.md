# 多智能体家用助理（React + FastAPI + LangGraph）

## 项目简介

本项目基于原始多智能体家用助理的思想，提供一个可运行的最小化示例：
- 前端使用 React 构建一个简易聊天界面
- 后端使用 FastAPI + LangGraph 构建监督/子智能体编排
- 子智能体工具不调用任何外部服务，全部通过内存 Map 模拟数据返回
- 所有提示词内容均为中文，便于本地化与学习

## 目录结构

```
demo_project/
  ├─ backend/                  # 后端（FastAPI + LangGraph）
  │   ├─ requirements.txt
  │   └─ app/
  │       ├─ main.py           # FastAPI 入口与路由
  │       ├─ graph.py          # LangGraph 图构建
  │       ├─ config.py         # 智能体配置（中文提示词）
  │       ├─ agents/
  │       │   └─ supervisor.py # 监督智能体
  │       ├─ utils/
  │       │   └─ factory.py    # ReAct 子智能体工厂
  │       └─ tools/            # 子智能体工具（全部Mock）
  │           ├─ registry.py
  │           ├─ calendar_tools.py
  │           ├─ notion_tools.py
  │           └─ meal_tools.py
  └─ frontend/                 # 前端（React + Vite）
      ├─ package.json
      ├─ vite.config.js
      ├─ index.html
      └─ src/
          ├─ main.jsx
          └─ App.jsx
```

## 环境要求

- Python 3.11+
- Node.js 18+
- 后端需要 `DASHSCOPE_API_KEY`（用于调用通义千问 ChatTongyi 模型）。

## 安装与启动

### 后端

1. 进入后端目录：
   ```bash
   cd backend
   ```
2. 创建并激活虚拟环境（Windows）：
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
   macOS/Linux：
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 配置环境变量（示例）：
   ```bash
   set DASHSCOPE_API_KEY=your_key_here      # Windows PowerShell: $env:DASHSCOPE_API_KEY="..."
   ```
5. 启动后端：
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### 前端

1. 进入前端目录：
   ```bash
   cd frontend
   ```
2. 安装依赖：
   ```bash
   npm install
   ```
3. 启动开发服务器：
   ```bash
   npm run dev
   ```
4. 浏览器访问 `http://localhost:5173`，通过页面输入消息与后端交互。

## 使用说明

- 在前端输入自然语言请求，例如：
  - "帮我生成两天的晚餐计划并添加到家庭日历"
  - "列出购物清单的未完成条目"

- 后端监督智能体会根据提示词拆解任务，把子任务分派给相应子智能体；子智能体通过Mock工具返回枚举数据。

## 注意事项

- 本示例不调用任何外部应用；所有工具均为内存Map模拟。
- 提示词内容为中文，且尽量保持结构化与可读性，方便学习与二次改造。


## 接口一览

- `POST /api/invoke`：输入 `messages: [["user", "..."], ...]`，返回智能体对话 `messages`
- `GET  /api/mermaid`：返回LangGraph图的Mermaid文本，用于可视化
- `GET  /api/agents`：返回已注册的子智能体名称

## 常用命令
`
- 查看已注册子智能体
  ```bash
  curl http://localhost:8000/api/agents
  ```

- 查看图的 Mermaid 表示
  ```bash
  curl http://localhost:8000/api/mermaid
  ```

- 提交一次对话（生成并添加晚餐计划示例）
  ```bash
  curl -X POST http://localhost:8000/api/invoke \
    -H "Content-Type: application/json" \
    -d '{
      "messages": [
        {"role": "user", "content": "帮我生成两天的晚餐计划并添加到家庭日历"}
      ],
      "recursion_limit": 20
    }'
  ```

- 在 Python 中直接调用日历工具（测试自动建表与事件添加）
  ```bash
  python -c "from app.tools.calendar_tools import create_calendar, add_calendar_event; print(create_calendar('家庭日历')); print(add_calendar_event('今天','明天','家庭日历','晚餐计划','两天的晚餐计划'))"
  ```

## 二次开发建议

- 优先在 `app/config.py` 修改提示词、模型或工具清单，实现快速迭代
- 在 `app/tools/` 下替换Mock实现，可逐步接入真实系统
- 使用 `supervisor.py` 的中文提示词作为拆解范式，按需扩展子任务类型

## 面向企业级生产的改进方向
### 当前状态概览
- 前端：React + Vite，最小化聊天界面（`frontend/src/App.jsx:1-61`）。
- 后端：FastAPI + LangGraph 单体进程，跨域较宽松（`backend/app/main.py:23-29`）。
- 会话状态：保存在进程内存字典 `SESSIONS`，无持久化（`backend/app/main.py:31-32`）。
- 智能体：监督智能体与子智能体通过 LangGraph 编排（`backend/app/graph.py:7-21`）。
- 模型接入：依赖通义千问 ChatTongyi，需 `DASHSCOPE_API_KEY`（`backend/app/agents/supervisor.py:28`，`backend/app/utils/factory.py:48-56`）。
- 工具：均为内存 Mock（`backend/app/tools/registry.py:1-16`）。

### 改进方向（分领域）

- 架构与模块化
  - 引入配置中心与分环境配置（dev/staging/prod），建议使用 `pydantic-settings` 定义 `Settings`，集中管理模型、工具、数据库、CORS、鉴权等。
  - 抽象 LLM Provider 层与路由策略，支持多模型与故障切换（主备、降级）。
  - 将工具系统插件化：统一接口、版本与权限声明，支持热插拔与灰度。
  - 为 LangGraph 的记忆与检查点引入外部存储（Redis/DB），避免进程重启丢失状态。

- 可用性与伸缩性
  - 进程模型：生产部署建议使用多进程/多实例（`uvicorn --workers N` 或容器编排），前置反向代理（Nginx/Ingress）。
  - 状态外置：将 `SESSIONS` 替换为 Redis/数据库会话表，支持多实例共享会话。
  - 长耗时任务异步化：使用消息队列与任务执行器（Celery/RQ），支持重试与死信队列。

- 安全与合规
  - CORS 收敛至可信域名列表，移除通配 `*`（参考 `backend/app/main.py:23-29`）。
  - 增加鉴权与权限控制（API Key/JWT/OAuth2），为每个接口定义 `Depends` 依赖与角色（RBAC）。
  - 秘钥管理：从环境变量迁移到安全秘钥托管（KMS/Vault），支持轮换与最小权限；避免在日志中打印敏感内容。
  - 内容安全：提示词与工具加防护（输入过滤、PII 识别与脱敏、越权工具调用拦截）。

- 可观测性与运维
  - 结构化 JSON 日志与全链路关联（request-id、trace-id），区分等级与模块，沉淀到日志平台。
  - 指标监控：暴露 `/metrics`（Prometheus），采集 QPS、P95 延迟、错误率、模型调用耗时与成本。引入告警（阈值/异常检测）。
  - 分布式追踪：OpenTelemetry（FastAPI/HTTP/队列/数据库），接入可视化（Jaeger/Tempo）。
  - 错误上报：Sentry/新枢纽，抓取异常堆栈与用户影响面。

- 数据与状态
  - 会话与消息持久化：PostgreSQL/SQLite（dev）存储对话、执行轨迹与工具结果，支持审计与复盘。
  - RAG 能力：向量库（PGVector/FAISS/Milvus），检索增强与知识版本管理。
  - 数据治理：TTL/归档策略、字段级加密（KMS）、访问审计表。

- LLM 工程
  - 提示词版本化与实验管理（A/B），引入模板库与参数对齐（temperature、max_tokens）。
  - 结构化输出契约：通过 JSON Schema/工具函数约束模型输出，减少回退解析与脆弱性（参考 `backend/app/agents/supervisor.py:124-156` 的回退解析）。
  - 质量评估：构建数据集与自动评测（准确性、一致性、工具调用正确率），形成基线。

- API 设计与契约
  - 统一请求/响应模型（Pydantic），明确错误码与错误体结构，提供 `trace_id` 与 `request_id`。
  - 流式响应：SSE/WebSocket 支持实时输出，前端优化体验（打字机效果/逐步日志）。
  - 版本管理：在路径或头中声明 `v1/v2`，兼容演进。

- 前端工程化
  - 环境配置与 API 基地址通过 `.env` 注入，区分 dev/prod；统一错误/重试/超时策略。
  - 体验优化：流式显示、消息分组、系统状态板（模型延迟/工具调用日志），前端错误兜底与重试提示。
  - 安全：XSS/CSRF 防护、依赖锁定与供应链安全；静态资源缓存策略。

- 测试与质量保障
  - 后端：`pytest` 单元测试（工具）、集成测试（图与路由）、契约测试（API）。
  - 前端：`vitest`/`react-testing-library` 组件测试；`playwright` E2E（端到端）测试。
  - 静态检查：`ruff`/`black`/`mypy`（Python），`eslint`/`prettier`（JS）。引入 `pre-commit` 钩子。

- CI/CD 与部署
  - 制品化：Docker 镜像与多阶段构建，`docker-compose` 开发，Kubernetes/Helm 部署。
  - 流水线：Lint/Tests/安全扫描/构建/部署，支持预览环境与回滚（蓝绿/金丝雀）。
  - 配置与秘钥：使用环境注入与密文挂载，按环境分层。

- 成本与性能
  - 模型选择与降级：按场景动态选择模型与上下文长度，失败自动回退；缓存常见问答与工具结果。
  - 速率限制与配额：基于用户/租户的限流（Redis），防滥用与成本爆炸。
  - 性能分析：采集热点与瓶颈（序列化/网络/提示词长度），针对性优化。

### 关键代码位置（用于改造时快速定位）
- CORS 配置与服务入口：`backend/app/main.py:23-29`
- 内存会话状态：`backend/app/main.py:31-32`
- LangGraph 构建与编译：`backend/app/graph.py:7-21`
- 监督智能体模型与提示：`backend/app/agents/supervisor.py:28`、`backend/app/agents/supervisor.py:41-72`
- 回退解析逻辑（可用 Schema 约束替换）：`backend/app/agents/supervisor.py:124-156`
- 子智能体工厂与模型选择：`backend/app/utils/factory.py:36-67`
- 工具注册表：`backend/app/tools/registry.py:1-16`
- 前端调用后端的请求路径与展示：`frontend/src/App.jsx:12-18`、`frontend/src/App.jsx:34-57`

### 实施路线图（示例，约 6–12 周）
- 第 0 阶段（基线加固，1 周）
  - 收敛 CORS 与日志格式化，添加基础健康检查与 `/metrics`。
  - 引入 `ruff/black/mypy` 与 `eslint/prettier`，建立最小 CI。
- 第 1 阶段（状态外置与鉴权，2–3 周）
  - 会话与 LangGraph checkpoint 迁移至 Redis/DB；加 API Key/JWT 与 RBAC。
  - 建立 Sentry 与基本指标看板。
- 第 2 阶段（LLM 工程与契约化，2–3 周）
  - Prompt 版本化、JSON Schema 输出契约、流式响应；评测集与自动评估。
- 第 3 阶段（规模化与合规，2–4 周）
  - 容器化与 K8s 部署、告警与扩缩容、RAG 与数据治理落地。

> 以上为可执行的改造清单与路径，结合业务场景与预算可裁剪与排列优先级。

## 幻觉治理评估与引入建议

### 总览
- 核心目标：降低编造与不可靠输出，确保“只来自已知来源/工具”的可验证结果。
- 项目当前基础：已采用 ReAct 工程（工具优先）、提示禁止编造（`backend/app/config.py:18-35`、`backend/app/config.py:40-57`），并在日历等操作要求“先工具成功后声明”（`backend/app/config.py:40-57`）。监督输出当前存在“文本回退解析”的脆弱环节（`backend/app/agents/supervisor.py:124-156`）。

### 方案一：结构化输出与契约约束（强烈推荐，P0）
- 原理：通过 JSON Schema/类型约束让模型只产出结构化内容；解析失败时自动重试或降级。
- 适配点：
  - 监督智能体输出契约：替换回退正则解析，采用 JSON Schema + 验证重试（定位 `backend/app/agents/supervisor.py:124-156`）。
  - 子智能体输出契约：在 `create_react_agent` 层对工具与输出增加类型约束（定位 `backend/app/utils/factory.py:55-65`）。
- 引入方式：
  - 使用 Pydantic/JSON Schema 定义 `SupervisorResponse`（字段：`next`、`task_description_for_agent`、`message_completion_summary`）。
  - 对不合规输出进行“要求纠正”的二次调用，携带错误报告与目标 Schema。
- 成本与收益：实现成本低、收益显著；对现有代码影响最小。

### 方案二：检索增强（RAG）与来源引用（推荐，P1）
- 原理：将生成限制在检索到的知识子集；输出携带来源引用，前端和后端可核查。
- 适配点：
  - 晚餐计划：将菜谱从内存 Map 迁移到向量库/数据库，子智能体只能基于检索结果生成（定位 `backend/app/tools/meal_tools.py` 与 `backend/app/config.py:18-35`）。
  - 输出引用：在返回消息中附带 `source_id`/`document_id`，前端展示并支持点击回溯。
- 引入方式：
  - 向量库（PGVector/FAISS/Milvus）与检索器；在 `TOOLS_REGISTRY` 新增 `search_recipes(query)`（定位 `backend/app/tools/registry.py:1-16`）。
  - 提示更新为“仅基于检索结果，必须附带来源”。
- 成本与收益：需数据工程与部署；显著降低编造并提升可审计性。

### 方案三：工具调用验证闭环（已部分具备，P0）
- 原理：所有可执行声明前必须有工具成功调用的证据；失败时返回需要信息或报错。
- 适配点：
  - 日历添加：已在提示中声明工具成功才可宣称已安排（定位 `backend/app/config.py:40-57`）。
  - 通用扩展：为 notion/shopping 等工具统一添加“检查器”，当工具返回异常或为空时强制继续询问或回退。
- 引入方式：
  - 在 `TOOLS_REGISTRY` 结果上添加轻量校验器（非空、字段范围、重复判定），不通过则拒绝生成“完成”结论（定位 `backend/app/tools/registry.py:1-16`）。
  - 在监督节点引入“工具成功标志”检查，未达标不允许 `FINISH`（定位 `backend/app/agents/supervisor.py:41-72`）。
- 成本与收益：改动小、收益稳定；与结构化契约互补。

### 方案四：不确定性表达与动作门控（推荐，P1）
- 原理：要求模型在输出中给出“置信度/不确定性原因”，并据此决定是否继续检索或请求澄清；对关键操作（写/改）增加门控。
- 适配点：
  - 监督输出新增 `confidence` 与 `uncertainty_reason` 字段，并在低置信度时自动走检索或向用户确认。
  - 前端交互：当置信度低于阈值时弹窗确认再执行。
- 引入方式：
  - 提示规范中明确“遇到缺失信息要说明不确定性并主动请求工具/确认”（定位 `backend/app/agents/supervisor.py:41-72`）。
  - 在后端根据置信度阈值切换路由策略（继续子任务→检索→人工确认）。
- 成本与收益：实现中等；对体验提升明显，减少“硬编造”。

### 方案五：多样化采样与判官机制（可选，P2）
- 原理：对同一任务生成多份候选（自一致/辩论），再由判官模型或规则选优与合并。
- 适配点：
  - 监督节点：对关键任务（如计划/总结）进行 N 次生成，再由“判官智能体”评审（新增节点）。
  - 子智能体：对菜谱推荐做多样化采样，判官从来源一致性与工具核验角度评分。
- 引入方式：
  - 在 LangGraph 中新增 `judge` 节点与路由，判官使用严格提示与规则，输出评分与选择理由。
- 成本与收益：成本较高、延迟上升；在关键场景能显著降低错误率。

### 方案六：解码与温度控制（基础项，P0）
- 原理：通过低温度、受限采样（`temperature/top_p`）减少自由生成与编造。
- 适配点：
  - 在 ChatTongyi 初始化时设置 `temperature=0.2~0.3`（定位 `backend/app/utils/factory.py:54`、`backend/app/agents/supervisor.py:28`）。
- 引入方式：
  - 在 `ChatTongyi(..., model_kwargs={...})` 中追加温度与相关采样参数。
- 成本与收益：成本极低；对幻觉有直接抑制效果，但可能略降创造性。

### 方案七：来源引用与“我不知道”策略（基础项，P0）
- 原理：对非工具来源的知识要求显式“我不知道/需要更多信息”；对工具来源必须携带引用。
- 适配点：
  - 在所有提示中明确“不得编造，信息不足时返回需要的信息”，并将其上升为强提示与校验项（定位 `backend/app/config.py:18-35`、`backend/app/config.py:40-57`）。
  - 前端对“我不知道”做友好引导，允许补充信息或改写请求。
- 引入方式：
  - 监督节点在低置信度或无工具证据时，默认给出“我不知道”并触发澄清或检索。
- 成本与收益：改动小；能显著减少虚构。

### 方案八：领域校验器（基础项，P0）
- 原理：为领域结果定义可编程校验（日期区间、菜谱存在性、重复检测），用规则拒绝不合规输出。
- 适配点：
  - 日历时间合法性、跨日事件范围、标题规范等；菜谱必须存在且食材完整。
- 引入方式：
  - 在工具返回后做校验，失败则要求模型修正或重新调用工具（定位 `backend/app/tools/registry.py:1-16`）。
- 成本与收益：成本低；与契约/工具验证形成闭环。

### 方案九：日志概率/置信门控（条件支持，P2）
- 原理：若模型支持 `logprobs` 或置信度接口，则对低置信 token/段落进行二次确认或重写。
- 适配点：
  - ChatTongyi 若提供相关接口，可在关键输出处进行门控；否则可用替代特征（长度、矛盾、来源缺失）。
- 引入方式：
  - 在生成阶段或后处理阶段根据门控特征触发重试/检索/人工确认。
- 成本与收益：依赖模型支持；对关键场景有价值。

### 优先级与落地建议
- P0 立即落地：结构化输出契约、工具验证闭环、温度控制、领域校验器、“我不知道”策略。
- P1 中期引入：RAG 与来源引用、不确定性表达与门控。
- P2 条件引入：多样化采样 + 判官、日志概率门控。

### 关键代码定位（用于实施）
- 监督输出契约与重试：`backend/app/agents/supervisor.py:124-156`
- 子智能体创建与参数：`backend/app/utils/factory.py:54-56`
- 提示与“不得编造”：`backend/app/config.py:18-35`、`backend/app/config.py:40-57`
- 工具注册与统一校验器：`backend/app/tools/registry.py:1-16`
- 前端交互与二次确认：`frontend/src/App.jsx:24-33`、`frontend/src/App.jsx:34-57`
