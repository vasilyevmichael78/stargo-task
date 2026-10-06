"""Normalize supported inputs without executing or rendering source content."""

from email import policy
from email.parser import BytesParser
from email.utils import getaddresses
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from pypdf import PdfReader

from .domain import AppError

MAX_UPLOAD = 10 * 1024 * 1024
MAX_TEXT = 100_000


def source(name, text):
    return {"id": str(uuid4()), "name": name, "text": text}


def normalize(text: str, attachments=None, metadata=None):
    if not text.strip() and not attachments:
        raise AppError("invalid_input", "Provide non-empty email content.")
    sources = [source("Email", text)] + [
        source(item["filename"], item["extracted_text"]) for item in (attachments or [])
    ]
    if sum(len(item["text"]) for item in sources) > MAX_TEXT:
        raise AppError(
            "invalid_input",
            "Normalized content exceeds 100,000 characters.",
            False,
            413,
        )
    parsed = BytesParser(policy=policy.default).parsebytes(text.encode())
    fields = {
        "sender": str(parsed.get("From", "Unknown sender")),
        "recipients": [
            address for _, address in getaddresses(parsed.get_all("To", []))
        ],
        "subject": str(parsed.get("Subject", "Untitled email")),
        "date": str(parsed["Date"]) if parsed["Date"] else None,
    }
    return {
        **fields,
        **(metadata or {}),
        "body": text,
        "sources": sources,
        "warnings": [],
    }


def pdf_text(data):
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise ValueError()
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if not text.strip():
            raise ValueError()
        return text
    except Exception:
        raise AppError(
            "invalid_input",
            "PDF requires an unencrypted, readable text layer. OCR is not supported.",
        ) from None


def upload(filename: str, data: bytes):
    if len(data) > MAX_UPLOAD:
        raise AppError(
            "invalid_input", "File exceeds the 10 MiB upload limit.", False, 413
        )
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return normalize(pdf_text(data))
    if suffix == ".txt":
        try:
            return normalize(data.decode("utf-8-sig"))
        except UnicodeError:
            raise AppError(
                "invalid_input", "Text files must use UTF-8 encoding."
            ) from None
    if suffix != ".eml":
        raise AppError("invalid_input", "Upload a .txt, .pdf, or .eml file.")
    try:
        message = BytesParser(policy=policy.default).parsebytes(data)
        body = message.get_body(preferencelist=("plain",))
        if not body:
            raise AppError(
                "invalid_input",
                "EML requires a plain-text body; HTML-only email is not supported.",
            )
        text = body.get_content()
        attachments, warnings = [], []
        for part in message.iter_attachments():
            name = part.get_filename() or "attachment"
            content = part.get_payload(decode=True) or b""
            if Path(name).suffix.lower() == ".pdf":
                attachments.append(
                    {"filename": name, "extracted_text": pdf_text(content)}
                )
            elif part.get_content_type() == "text/plain":
                attachments.append(
                    {"filename": name, "extracted_text": part.get_content()}
                )
            else:
                warnings.append("An unsupported attachment was skipped.")
        headers = "\n".join(
            f"{key}: {message[key]}"
            for key in ("From", "To", "Date", "Subject")
            if message[key]
        )
        result = normalize(headers + "\n\n" + text, attachments)
        result["warnings"] = warnings
        return result
    except AppError:
        raise
    except Exception:
        raise AppError("invalid_input", "The email file could not be parsed.") from None
