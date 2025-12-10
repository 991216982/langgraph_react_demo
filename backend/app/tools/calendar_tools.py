"""日历工具：在内存中模拟查询与添加日历事件。"""

import logging
from datetime import datetime, timedelta
from langchain_core.tools import tool
logger = logging.getLogger(__name__)

MOCK_EVENTS = {
    "family": [
        {"summary": "家庭晚餐：意大利面", "start": {"dateTime": "2025-12-10T18:00:00+01:00"}, "end": {"dateTime": "2025-12-10T19:00:00+01:00"}, "description": "番茄酱与罗勒"},
    ],
    "personal": [
        {"summary": "健身训练", "start": {"dateTime": "2025-12-10T07:30:00+01:00"}, "end": {"dateTime": "2025-12-10T08:30:00+01:00"}, "description": "力量训练"},
    ],
    "work": [
        {"summary": "季度汇报会", "start": {"dateTime": "2025-12-11T10:00:00+01:00"}, "end": {"dateTime": "2025-12-11T11:00:00+01:00"}, "description": "准备PPT"},
    ],
}

CALENDAR_NAME_ALIASES = {
    "家庭日历": "family",
    "家庭": "family",
    "家": "family",
    "个人": "personal",
    "个人日历": "personal",
    "工作": "work",
    "工作日历": "work",
}

def _normalize_calendar_name(name: str) -> str:
    if not name:
        return name
    return CALENDAR_NAME_ALIASES.get(name.strip(), name.strip())

def _parse_any_datetime(dt):
    if isinstance(dt, datetime):
        return dt
    if isinstance(dt, str):
        text = dt.strip()
        if text in ("今天", "today"):
            now = datetime.now()
            return datetime(now.year, now.month, now.day, 18, 0, 0)
        if text in ("明天", "tomorrow"):
            now = datetime.now()
            return datetime(now.year, now.month, now.day, 18, 0, 0) + timedelta(days=1)
        try:
            return datetime.fromisoformat(text)
        except Exception:
            pass
        try:
            return datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
        try:
            return datetime.strptime(text, "%Y-%m-%d")
        except Exception:
            logger.info("无法解析日期时间: %s", dt)
            return datetime.now()
    return datetime.now()

@tool
def get_current_date_and_time():
    """获取当前日期时间与星期信息。"""
    now = datetime.now()
    result = {"datetime": now.strftime("%Y-%m-%d %H:%M:%S"), "day_of_the_week": now.strftime("%A")}
    logger.info("获取当前时间 %s 星期=%s", result["datetime"], result["day_of_the_week"]) 
    return result

@tool
def get_calendar_events(startDate: str = None, endDate: str = None):
    """返回当前内存中的所有日历事件。

    参数:
        startDate: 起始日期（保留参数，当前未过滤）。
        endDate: 结束日期（保留参数，当前未过滤）。
    """
    logger.info("获取日历事件 起始=%s 结束=%s", startDate, endDate)
    events = []
    for calendar_id in MOCK_EVENTS:
        for event in MOCK_EVENTS[calendar_id]:
            events.append({"calendarId": calendar_id, **event})
    logger.info("获取日历事件 返回数量=%d", len(events))
    return events

@tool
def create_calendar(calendar_name: str):
    """创建新的日历（内存），若已存在则直接返回。"""
    normalized = _normalize_calendar_name(calendar_name)
    if normalized not in MOCK_EVENTS:
        MOCK_EVENTS[normalized] = []
        logger.info("创建日历 成功=%s 原称=%s", normalized, calendar_name)
    else:
        logger.info("创建日历 已存在=%s", normalized)
    return {"calendar": normalized}

@tool
def add_calendar_event(startDate: datetime, endDate: datetime, calendar_name: str, title: str, description: str):
    """向指定日历添加事件，并返回创建的事件。"""
    normalized = _normalize_calendar_name(calendar_name)
    start_dt = _parse_any_datetime(startDate)
    end_dt = _parse_any_datetime(endDate)
    if normalized not in MOCK_EVENTS:
        MOCK_EVENTS[normalized] = []
        logger.info("自动创建日历=%s 原称=%s", normalized, calendar_name)
    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start_dt.isoformat()},
        "end": {"dateTime": end_dt.isoformat()},
    }
    MOCK_EVENTS[normalized].append(event)
    logger.info("添加事件 日历=%s 标题=%s 开始=%s 结束=%s", normalized, title[:50], event["start"]["dateTime"], event["end"]["dateTime"])
    return event
