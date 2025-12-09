"""餐食工具（内存模拟）：提供菜谱与人类确认接口。"""

import logging
from langchain_core.tools import tool
logger = logging.getLogger(__name__)

MOCK_RECIPES = [
    {"name": "番茄意面", "ingredients": ["意面", "番茄", "蒜", "罗勒"]},
    {"name": "鱼塔可", "ingredients": ["鱼片", "玉米饼", "卷心菜", "酸奶"]},
]

@tool
def get_recipes():
    """返回可选菜谱及其食材。"""
    logger.info("get_recipes count=%d", len(MOCK_RECIPES))
    return {"data": MOCK_RECIPES}

@tool
def human_feedback(query: str):
    """模拟人类确认流程，返回统一的确认结果。"""
    logger.info("human_feedback query_length=%d", len(query))
    return {"feedback": "已确认"}
