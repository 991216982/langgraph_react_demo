"""联系人工具（内存模拟）：提供联系人列表与单项查询。"""

from langchain_core.tools import tool

MOCK_CONTACTS = [
    {"name": "张三", "email": "zhangsan@example.com"},
    {"name": "李四", "email": "lisi@example.com"},
]

@tool
def get_contacts():
    """返回联系人列表。"""
    return MOCK_CONTACTS

@tool
def get_single_contact(query: str):
    """根据姓名或邮箱查询单个联系人。"""
    for contact in MOCK_CONTACTS:
        if contact["name"] == query or contact["email"] == query:
            return contact
    return {"error": "not found"}
