"""回归测试：已落盘的新读数必须立刻在列表可见；整理态不得粘住；非记录员不可写。"""

import asyncio
import os
import sys
from datetime import datetime, timezone

import jwt
from aiohttp.test_utils import TestClient, TestServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import api  # noqa: E402


def _row(id_, **over):
    row = {
        "id": id_,
        "probe_id": f"探头{id_:02d}",
        "temp_c": 5.0,
        "verdict": "合格",
        "reason": "探头温度未超过 8℃ 上限",
        "status": "done",
        "created_by": "logger",
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "processed_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    row.update(over)
    return row


class _FakePool:
    def __init__(self, rows):
        self.rows = list(rows)

    async def fetch(self, _sql, *_args):
        return list(self.rows)

    async def fetchrow(self, _sql, *args):
        new = _row(
            max((r["id"] for r in self.rows), default=0) + 1,
            probe_id=args[0],
            temp_c=args[1],
            verdict=None,
            reason=None,
            status="pending",
            created_by=args[2],
            processed_at=None,
        )
        self.rows.insert(0, new)
        return new


def _token(username, role):
    return jwt.encode({"sub": username, "role": role}, api.SECRET, algorithm="HS256")


async def _with_client(rows, fn):
    app = api.create_app()
    app.on_startup.clear()
    app.on_cleanup.clear()
    pool = _FakePool(rows)
    app["pool"] = pool
    client = TestClient(TestServer(app))
    await client.start_server()
    try:
        await fn(client, pool)
    finally:
        await client.close()


def test_list_includes_newest_reading():
    """列表不得滤掉最新一条（max id 必须可见）。"""

    async def main(client, _pool):
        resp = await client.get(
            "/api/readings",
            headers={"Authorization": f"Bearer {_token('watcher', 'reader')}"},
        )
        assert resp.status == 200
        data = await resp.json()
        assert [r["id"] for r in data] == [3, 2, 1]

    asyncio.run(_with_client([_row(3), _row(2), _row(1)], main))


def test_submit_then_refresh_shows_new_id():
    """提交回包成功后，刷新列表必须立刻能看到新编号。"""

    async def main(client, _pool):
        resp = await client.post(
            "/api/readings",
            json={"probe_id": "探头T99", "temp_c": 5.0},
            headers={"Authorization": f"Bearer {_token('logger', 'writer')}"},
        )
        assert resp.status == 201
        created = await resp.json()
        new_id = created["id"]

        resp = await client.get(
            "/api/readings",
            headers={"Authorization": f"Bearer {_token('logger', 'writer')}"},
        )
        assert resp.status == 200
        ids = [r["id"] for r in await resp.json()]
        assert new_id in ids, f"新编号 {new_id} 未出现在列表 {ids}"

    asyncio.run(_with_client([_row(2), _row(1)], main))


def test_reader_cannot_write():
    """非记录员（值班员）提交读数必须被拒。"""

    async def main(client, pool):
        resp = await client.post(
            "/api/readings",
            json={"probe_id": "探头X01", "temp_c": 5.0},
            headers={"Authorization": f"Bearer {_token('watcher', 'reader')}"},
        )
        assert resp.status == 403
        assert len(pool.rows) == 2  # 未写入

    asyncio.run(_with_client([_row(2), _row(1)], main))
