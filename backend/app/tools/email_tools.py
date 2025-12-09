"""邮件工具（内存模拟）：发送邮件、查询、打标签与草稿管理。"""

import logging
from langchain_core.tools import tool
logger = logging.getLogger(__name__)

MOCK_EMAILS = [
    {"id": "m1", "snippet": "项目更新：请查看附件", "labelIds": ["work"], "body": "本周完成了模块A的开发。"},
    {"id": "m2", "snippet": "促销活动：冬季特价", "labelIds": ["marketing"], "body": "全场八折，点击查看详情。"},
]
MOCK_SENT = []
MOCK_DRAFTS = []
MOCK_LABELS = {"work": "work", "personal": "personal", "marketing": "marketing"}

@tool
def send_email(to_email: str, subject: str, body: str):
    """发送邮件并返回已发送的邮件对象。"""
    sent_message = {"to": to_email, "subject": subject, "body": body, "id": f"s{len(MOCK_SENT)+1}"}
    MOCK_SENT.append(sent_message)
    logger.info("send_email to=%s subject_length=%d", to_email, len(subject))
    return sent_message

@tool
def check_emails(query: str = "", max_results: int = 10, only_unlabeled: bool = False):
    """查询邮件列表，可选过滤未打标签邮件。"""
    logger.info("check_emails query=%s max_results=%d only_unlabeled=%s", query, max_results, only_unlabeled)
    emails = MOCK_EMAILS[:max_results]
    if only_unlabeled:
        emails = [email for email in emails if not email.get("labelIds")]
    logger.info("check_emails returned=%d", len(emails))
    return {"emails": emails}

@tool
def label_email(message_id: str, label: str):
    """为指定邮件打标签，返回更新后的邮件。"""
    logger.info("label_email id=%s label=%s", message_id, label)
    label_id = MOCK_LABELS.get(label)
    for email_message in MOCK_EMAILS:
        if email_message["id"] == message_id and label_id:
            labels = email_message.get("labelIds", [])
            if label_id not in labels:
                labels.append(label_id)
            email_message["labelIds"] = labels
            logger.info("label_email updated labels=%s", labels)
            return email_message
    logger.info("label_email not found")
    return {"error": "message or label not found"}

@tool
def create_draft(to_email: str, subject: str, body: str):
    """创建邮件草稿，返回草稿对象。"""
    draft = {"to": to_email, "subject": subject, "body": body, "id": f"d{len(MOCK_DRAFTS)+1}"}
    MOCK_DRAFTS.append(draft)
    logger.info("create_draft to=%s subject_length=%d", to_email, len(subject))
    return draft
