from mcp.server.fastmcp import FastMCP

from .models import Email
from .mu import find, mailboxes, view

mcp = FastMCP("mu-mcp")


@mcp.tool()
async def search_emails(
    query: str,
    max_results: int = 50,
    sort_field: str = "date",
    sort_order: str = "desc",
) -> list[Email]:
    """Search emails using mu find query syntax.

    Examples: 'from:alice subject:report date:2w..'

    sort_field: one of date, from, to, subject, size, maildir (default: date)
    sort_order: "desc" for newest/largest first, "asc" for oldest/smallest first
    """
    return await find(query, max_results, sort_field, sort_order)


@mcp.tool()
async def list_mailboxes() -> list[str]:
    """List all maildirs in the mu index.

    Call this first to discover maildir names before using maildir: in queries.
    """
    return await mailboxes()


@mcp.tool()
async def get_email(path: str) -> str:
    """Get the full content of an email by its file path.

    The path is obtained from the `path` field of search_emails results.
    Returns the raw email text including headers and body.
    """
    return await view(path)
