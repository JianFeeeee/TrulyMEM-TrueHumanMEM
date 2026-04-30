"""
活动记录器 - 记录 AI 对图数据库的操作
使用 SQLite :memory: 供 WebUI 实时渲染，同时后台线程持久化到日志文件
日志每 6 小时自动压缩归档
"""

import sqlite3
import time
import os
import gzip
import json
import threading
import shutil
from typing import List, Dict, Optional
from datetime import datetime, timedelta


# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
# 归档间隔（秒）
ARCHIVE_INTERVAL = 6 * 3600  # 6 小时
# 轮询间隔（秒）
POLL_INTERVAL = 10


class ActivityRecorder:
    """记录 AI 对图数据库的操作到内存 SQLite"""

    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.execute(
            "CREATE TABLE activities (id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "timestamp REAL, action TEXT, tool_name TEXT, entity TEXT, detail TEXT)"
        )
        self.conn.commit()

    def record(self, action: str, tool_name: str, entity: str, detail: str = "") -> None:
        self.conn.execute(
            "INSERT INTO activities (timestamp, action, tool_name, entity, detail) VALUES (?, ?, ?, ?, ?)",
            (time.time(), action, tool_name, entity, detail)
        )
        self.conn.commit()

    def get_all(self) -> List[Dict]:
        cursor = self.conn.execute(
            "SELECT id, timestamp, action, tool_name, entity, detail FROM activities ORDER BY id"
        )
        rows = cursor.fetchall()
        return [
            {"id": r[0], "timestamp": r[1], "action": r[2],
             "tool_name": r[3], "entity": r[4], "detail": r[5]}
            for r in rows
        ]

    def get_since_id(self, last_id: int) -> List[Dict]:
        """获取自 last_id 之后的新记录"""
        cursor = self.conn.execute(
            "SELECT id, timestamp, action, tool_name, entity, detail FROM activities WHERE id > ? ORDER BY id",
            (last_id,)
        )
        rows = cursor.fetchall()
        return [
            {"id": r[0], "timestamp": r[1], "action": r[2],
             "tool_name": r[3], "entity": r[4], "detail": r[5]}
            for r in rows
        ]

    def get_max_id(self) -> int:
        cursor = self.conn.execute("SELECT COALESCE(MAX(id), 0) FROM activities")
        return cursor.fetchone()[0]

    def clear(self) -> None:
        self.conn.execute("DELETE FROM activities")
        self.conn.commit()

    def get_summary(self) -> Dict[str, int]:
        cursor = self.conn.execute("SELECT action, COUNT(*) FROM activities GROUP BY action")
        rows = cursor.fetchall()
        return {r[0]: r[1] for r in rows}


# ── 日志文件管理 ──

def _current_log_path() -> str:
    """返回当前日志文件路径（按日期命名）"""
    os.makedirs(LOG_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    return os.path.join(LOG_DIR, f"operations.{date_str}.log")


def _archive_log(filepath: str) -> str:
    """压缩归档日志文件，返回归档文件路径"""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return ""
    archive_path = filepath + ".gz"
    try:
        with open(filepath, "rb") as f_in:
            with gzip.open(archive_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(filepath)
        return archive_path
    except Exception:
        return ""


class LogPersister:
    """后台日志持久化线程 - 定期将内存记录写入日志文件并自动归档"""

    def __init__(self, recorder: ActivityRecorder):
        self.recorder = recorder
        self._last_persisted_id = 0
        self._last_archive_time = time.time()
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="log-persister")
        self._thread.start()

    def _run(self):
        """主循环"""
        while self._running:
            try:
                self._persist_new()
                self._check_archive()
            except Exception:
                pass  # 不因日志异常影响主进程
            time.sleep(POLL_INTERVAL)

    def _persist_new(self):
        """增量写入新记录到日志文件"""
        records = self.recorder.get_since_id(self._last_persisted_id)
        if not records:
            return

        log_path = _current_log_path()
        with open(log_path, "a", encoding="utf-8") as f:
            for r in records:
                line = json.dumps(r, ensure_ascii=False)
                f.write(line + "\n")

        # 更新水位
        if records:
            self._last_persisted_id = records[-1]["id"]

    def _check_archive(self):
        """检查是否需要归档"""
        elapsed = time.time() - self._last_archive_time
        if elapsed < ARCHIVE_INTERVAL:
            return

        log_path = _current_log_path()
        archived = _archive_log(log_path)
        if archived:
            dt = datetime.fromtimestamp(self._last_archive_time)
            print(f"[日志归档] {dt.strftime('%H:%M')} → {os.path.basename(archived)} ({_fmt_size(archived)})")
        self._last_archive_time = time.time()

    def stop(self):
        self._running = False


def _fmt_size(path: str) -> str:
    size = os.path.getsize(path)
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}GB"


# ── 单例 ──

_recorder: Optional[ActivityRecorder] = None
_persister: Optional[LogPersister] = None


def get_recorder() -> ActivityRecorder:
    """获取全局 ActivityRecorder（首次调用时自动启动日志持久化线程）"""
    global _recorder, _persister
    if _recorder is None:
        _recorder = ActivityRecorder()
        _persister = LogPersister(_recorder)
    return _recorder


def get_persister() -> Optional[LogPersister]:
    return _persister
