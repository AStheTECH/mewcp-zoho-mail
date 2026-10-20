"""MewCP Zoho Mail tool registration."""

from fastmcp import FastMCP

from .accounts_tools import register_accounts_tools
from .folders_tools import register_folders_tools
from .labels_tools import register_labels_tools
from .emails_tools import register_emails_tools


def register_tools(mcp: FastMCP) -> None:
    register_accounts_tools(mcp)
    register_folders_tools(mcp)
    register_labels_tools(mcp)
    register_emails_tools(mcp)
