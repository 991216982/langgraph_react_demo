"""联系人工具（内存模拟）：提供联系人列表与单项查询。"""

import logging
from langchain_core.tools import tool
logger = logging.getLogger(__name__)

MOCK_CONTACTS = [
    {"name": "张三", "email": "zhangsan@example.com"},
    {"name": "李四", "email": "lisi@example.com"},
]

@tool
def get_contacts():
    """返回联系人列表。"""
    logger.info("get_contacts called, count=%d", len(MOCK_CONTACTS))
    return MOCK_CONTACTS

@tool
def get_single_contact(query: str):
    """根据姓名或邮箱查询单个联系人。"""
    logger.info("get_single_contact query=%s", query)
    for contact in MOCK_CONTACTS:
        if contact["name"] == query or contact["email"] == query:
            logger.info("get_single_contact found")
            return contact
    logger.info("get_single_contact not found")
    return {"error": "not found"}
