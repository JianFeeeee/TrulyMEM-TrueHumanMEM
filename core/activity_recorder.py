import sqlite3
import time
from typing import List, Dict, Optional


class ActivityRecorder:
    """记录 AI 对图数据库的操作到内存 SQLite"""

    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.execute("CREATE TABLE activities (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp REAL, action TEXT, tool_name TEXT, entity TEXT, detail TEXT)")
        self.conn.commit()

    def record(self, action: str, tool_name: str, entity: str, detail: str = "") -> None:
        self.conn.execute("INSERT INTO activities (timestamp, action, tool_name, entity, detail) VALUES (?, ?, ?, ?, ?)",
                          (time.time(), action, tool_name, entity, detail))
        self.conn.commit()

    def get_all(self) -> List[Dict]:
        cursor = self.conn.execute("SELECT id, timestamp, action, tool_name, entity, detail FROM activities ORDER BY id")
        rows = cursor.fetchall()
        return [{"id": r[0], "timestamp": r[1], "action": r[2], "tool_name": r[3], "entity": r[4], "detail": r[5]} for r in rows]

    def clear(self) -> None:
        self.conn.execute("DELETE FROM activities")
        self.conn.commit()

    def get_summary(self) -> Dict[str, int]:
        cursor = self.conn.execute("SELECT action, COUNT(*) FROM activities GROUP BY action")
        rows = cursor.fetchall()
        return {r[0]: r[1] for r in rows}


_recorder: Optional[ActivityRecorder] = None


def get_recorder() -> ActivityRecorder:
    global _recorder
    if _recorder is None:
        _recorder = ActivityRecorder()
    return _recorder
