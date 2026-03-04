from mcp.server.fastmcp import FastMCP

from .models import Contact, Email
from .mu import contacts, find, mailboxes, view

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
async def find_contacts(query: str, max_results: int = 20) -> list[Contact]:
    """Search contacts by name or email address using mu cfind.

    Use this to resolve a person's name to their exact email address before
    searching emails with from: or to: filters.
    """
    return await contacts(query, max_results)


@mcp.tool()
async def list_mailboxes() -> list[str]:
    """List all maildirs in the mu index.

    Call this first to discover maildir names before using maildir: in queries.
    """
    return await mailboxes()


@mcp.resource("mu://query-syntax")
def query_syntax() -> str:
    """Reference guide for mu query syntax."""
    return """\
# mu query syntax

## Field prefixes
from:alice          sender name or address contains "alice"
to:bob              recipient contains "bob"
cc:carol            cc contains "carol"
subject:report      subject contains "report"
body:invoice        body contains "invoice"
maildir:/inbox      in the /inbox maildir (use list_mailboxes to discover names)
msgid:<id@host>     exact message-id match

## Flags
flag:unread         unread messages
flag:flagged        flagged/starred messages
flag:replied        messages you have replied to
flag:attach         messages with attachments

## Date ranges
date:2w..           last 2 weeks (w=weeks, d=days, m=months, y=years)
date:..2024-01-01   before 2024-01-01
date:2024-01-01..2024-12-31  during 2024
date:today          today only

## Combining
from:alice flag:unread          unread from alice
subject:invoice date:3m..       invoices in the last 3 months
from:alice OR from:bob          from either sender
from:alice AND subject:report   both conditions
NOT flag:unread                 read messages

## Wildcards
from:ali*           prefix wildcard
"""


@mcp.tool()
async def get_email(path: str) -> str:
    """Get the full content of an email by its file path.

    The path is obtained from the `path` field of search_emails results.
    Returns the raw email text including headers and body.
    """
    return await view(path)
