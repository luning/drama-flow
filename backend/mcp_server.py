#!/usr/bin/env python3
"""DramaFlow MCP Server — Read-only stats for content operators.

Implements MCP (Model Context Protocol) JSON-RPC 2.0 over stdio using only stdlib.
No external dependencies required — works with Python 3.9+.

Tools:
  - get_drama_stats: play count, rating, completion rate for a drama
  - get_user_watch_summary: recent dramas, completed count, total watch time

Usage: configure in Claude Code as an MCP server, or run directly for manual testing.
"""

import os
import sys
import json
import sqlite3
import asyncio
from pathlib import Path

DB_PATH = os.environ.get(
    "DRAMAFLOW_DB",
    str(Path(__file__).resolve().parent / "dramaflow.db"),
)

SERVER_NAME = "dramaflow-stats"
SERVER_VERSION = "1.0.0"


def query_db(sql: str, params: tuple = ()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


# ── Tool definitions ──────────────────────────────────────────────

TOOLS = [
    {
        "name": "get_drama_stats",
        "description": "查询指定剧集的播放量、评分和平均完播率。传入 drama_id，返回该剧集的统计数据，包括播放次数、当前评分和完播率百分比。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "drama_id": {
                    "type": "integer",
                    "description": "剧集 ID（dramas 表主键）",
                }
            },
            "required": ["drama_id"],
        },
    },
    {
        "name": "get_user_watch_summary",
        "description": "查询用户近期观看记录摘要：最近观看的剧集列表、完播数量、累计观看时长。传入 user_id，返回该用户的观看行为统计。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "用户 ID（users 表主键）",
                }
            },
            "required": ["user_id"],
        },
    },
]


# ── Tool handlers ─────────────────────────────────────────────────

def handle_get_drama_stats(args: dict) -> str:
    drama_id = args["drama_id"]

    drama_rows = query_db(
        "SELECT id, title, rating FROM dramas WHERE id = ?", (drama_id,)
    )
    if not drama_rows:
        return f"剧集不存在：未找到 ID 为 {drama_id} 的剧集。"

    drama = drama_rows[0]

    play_rows = query_db(
        "SELECT COUNT(*) AS cnt FROM watch_records wr "
        "JOIN episodes e ON wr.episode_id = e.id "
        "WHERE e.drama_id = ?",
        (drama_id,),
    )
    play_count = play_rows[0]["cnt"]

    comp_rows = query_db(
        "SELECT "
        "  COUNT(*) AS total, "
        "  SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) AS completed_count "
        "FROM watch_records wr "
        "JOIN episodes e ON wr.episode_id = e.id "
        "WHERE e.drama_id = ?",
        (drama_id,),
    )
    total_records = comp_rows[0]["total"]
    completed_count = comp_rows[0]["completed_count"]
    completion_rate = (
        round(completed_count * 100.0 / total_records, 1) if total_records > 0 else 0.0
    )

    avg_rows = query_db(
        "SELECT ROUND(AVG(wr.progress), 1) AS avg_progress "
        "FROM watch_records wr "
        "JOIN episodes e ON wr.episode_id = e.id "
        "WHERE e.drama_id = ?",
        (drama_id,),
    )
    avg_progress = avg_rows[0]["avg_progress"] or 0.0

    result = {
        "drama_id": drama_id,
        "title": drama["title"],
        "rating": round(drama["rating"], 1),
        "play_count": play_count,
        "completion_rate_pct": completion_rate,
        "avg_progress_pct": avg_progress,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def handle_get_user_watch_summary(args: dict) -> str:
    user_id = args["user_id"]

    user_rows = query_db(
        "SELECT id, nickname, email FROM users WHERE id = ?", (user_id,)
    )
    if not user_rows:
        return f"用户不存在：未找到 ID 为 {user_id} 的用户。"

    user = user_rows[0]

    recent = query_db(
        "SELECT DISTINCT d.id, d.title, d.rating, MAX(wr.updated_at) AS last_watched "
        "FROM watch_records wr "
        "JOIN episodes e ON wr.episode_id = e.id "
        "JOIN dramas d ON e.drama_id = d.id "
        "WHERE wr.user_id = ? "
        "GROUP BY d.id "
        "ORDER BY last_watched DESC "
        "LIMIT 10",
        (user_id,),
    )

    comp_rows = query_db(
        "SELECT COUNT(*) AS cnt FROM watch_records WHERE user_id = ? AND completed = 1",
        (user_id,),
    )
    completed_count = comp_rows[0]["cnt"]

    dur_rows = query_db(
        "SELECT COALESCE(SUM(last_position), 0) AS total_seconds "
        "FROM watch_records WHERE user_id = ?",
        (user_id,),
    )
    total_seconds = int(dur_rows[0]["total_seconds"])
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    result = {
        "user_id": user_id,
        "nickname": user["nickname"],
        "email": user["email"],
        "total_watched_dramas": len(recent),
        "completed_episodes": completed_count,
        "total_watch_time": f"{hours}h {minutes}m ({total_seconds}s)",
        "total_watch_seconds": total_seconds,
        "recently_watched": [
            {
                "drama_id": r["id"],
                "title": r["title"],
                "rating": round(r["rating"], 1),
                "last_watched": r["last_watched"],
            }
            for r in recent
        ],
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


TOOL_HANDLERS = {
    "get_drama_stats": handle_get_drama_stats,
    "get_user_watch_summary": handle_get_user_watch_summary,
}


# ── JSON-RPC 2.0 over stdio ───────────────────────────────────────

def make_response(id_, result):
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def make_error(id_, code, message):
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}


async def run_mcp():
    """MCP main loop: read JSON-RPC from stdin, write responses to stdout."""
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    loop = asyncio.get_event_loop()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    def write_json(data: dict):
        line = json.dumps(data, ensure_ascii=False)
        sys.stdout.write(line + "\n")
        sys.stdout.flush()

    while True:
        try:
            line = await reader.readline()
        except EOFError:
            break
        if not line:
            break

        try:
            request = json.loads(line.decode("utf-8"))
        except json.JSONDecodeError:
            continue

        req_id = request.get("id")
        method = request.get("method", "")
        params = request.get("params", {})

        if method == "initialize":
            write_json(make_response(req_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION,
                },
            }))

        elif method == "notifications/initialized":
            pass  # no response for notifications

        elif method == "tools/list":
            write_json(make_response(req_id, {"tools": TOOLS}))

        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            handler = TOOL_HANDLERS.get(tool_name)
            if handler:
                try:
                    text = handler(tool_args)
                    write_json(make_response(req_id, {
                        "content": [{"type": "text", "text": text}],
                    }))
                except Exception as e:
                    write_json(make_response(req_id, {
                        "content": [{"type": "text", "text": f"工具执行出错: {e}"}],
                        "isError": True,
                    }))
            else:
                write_json(make_error(req_id, -32601, f"Unknown tool: {tool_name}"))

        elif req_id is not None:
            # Only respond to unrecognized methods that expect a response (have an id)
            write_json(make_error(req_id, -32601, f"Method not found: {method}"))


if __name__ == "__main__":
    asyncio.run(run_mcp())
