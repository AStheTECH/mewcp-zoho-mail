"""Configuration for MewCP Zoho Mail MCP Server."""

import logging
import os

SERVER_VERSION = "v1.0.0"
BREAKING_CHANGES: list[dict] = []

SCOPES = [
    "ZohoMail.accounts.READ",   # accounts.list_accounts
    "ZohoMail.folders.READ",    # folders.list_folders
    "ZohoMail.tags.READ",       # labels.list_labels
    "ZohoMail.messages.READ",   # emails.list_emails, search_emails, get_email_content
    "ZohoMail.messages.CREATE",  # emails.send_email, reply_to_email, save_draft
    "ZohoMail.messages.UPDATE",  # emails.mark_email_as_read/unread, move_emails, apply_labels_to_emails
    "ZohoMail.messages.DELETE",  # emails.delete_email
]

# api_base holds a per-user placeholder — the data center host is derived per
# request in service.py from the connection's credentials, never cached here.
ZOHO_MAIL_API_BASE = "https://{mail_host}/api"

CONNECT_TIMEOUT = 5    # TCP connection — fixed across all servers
READ_TIMEOUT = 30      # Zoho Mail has no published SLA; 30s matches other REST-based MewCP servers


def configure_logging() -> None:
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    try:
        from pythonjsonlogger import jsonlogger
        handler = logging.StreamHandler()
        handler.setFormatter(
            jsonlogger.JsonFormatter(fmt="%(asctime)s %(name)s %(levelname)s %(message)s")
        )
    except ImportError:
        handler = logging.StreamHandler()
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)
