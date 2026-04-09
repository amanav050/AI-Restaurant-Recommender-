# Phase 0: Foundations and Cross-Cutting Architecture

## Purpose

Establish technical anchors so later phases (data, prompts, UI) stay consistent: runtime choices, configuration, error handling philosophy, and how non-functional requirements (latency, cost, privacy) are satisfied.

## Scope

- Technology stack recommendations (adjust to team skills).
- Repository layout and configuration boundaries.
- Shared types/schemas used across phases.
- Cross-cutting concerns: logging, retries, secrets, rate limits.

## Architectural decisions

| Decision area | Recommended default | Rationale |
|---------------|---------------------|-----------|
| Runtime | Python 3.11+ backend service (FastAPI or similar) | Strong ecosystem for data + LLM SDKs; simple FastAPI deployment. |
| Data at rest | Parquet or SQLite for local dev; optional Postgres for multi-user | Dataset is structured; start simple, scale if needed. |
| LLM access | Groq LLM via env-configured API key (`LLM_API_KEY` in `.env`) | Matches “use an LLM”; abstract behind an interface for swap/testing. |
| Caching | Optional Redis or in-memory TTL cache keyed by `(preferences_hash, dataset_version)` | Reduces duplicate LLM calls for repeated queries. |
| Config | `.env` + pydantic-settings (or equivalent) | Keeps secrets out of code; one place for model name and limits. |

## Logical modules (high level)

```
app/
  core/           # config, logging, errors
  domain/         # Restaurant, UserPreferences, Recommendation (pure types)
  data/           # loaders, repositories (Phase 1)
  services/       # filter, llm client, orchestration (Phases 3–4)
  api/            # routes, schemas (Phases 2, 5)
```

## Shared domain model (contract across phases)

- **Restaurant**: normalized record after ingestion (id, name, city/location, cuisines, cost tier or numeric, rating, optional tags).
- **UserPreferences**: location, budget band, cuisine(s), min rating, free-text or structured “additional preferences.”
- **RecommendationItem**: restaurant fields surfaced to UI + `explanation` + optional `rank` or `score`.
- **RecommendationResponse**: ordered list of `RecommendationItem`, optional `summary`, metadata (`model`, `latency_ms`, `dataset_version`).

## Non-functional requirements

- **Latency**: cap candidate set before LLM (e.g., top N after filter) to bound prompt size and token cost.
- **Cost**: structured output (JSON mode or schema-guided parsing) to avoid long rambling completions.
- **Reliability**: timeouts and retries on LLM with fallback message (“try again” / show filtered list without AI copy).
- **Observability**: structured logs for request id, filter counts, token usage (if available), and errors (Phase 6 expands).

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Dataset schema drift on Hugging Face | Version pin; ingestion validation step; schema contract test. |
| LLM hallucinates restaurants | Only allow the model to choose from provided candidate list in the prompt; post-validate IDs. |
| PII in logs | Log preference categories, not raw free-text if policy requires. |

## Deliverables checklist

- [ ] Repo skeleton with `domain` types and config loading
- [ ] CI placeholder (lint/test) if team uses it
- [ ] Documented environment variables for dataset path and LLM provider

## Inputs / outputs to other phases

- **Outputs**: schemas and module boundaries consumed by Phases 1–5.
- **Inputs**: none (this phase is the root).
