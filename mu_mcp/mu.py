import asyncio
import datetime
import json
from typing import Any

from .models import Email

_MU_NO_RESULTS_EXIT_CODE = 4


async def _run_mu(*args: str) -> bytes:
    proc = await asyncio.create_subprocess_exec(
        "mu",
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode not in (0, _MU_NO_RESULTS_EXIT_CODE):
        raise RuntimeError(f"mu {args[0]} failed: {stderr.decode().strip()}")
    return stdout


def _strip_colons(obj: Any) -> Any:
    """Recursively strip leading ':' from all dict keys in mu JSON output."""
    if isinstance(obj, dict):
        return {k.lstrip(":"): _strip_colons(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_strip_colons(i) for i in obj]
    return obj


def _parse_date(val: Any) -> str:
    """Convert mu time-val [high, low, microseconds] (Emacs time) to ISO 8601 UTC.

    Unix timestamp = high * 65536 + low
    """
    if isinstance(val, list) and len(val) >= 2:
        ts = val[0] * 65536 + val[1]
    elif isinstance(val, int):
        ts = val
    else:
        return ""
    return datetime.datetime.fromtimestamp(ts, tz=datetime.UTC).isoformat()


def _parse_flags(val: Any) -> list[str]:
    """Convert mu flags dict (e.g. {'seen': 'attach'}) to a flat list."""
    if isinstance(val, dict):
        flags: set[str] = set()
        for k, v in val.items():
            flags.add(k)
            if isinstance(v, str) and v:
                flags.add(v)
        return sorted(flags)
    if isinstance(val, list):
        return [str(f) for f in val]
    return []


def _normalize(raw: dict[str, Any]) -> dict[str, Any]:
    data: dict[str, Any] = _strip_colons(raw)
    data["date"] = _parse_date(data.get("date", 0))
    data["flags"] = _parse_flags(data.get("flags", {}))
    return data


async def find(
    query: str,
    max_results: int = 50,
    sort_field: str = "date",
    sort_order: str = "desc",
) -> list[Email]:
    """Run mu find and return parsed Email objects."""
    args = [
        "find",
        "--format=json",
        f"--maxnum={max_results}",
        f"--sortfield={sort_field}",
        "--nocolor",
    ]
    if sort_order == "desc":
        args.append("--reverse")
    args.append(query)
    stdout = await _run_mu(*args)
    if not stdout.strip():
        return []
    return [Email.model_validate(_normalize(item)) for item in json.loads(stdout)]


async def view(path: str) -> str:
    """Run mu view on a specific message path and return the raw email text."""
    stdout = await _run_mu("view", "--format=plain", path)
    return stdout.decode(errors="replace")
