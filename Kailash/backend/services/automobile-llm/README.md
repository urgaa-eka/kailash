# services/automobile-llm

The moat. Domain-specialized LLM for Indian automobile regulations,
parts, HSN / GST, chargers, RTO, servicing, insurance.

| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/model` | Default + active model id. |
| `POST` | `/chat`  | `{ messages, model?, temperature? }` |

**Moat ladder**
1. OpenRouter pass-through (any chat model) — ships today.
2. Llama-3.1-8B fine-tune on scraped regulations + synthetic data.
3. Continued fine-tune on anonymized customer data.
4. Automobile-LLM-13B licensed product for OEM / DISCOM.

Set `AUTOMOBILE_LLM_MODEL` to override. Requires `OPENROUTER_API_KEY`.
