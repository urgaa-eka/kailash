# services/document-ai

OCR, layout understanding and field validation for certs, invoices, RC books and ID proofs.

**Endpoints**

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/extract` | Multipart upload; returns per-page text (PDF text layer). |
| `POST` | `/validate` | `{profile, fields}` → required-field validation. |
| `GET`  | `/profiles` | Built-in validation profiles. |

**Profiles:** `gst_invoice`, `rc_book`, `id_proof`, `certification`.

Default provider extracts PDF text via `pypdf`. Swap to Azure Document
Intelligence / in-house LayoutLMv3 by implementing a new provider in
`app/service.py` and switching at startup.
