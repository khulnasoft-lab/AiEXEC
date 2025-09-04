# Tests for helpers and fixtures defined in api/tests/conftest.py
# Testing stack: pytest + pytest-anyio-style async tests; logging via loguru integrated with pytest caplog through custom conftest fixture.

from __future__ import annotations

import os
import types
import uuid
import pytest

# Import the local conftest module loaded for this test package
import conftest as conf


@pytest.mark.anyio
async def test_delete_transactions_by_flow_id_returns_early_on_falsy_flow_id():
    class SentinelSession:
        async def exec(self, stmt):  # pragma: no cover - should never be called
            raise AssertionError("exec should not be called when flow_id is falsy")

        async def delete(self, obj):  # pragma: no cover - should never be called
            raise AssertionError("delete should not be called when flow_id is falsy")

    session = SentinelSession()

    # None
    await conf.delete_transactions_by_flow_id(session, None)
    # Empty string
    await conf.delete_transactions_by_flow_id(session, "")
    # Zero-like value
    await conf.delete_transactions_by_flow_id(session, 0)


@pytest.mark.anyio
async def test_delete_transactions_by_flow_id_deletes_all_transactions():
    txn1, txn2 = object(), object()

    class DummyAsyncSession:
        def __init__(self):
            self.deleted = []
            self.last_stmt = None

        async def exec(self, stmt):
            self.last_stmt = stmt
            # Return an awaitable that resolves to an iterable of transactions
            return [txn1, txn2]

        async def delete(self, obj):
            self.deleted.append(obj)

    session = DummyAsyncSession()
    flow_id = uuid.uuid4()

    await conf.delete_transactions_by_flow_id(session, flow_id)

    assert session.deleted == [txn1, txn2], "Should delete every returned transaction in order"
    assert session.last_stmt is not None, "Should issue a select statement with the provided flow_id"


@pytest.mark.anyio
async def test__delete_transactions_and_vertex_builds_calls_subfunctions_for_each_valid_flow_id(monkeypatch):
    calls: list[tuple[str, str, uuid.UUID]] = []

    async def fake_delete_vertex(session, flow_id):
        calls.append(("vb", session, flow_id))

    async def fake_delete_tx(session, flow_id):
        calls.append(("tx", session, flow_id))

    monkeypatch.setattr(conf, "delete_vertex_builds_by_flow_id", fake_delete_vertex)
    monkeypatch.setattr(conf, "delete_transactions_by_flow_id", fake_delete_tx)

    f1 = types.SimpleNamespace(id=uuid.uuid4())
    f_none = types.SimpleNamespace(id=None)  # should be skipped
    f2 = types.SimpleNamespace(id=uuid.uuid4())

    session = "SESSION"
    await conf._delete_transactions_and_vertex_builds(session, [f1, f_none, f2])

    expected = [
        ("vb", session, f1.id),
        ("tx", session, f1.id),
        ("vb", session, f2.id),
        ("tx", session, f2.id),
    ]
    assert calls == expected, "Must call vertex-build deletion then transaction deletion for each valid flow id"


@pytest.mark.anyio
async def test__delete_transactions_and_vertex_builds_logs_exceptions_and_continues(caplog, monkeypatch):
    caplog.set_level("DEBUG")

    async def raise_vb(session, flow_id):
        raise RuntimeError("vb oops")

    async def raise_tx(session, flow_id):
        raise RuntimeError("tx oops")

    monkeypatch.setattr(conf, "delete_vertex_builds_by_flow_id", raise_vb)
    monkeypatch.setattr(conf, "delete_transactions_by_flow_id", raise_tx)

    fid = uuid.uuid4()
    flows = [types.SimpleNamespace(id=fid)]

    # Should not raise despite underlying failures; errors are logged at DEBUG
    await conf._delete_transactions_and_vertex_builds("SESSION", flows)

    messages = [r.message for r in caplog.records]
    assert any("Error deleting vertex builds for flow" in m and str(fid) in m for m in messages), \
        "Must log vertex-build deletion errors with flow id"
    assert any("Error deleting transactions for flow" in m and str(fid) in m for m in messages), \
        "Must log transaction deletion errors with flow id"


def test_deactivate_tracing_env_is_set():
    # Autouse fixture in conftest should ensure this is present for all tests
    assert os.getenv("AIEXEC_DEACTIVATE_TRACING") == "true"


def test_use_noop_session_fixture_sets_env(use_noop_session):
    # The fixture should set the env var for the duration of the test
    assert os.getenv("AIEXEC_USE_NOOP_DATABASE") == "1"