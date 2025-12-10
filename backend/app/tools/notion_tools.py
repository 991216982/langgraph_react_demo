"""Notion 工具（内存模拟）：管理购物清单与 Mind Base。"""

import logging
from langchain_core.tools import tool
logger = logging.getLogger(__name__)

MOCK_SHOPPING_LIST = ["意面", "番茄", "罗勒", "鸡胸肉"]
MOCK_MIND_BASE = []

@tool
def get_shopping_list():
    """获取未完成的购物清单。"""
    logger.info("获取购物清单 数量=%d 项目=%s", len(MOCK_SHOPPING_LIST), ",".join(MOCK_SHOPPING_LIST))
    return MOCK_SHOPPING_LIST

@tool
def add_entry_to_mindbase(entryContent: str, entryType: str):
    """向 Mind Base 添加一条记录。"""
    item = {"content": entryContent, "type": entryType}
    MOCK_MIND_BASE.append(item)
    logger.info("写入Mind Base 类型=%s 内容长度=%d 总条目=%d", entryType, len(entryContent), len(MOCK_MIND_BASE))
    return item

@tool
def add_to_shopping_list(data: list):
    """批量添加购物项。"""
    for item in data:
        MOCK_SHOPPING_LIST.append(item)
    logger.info("批量添加购物项 新增=%d 总数=%d", len(data), len(MOCK_SHOPPING_LIST))
    return {"added": data, "total": len(MOCK_SHOPPING_LIST)}
