# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

MCP (Model Context Protocol) server exposing `mu` email search capabilities to LLM clients.

## Tech Stack

- Python 3.14
- `uv` for all packaging, dependency management, and running scripts
- `mcp` Python SDK for the MCP server
- `fastapi` for HTTP layer (if needed beyond stdio transport)
- `ruff` for linting and formatting
- `ty` for static type checking

## Commands

```bash
# Install dependencies
uv sync

# Run the MCP server
uv run python -m mu_mcp

# Type check
uv run ty check

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_foo.py::test_bar
```

## Architecture

The server wraps the `mu` CLI tool (specifically `mu find`) to expose email search as MCP tools. Key components:

- **`mu_mcp/`** — main package
  - **`server.py`** — FastMCP setup; registers `search_emails` and `get_email` tools
  - **`mu.py`** — async subprocess wrappers for `mu find` and `mu view`; parses JSON output
  - **`models.py`** — Pydantic models (`Address`, `Email`, `EmailWithBody`); `from_` uses `Field(alias="from")` to handle the reserved keyword
- **`tests/`** — pytest tests using `unittest.mock` to patch `asyncio.create_subprocess_exec`

The server communicates via MCP stdio transport by default (suitable for Claude Desktop and similar clients).

**mu JSON format quirks** (all handled in `mu.py`):
- All keys are colon-prefixed: `:subject`, `:from`, `:path`, etc. — stripped by `_strip_colons()`
- Date is Emacs time-val `[high, low, microseconds]`; unix timestamp = `high * 65536 + low`
- Flags is a dict like `{"seen": "attach"}` where both keys and values are flag names
- Limit flag is `--maxnum`, not `--number`
- `name` in address objects is optional (some senders omit it)
- `mu find` exits with code 4 when there are no results (treated as success)

The `[tool.ty.environment]` section (not `[tool.ty]` directly) is where `python-version` lives in `pyproject.toml`.

## Conventions

- All code must pass `ty check` and `ruff check` with no errors before committing
- Use `uv add` / `uv remove` to manage dependencies (never edit `pyproject.toml` dependency lists manually)
- All public functions and methods must have type annotations
