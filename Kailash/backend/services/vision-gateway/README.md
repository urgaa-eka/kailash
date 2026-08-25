# services/vision-gateway

Cost/latency-aware router over GPT-4o / Gemini 1.5 / Claude 3.5, all via OpenRouter.

| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/models` | Tier → model mapping. |
| `POST` | `/route`  | Dry-run the routing decision. |
| `POST` | `/infer`  | Route + call the model. |

Tiers: `fast` (`openai/gpt-4o-mini`), `balanced` (`anthropic/claude-3.5-sonnet`),
`long` (`google/gemini-1.5-pro`). Auto-selects by prompt length unless
caller pins a tier. Requires `OPENROUTER_API_KEY`.
