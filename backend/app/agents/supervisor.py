"""监督智能体定义：拆解任务并将子任务分派给合适的子智能体。"""

import logging
import json
import re
from typing import Literal
from typing_extensions import TypedDict
import os
from langchain_community.chat_models.tongyi import ChatTongyi
from langgraph.graph import MessagesState, END
from langgraph.types import Command
from ..config import AGENTS, MEMBERS

agent_members_prompt = []
# 汇总成员智能体的描述与工具，注入到系统提示中作为参考
for key, data in AGENTS.items():
    if data["name"] in MEMBERS:
        agent_members_prompt.append(f"{data['name']}: {data['description']}")
        for tool_description in data.get("tools", []):
            agent_members_prompt.append(f"- {tool_description}")
        agent_members_prompt.append("")
agent_members_prompt_final = "\n".join(agent_members_prompt)

logger = logging.getLogger(__name__)
if not os.environ.get("DASHSCOPE_API_KEY"):
    logger.error("DASHSCOPE_API_KEY 未设置")
    raise RuntimeError("DASHSCOPE_API_KEY 未设置")
supervisor_llm = ChatTongyi(model="qwen3-max", model_kwargs={"enable_thinking": False})

class State(MessagesState):
    """监督态的消息状态，包含下一跳智能体标识。"""
    next: str
    supervisor_loops: int
    supervisor_repeat_count: int

class SupervisorOutput(TypedDict):
    """监督模型的结构化输出。"""
    next: Literal["calendar_agent", "notion_agent", "meal_planner_agent", "FINISH"]
    task_description_for_agent: str
    message_completion_summary: str

supervisor_system_prompt = f"""
# 角色
你是家用助理的监督智能体。你的职责是理解用户请求，拆解为子任务，并把每个子任务分派给最合适的子智能体，直到任务完成。

# 上下文
你可以使用以下 {len(MEMBERS)} 个子智能体：{MEMBERS}
每个子智能体的描述与工具如下：
{agent_members_prompt_final}

# 目标
分析用户请求，拆分子任务，逐步完成。为每个子任务生成清晰的中文指令并发送给对应子智能体。当全部完成时返回 next = FINISH。

# 操作指引
1. 理解用户目标。
2. 拆解为有序的子任务。
3. 为每个子任务选择最佳子智能体。
4. 下达指令时，只写该子任务需要的信息与预期输出，不提及其他智能体。
5. 评估子智能体返回是否完成该子任务，若未完成继续迭代。
6. 全部完成后，返回 FINISH。

# 重要
- 委派的任务内容写入 task_description_for_agent 字段。
- 对每次返回做出简短完成情况评估。

# 输出规范（必须严格遵守）
- 仅按结构化模式输出，不得输出额外文字。
- 字段：
  - next ∈ {{calendar_agent, notion_agent, meal_planner_agent, FINISH}}
  - task_description_for_agent: 中文指令，任务所需信息与预期输出，且只针对选定智能体
  - message_completion_summary: 上一步完成情况的简短中文评估
- 示例：
  {{"next": "calendar_agent", "task_description_for_agent": "添加事件……", "message_completion_summary": "已生成菜谱，待入日历"}}

# 完成判定规则（必须遵守）
- 当选定子智能体已完成其目标时，返回 next = FINISH。
- 判定信号：最近一次子智能体消息含有以下任一中文词/短语：
  - 已完成、完成、已添加、已创建、已确认、成功、已安排、已生成
- 针对具体智能体：
  - calendar_agent：事件已创建或已添加到指定日历；若提示日历不存在，应先创建再添加，完成后 FINISH。
  - meal_planner_agent：已给出具体菜名与食材的计划（无占位符），视为完成。
  - notion_agent：购物清单或 Mind Base 已成功更新（返回新增条目或总数变化），视为完成。
- 不得重复委派已完成的同一子任务；若重复，立即 FINISH。

# 路由关键词参考（辅助选择 next）
- calendar_agent：日历、事件、安排、添加、家庭日历、个人日历、工作日历、日程、schedule、event
- notion_agent：购物、清单、待办、笔记、Mind Base、列表、新增条目、notion、todo
- meal_planner_agent：晚餐、晚饭、餐食、食谱、菜谱、菜名、食材、meal、dinner、menu
"""

def _detect_route(text: str) -> str:
    t = (text or "").lower()
    completion_tokens = ["已完成", "完成", "已添加", "已创建", "已确认", "成功", "已安排", "已生成", "done", "success", "ok"]
    if any(tok.lower() in t for tok in completion_tokens):
        return "FINISH"
    if ("日历" in text) or ("事件" in text) or ("安排" in text) or ("添加" in text) or ("日程" in text) or ("schedule" in t) or ("event" in t) or ("家庭日历" in text) or ("个人日历" in text) or ("工作日历" in text):
        return "calendar_agent"
    if ("购物" in text) or ("清单" in text) or ("待办" in text) or ("笔记" in text) or ("mind base" in t) or ("列表" in text) or ("新增条目" in text) or ("notion" in t) or ("todo" in t):
        return "notion_agent"
    if ("晚餐" in text) or ("晚饭" in text) or ("餐食" in text) or ("食谱" in text) or ("菜谱" in text) or ("菜名" in text) or ("食材" in text) or ("meal" in t) or ("dinner" in t) or ("menu" in t):
        return "meal_planner_agent"
    return "FINISH"

def supervisor_node(state: State) -> Command[Literal["calendar_agent", "notion_agent", "meal_planner_agent", "__end__"]]:
    """监督节点：根据当前消息决定下一步路由并生成子任务指令。"""
    loops = int(state.get("supervisor_loops", 0)) + 1
    logger.info("监督节点接收%d条消息，循环=%d", len(state["messages"]), loops)
    if loops > 20:
        logger.warning("循环保护触发，结束")
        return Command(goto=END, update={"next": END, "supervisor_loops": loops})
    messages = [{"role": "system", "content": supervisor_system_prompt}] + state["messages"]
    if state["messages"]:
        lm = state["messages"][-1]
        logger.info("监督输入最后一条 role=%s 长度=%d 头部=%s", getattr(lm, "type", getattr(lm, "role", "")), len(getattr(lm, "content", "")), str(getattr(lm, "content", ""))[:200])
    response = None
    try:
        response = supervisor_llm.with_structured_output(SupervisorOutput).invoke(messages)
        if isinstance(response, dict):
            logger.info("结构化输出 next=%s 摘要长度=%d 指令长度=%d 指令头=%s", response.get("next"), len(response.get("message_completion_summary", "")), len(response.get("task_description_for_agent", "")), str(response.get("task_description_for_agent", ""))[:200])
        else:
            logger.warning("结构化输出返回非字典类型=%s", type(response).__name__)
    except Exception:
        logger.exception("结构化输出异常")
        response = None
    if not response or not isinstance(response, dict) or "next" not in response or "task_description_for_agent" not in response:
        raw = supervisor_llm.invoke(messages)
        raw_content = getattr(raw, "content", str(raw))
        logger.warning("结构化失败，回退解析，原始长度=%d 头部=%s", len(str(raw_content)), str(raw_content)[:200])
        text = str(raw_content)
        parsed = None
        try:
            m = re.search(r"\{[\s\S]*\}", text)
            if m:
                candidate = m.group(0)
                parsed = json.loads(candidate)
        except Exception:
            parsed = None
        if isinstance(parsed, dict) and "next" in parsed and "task_description_for_agent" in parsed:
            candidate_next = parsed.get("next")
            if candidate_next == "FINISH":
                route = _detect_route(text)
                candidate_next = route
            response = {
                "next": candidate_next,
                "task_description_for_agent": parsed.get("task_description_for_agent", ""),
                "message_completion_summary": parsed.get("message_completion_summary", ""),
            }
        else:
            route = _detect_route(text)
            response = {
                "next": route,
                "task_description_for_agent": text[:2000],
                "message_completion_summary": "fallback",
            }
    goto = response["next"]
    if goto == "FINISH":
        last_text = str(getattr(state["messages"][-1], "content", "")) if state["messages"] else ""
        tokens = ["已完成", "完成", "已添加", "已创建", "已确认", "成功", "已安排", "已生成", "done", "success", "ok"]
        if not any(tok.lower() in last_text.lower() for tok in tokens):
            alt_route = _detect_route(last_text)
            goto = alt_route if alt_route != "FINISH" else "meal_planner_agent"
            if not response.get("task_description_for_agent"):
                response["task_description_for_agent"] = last_text or "继续完成任务"
    logger.info("路由决策: 下一步=%s 摘要头=%s 指令头=%s", goto, str(response.get("message_completion_summary", ""))[:200], str(response.get("task_description_for_agent", ""))[:200])
    prev_next = state.get("next")
    repeat = int(state.get("supervisor_repeat_count", 0))
    if prev_next == goto:
        repeat += 1
    else:
        repeat = 0
    logger.info("路由状态: 上一步next=%s 当前next=%s 重复计数=%d 循环=%d", prev_next, goto, repeat, loops)
    if repeat >= 3:
        logger.warning("连续重复路由%s达到3次，结束", goto)
        return Command(goto=END, update={"next": END, "supervisor_repeat_count": repeat, "supervisor_loops": loops})
    if goto == "FINISH":
        logger.info("监督节点结束")
        return Command(goto=END, update={"next": END, "supervisor_repeat_count": repeat, "supervisor_loops": loops})
    # 将监督给出的子任务说明注入到消息流，交由目标子智能体处理
    new_messages = [{"role": "system", "content": response["task_description_for_agent"]}]
    logger.info("子任务说明长度=%d", len(response["task_description_for_agent"]))
    return Command(goto=goto, update={"next": goto, "messages": new_messages, "supervisor_repeat_count": repeat, "supervisor_loops": loops})
