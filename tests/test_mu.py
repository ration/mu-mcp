import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mu_mcp.models import Address, Email
from mu_mcp.mu import _parse_date, _parse_flags, find, view

# mu JSON uses colon-prefixed keys and Emacs time-val for dates
_SAMPLE_RAW = {
    ":subject": "Hello",
    ":from": [{"email": "alice@example.com"}],
    ":to": [{"email": "bob@example.com"}],
    ":date": [24205, 51762, 0],  # Emacs [high, low, usec] → 2020-04-08
    ":path": "/home/user/Maildir/inbox/cur/msg1",
    ":message-id": "<abc@example.com>",
    ":size": 1024,
    ":flags": {"seen": "attach"},
    ":maildir": "/inbox",
    ":priority": "normal",
}

_SAMPLE_PLAIN_BODY = b"From: alice@example.com\nSubject: Hello\n\nHello Bob!"


def _mock_proc(stdout: bytes, returncode: int = 0) -> MagicMock:
    proc = MagicMock()
    proc.communicate = AsyncMock(return_value=(stdout, b""))
    proc.returncode = returncode
    return proc


def test_parse_date_emacs_timeval() -> None:
    assert _parse_date([24205, 51762, 0]) == 24205 * 65536 + 51762


def test_parse_date_int_passthrough() -> None:
    assert _parse_date(1700000000) == 1700000000


def test_parse_flags_dict() -> None:
    assert _parse_flags({"seen": "attach"}) == ["attach", "seen"]


def test_parse_flags_empty() -> None:
    assert _parse_flags({}) == []


@pytest.mark.asyncio
async def test_find_returns_emails() -> None:
    stdout = json.dumps([_SAMPLE_RAW]).encode()
    with patch("asyncio.create_subprocess_exec", return_value=_mock_proc(stdout)):
        results = await find("from:alice")
    assert len(results) == 1
    assert results[0].subject == "Hello"
    assert results[0].from_[0].email == "alice@example.com"
    assert results[0].flags == ["attach", "seen"]
    assert results[0].date == 24205 * 65536 + 51762


@pytest.mark.asyncio
async def test_find_no_results() -> None:
    with patch(
        "asyncio.create_subprocess_exec",
        return_value=_mock_proc(b"", returncode=4),
    ):
        results = await find("from:nobody")
    assert results == []


@pytest.mark.asyncio
async def test_view_returns_plain_text() -> None:
    with patch(
        "asyncio.create_subprocess_exec",
        return_value=_mock_proc(_SAMPLE_PLAIN_BODY),
    ):
        text = await view("/home/user/Maildir/inbox/cur/msg1")
    assert "Hello Bob!" in text
    assert "From: alice@example.com" in text


def test_email_model_alias() -> None:
    from mu_mcp.mu import _normalize

    data = _normalize(_SAMPLE_RAW)
    email = Email.model_validate(data)
    assert email.from_ == [Address(email="alice@example.com")]
