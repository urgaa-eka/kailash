"""Document AI — OCR, layout extraction, field validation.

Provider-backed. Default provider is a naive text-layer extractor for PDFs
using ``pypdf``. Plug in Azure Document Intelligence or an in-house
LayoutLMv3 backend by setting ``DOCAI_PROVIDER=azure`` and the relevant
credentials.
"""
from __future__ import annotations

import io
from typing import Any

from pypdf import PdfReader

from backend.shared import ValidationError, get_logger

log = get_logger("document-ai")


def extract_pdf_text(data: bytes) -> list[dict[str, Any]]:
    if not data:
        raise ValidationError("empty payload")
    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception as e:
        raise ValidationError(f"cannot parse pdf: {e}")
    pages = []
    for i, p in enumerate(reader.pages):
        try:
            txt = p.extract_text() or ""
        except Exception:
            txt = ""
        pages.append({"page": i + 1, "text": txt, "chars": len(txt)})
    return pages


# Minimal field-level validators. Services like GSTSAAS / URGAA pass a
# profile name to decide which validators to run.
VALIDATION_PROFILES: dict[str, list[str]] = {
    "gst_invoice":   ["gstin", "invoice_no", "total_amount"],
    "rc_book":       ["vehicle_no", "chassis_no", "engine_no"],
    "id_proof":      ["doc_no", "name"],
    "certification": ["cert_no", "issue_date"],
}


def validate_fields(profile: str, fields: dict[str, Any]) -> dict[str, Any]:
    required = VALIDATION_PROFILES.get(profile)
    if required is None:
        raise ValidationError(
            f"unknown profile: {profile}",
            hint=f"supported: {', '.join(VALIDATION_PROFILES)}",
        )
    missing = [f for f in required if not fields.get(f)]
    return {
        "profile": profile,
        "ok": not missing,
        "missing_fields": missing,
        "checked": required,
    }
