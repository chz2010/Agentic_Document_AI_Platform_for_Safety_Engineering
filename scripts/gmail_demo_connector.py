#!/usr/bin/env python3
"""Process controlled Gmail test emails through the Project 2 conversation workflow.

This is deliberately a demo-only *read and classify* connector. It never sends
email, never creates Gmail labels, and only processes unread messages that
match both an allowed sender and a configured subject prefix (``[DEMO]`` by
default). With an explicit flag, it can upload safe Markdown attachments to the
existing Project 2 document-ingestion API. It uses Gmail IMAP with an app
password, rather than exposing the local FastAPI server to the internet.
"""

from __future__ import annotations

import argparse
import email
import imaplib
import json
import os
import sys
from email.header import decode_header
from email.message import Message
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing {name}. Add it to {ROOT / '.env'}.")
    return value


def _decode_header(value: str | None) -> str:
    if not value:
        return ""
    pieces: list[str] = []
    for part, encoding in decode_header(value):
        if isinstance(part, bytes):
            pieces.append(part.decode(encoding or "utf-8", errors="replace"))
        else:
            pieces.append(part)
    return "".join(pieces).strip()


def _plain_text_body(message: Message) -> str:
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() != "text/plain" or part.get_content_disposition() == "attachment":
                continue
            payload = part.get_payload(decode=True) or b""
            return payload.decode(part.get_content_charset() or "utf-8", errors="replace").strip()
        return ""
    if message.get_content_type() != "text/plain":
        return ""
    payload = message.get_payload(decode=True) or b""
    return payload.decode(message.get_content_charset() or "utf-8", errors="replace").strip()


def _markdown_attachments(message: Message, max_bytes: int) -> list[tuple[str, bytes]]:
    """Return only small Markdown attachments; all other attachment types are ignored."""
    attachments: list[tuple[str, bytes]] = []
    if not message.is_multipart():
        return attachments
    for part in message.walk():
        filename = _decode_header(part.get_filename())
        if not filename or Path(filename).suffix.lower() not in {".md", ".markdown"}:
            continue
        payload = part.get_payload(decode=True) or b""
        if not payload:
            continue
        if len(payload) > max_bytes:
            print(f"Skipped Markdown attachment '{filename}': larger than {max_bytes} bytes.")
            continue
        attachments.append((Path(filename).name, payload))
    return attachments


def _post(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def _upload_markdown_attachment(api_base_url: str, project_id: int, filename: str, content: bytes) -> dict[str, Any]:
    response = requests.post(
        f"{api_base_url}/projects/{project_id}/documents",
        data={"replace_existing": "false"},
        files={"file": (filename, content, "text/markdown")},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def _process_message(
    api_base_url: str,
    project_id: int,
    sender: str,
    subject: str,
    body: str,
    message_id: str,
    owner: str | None,
    markdown_attachments: list[tuple[str, bytes]],
    process_markdown_attachments: bool,
) -> dict[str, Any]:
    metadata = {
        "channel": "email",
        "sender": sender,
        "subject": subject,
        "message_id": message_id,
        "demo_only": True,
    }
    conversation = _post(
        f"{api_base_url}/projects/{project_id}/conversations",
        {
            "title": f"Gmail demo: {subject}",
            "mode": "email_intake",
            "source_system": "gmail_demo",
            "metadata": metadata,
        },
    )
    conversation_id = conversation["id"]
    content = f"Incoming Gmail demo email\nFrom: {sender}\nSubject: {subject}\n\n{body}"
    message = _post(
        f"{api_base_url}/projects/{project_id}/conversations/{conversation_id}/messages",
        {"role": "user", "content": content, "metadata": metadata},
    )
    intent = _post(
        f"{api_base_url}/projects/{project_id}/conversations/{conversation_id}/intent-detect",
        {},
    )
    actions = _post(
        f"{api_base_url}/projects/{project_id}/conversations/{conversation_id}/actions",
        {
            "create_workflow_items": True,
            "create_agent_run": True,
            "owner": owner,
            "priority": None,
        },
    )
    result: dict[str, Any] = {
        "conversation_id": conversation_id,
        "message_id": message["id"],
        "intent": intent["intent"],
        "confidence": intent["confidence"],
        "recommended_actions": actions["proposed_actions"],
        "workflow_item_ids": [item["id"] for item in actions["workflow_items"]],
    }
    if process_markdown_attachments and markdown_attachments:
        uploaded = [
            _upload_markdown_attachment(api_base_url, project_id, filename, content)
            for filename, content in markdown_attachments
        ]
        extraction = _post(f"{api_base_url}/projects/{project_id}/requirements/extract", {})
        evaluation = _post(f"{api_base_url}/projects/{project_id}/requirements/evaluate", {})
        result["markdown_documents"] = [
            {"id": document["id"], "filename": document["filename"], "chunk_count": document["chunk_count"]}
            for document in uploaded
        ]
        result["extracted_requirement_count"] = len(extraction["requirements"])
        result["requirements_quality_summary"] = evaluation["quality_summary"]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Route controlled Gmail test emails to Project 2.")
    parser.add_argument("--execute", action="store_true", help="Actually create Project 2 conversations and workflow items.")
    parser.add_argument("--mark-seen", action="store_true", help="Mark successfully processed demo emails as read in Gmail.")
    parser.add_argument(
        "--process-markdown-attachments",
        action="store_true",
        help="Upload .md attachments to Project 2, then run requirement extraction and evaluation.",
    )
    parser.add_argument("--folder", default=os.getenv("GMAIL_IMAP_FOLDER", "INBOX"))
    parser.add_argument("--max-emails", type=int, default=3)
    parser.add_argument("--owner", default=os.getenv("GMAIL_DEMO_OWNER") or None)
    args = parser.parse_args()
    if args.mark_seen and not args.execute:
        raise SystemExit("--mark-seen requires --execute.")
    if args.process_markdown_attachments and not args.execute:
        raise SystemExit("--process-markdown-attachments requires --execute.")

    gmail_address = _required_env("GMAIL_IMAP_EMAIL")
    app_password = _required_env("GMAIL_IMAP_APP_PASSWORD")
    allowed_sender = _required_env("GMAIL_ALLOWED_SENDER").lower()
    subject_prefix = os.getenv("GMAIL_SUBJECT_PREFIX", "[DEMO]").strip()
    api_base_url = os.getenv("PROJECT2_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    project_id = int(os.getenv("PROJECT2_DEMO_PROJECT_ID", "1"))
    host = os.getenv("GMAIL_IMAP_HOST", "imap.gmail.com")
    port = int(os.getenv("GMAIL_IMAP_PORT", "993"))
    max_attachment_bytes = int(os.getenv("GMAIL_DEMO_MAX_ATTACHMENT_BYTES", "262144"))

    with imaplib.IMAP4_SSL(host, port) as client:
        client.login(gmail_address, app_password)
        status, _ = client.select(args.folder, readonly=not args.mark_seen)
        if status != "OK":
            raise SystemExit(f"Cannot open Gmail folder: {args.folder}")
        status, data = client.search(None, "UNSEEN", "FROM", f'"{allowed_sender}"', "SUBJECT", f'"{subject_prefix}"')
        if status != "OK":
            raise SystemExit("Gmail search failed.")
        email_ids = data[0].split()[-max(args.max_emails, 1) :]
        if not email_ids:
            print("No unread Gmail demo emails matched the configured sender and subject prefix.")
            return

        for email_id in email_ids:
            status, payload = client.fetch(email_id, "(BODY.PEEK[])")
            if status != "OK" or not payload or not isinstance(payload[0], tuple):
                print(f"Skipped Gmail message {email_id.decode()}: unable to read it.")
                continue
            message = email.message_from_bytes(payload[0][1])
            sender = _decode_header(message.get("From"))
            subject = _decode_header(message.get("Subject"))
            body = _plain_text_body(message)
            markdown_attachments = _markdown_attachments(message, max_attachment_bytes)
            message_id = message.get("Message-ID", "")
            if not body and not markdown_attachments:
                print(f"Skipped '{subject}': no plain-text body or Markdown attachment.")
                continue
            if not body:
                body = "Markdown attachment received for document processing."

            preview = {
                "sender": sender,
                "subject": subject,
                "body_preview": body[:160],
                "markdown_attachments": [filename for filename, _ in markdown_attachments],
            }
            if not args.execute:
                print("DRY RUN — would process:\n" + json.dumps(preview, ensure_ascii=False, indent=2))
                continue

            result = _process_message(
                api_base_url,
                project_id,
                sender,
                subject,
                body,
                message_id,
                args.owner,
                markdown_attachments,
                args.process_markdown_attachments,
            )
            print("Processed Gmail demo email:\n" + json.dumps({**preview, **result}, ensure_ascii=False, indent=2))
            if args.mark_seen:
                client.store(email_id, "+FLAGS", "\\Seen")


if __name__ == "__main__":
    try:
        main()
    except imaplib.IMAP4.error as exc:
        print(
            "Gmail IMAP login failed. Check that GMAIL_IMAP_EMAIL is the inbox account, "
            "GMAIL_IMAP_APP_PASSWORD is a current Google app password (not your normal password), "
            "and 2-Step Verification is enabled. Original Gmail response: " + str(exc),
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
    except requests.RequestException as exc:
        print(f"Project 2 API request failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
