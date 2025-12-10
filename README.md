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
