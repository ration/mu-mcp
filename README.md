# mu-mcp

An MCP server that lets your local LLM search your email using [mu](https://www.djcbsoftware.nl/code/mu/).

## Privacy

Your emails never leave your machine.

mu indexes your local maildir and searches it entirely on-device — no email content is sent to any server. When paired with a local LLM such as [Qwen](https://ollama.com/library/qwen2.5), [Mistral](https://ollama.com/library/mistral), or [Llama](https://ollama.com/library/llama3.2) running via [Ollama](https://ollama.com), the full pipeline is local:

```
your emails → mu index (local) → mu-mcp → local LLM
```

Nothing touches the internet. This is in contrast to cloud-based email AI integrations that require granting third-party services access to your inbox.

If you use a cloud LLM (e.g. Claude, GPT-4), be aware that email metadata — subjects, sender addresses, dates, and full message bodies if you invoke `get_email` — will be sent to that provider as part of the conversation context.

## Requirements

- [`mu`](https://www.djcbsoftware.nl/code/mu/) 1.x installed and your maildir indexed (`mu init && mu index`)
- Python 3.14
- [`uv`](https://github.com/astral-sh/uv)

## Installation

```bash
git clone ...
cd mu-mcp
uv sync
```

## MCP client configuration

```json
{
  "mcpServers": {
    "mu": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/mu-mcp",
        "mu-mcp"
      ]
    }
  }
}
```

## Tools

**`search_emails(query, max_results, sort_field, sort_order)`**
Search your maildir using [mu query syntax](https://www.djcbsoftware.nl/code/mu/mu4e/Queries.html). Returns email metadata (subject, sender, date, path, flags).

**`get_email(path)`**
Retrieve the full content of a message by its file path (as returned by `search_emails`). Returns headers and body as plain text.
