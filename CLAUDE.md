# LLM Infrastructure

## Tech Stack
- **Backend:** Python, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL
- **Frontend:** React, TypeScript, TanStack Query
- **Streaming:** Server-Sent Events (SSE)
- **Testing:** Pytest (unit, integration, provider contract)
- **CI:** Lint, type checks, tests — no paid API calls

## Repository Structure
`
llm-infrastructure/
├── apps/playground/       # React developer console
├── gateway/
│   ├── api/               # FastAPI routes
│   ├── core/              # Config, errors, logging
│   ├── providers/         # OpenAIProvider, OpenRouterProvider
│   ├── services/          # Business logic
│   ├── repositories/      # DB access layer
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── policies/          # Rate limiting, quotas
│   └── tests/
├── migrations/            # Alembic migrations
├── docs/
│   ├── architecture.md    # Design decisions
│   └── decisions/         # ADRs
├── .env.example
├── .gitignore
├── docker-compose.yml     # PostgreSQL only
└── README.md
`

## Implementation Phases
1. **Phase 1** — Basic Gateway (FastAPI + OpenAI, non-streaming, no DB)
2. **Phase 2** — Provider Abstraction (LLMProvider interface, OpenRouter)
3. **Phase 3** — Streaming (SSE, TTFT, client disconnect)
4. **Phase 4** — Organization Model (PostgreSQL, API keys, auth)
5. **Phase 5** — Model Catalog & Governance (aliases, policies, rate limits, quotas)
6. **Phase 6** — Usage & Observability (persistence, cost, logging)
7. **Phase 7** — Reliability (timeout, retry, fallback, error normalization)
8. **Phase 8** — Developer Playground (React app)
9. **Phase 9** — Hardening (tests, docs, CI)

## Key Design Principles
- Modular monolith — no microservices
- Provider abstraction isolates SDK-specific code
- Model aliases decouple apps from provider models
- Error normalization prevents provider leaks
- Fail closed — reject before spending on provider calls
- Never store/log raw API keys
- Tests alongside every feature
- Simple before clever, explicit before magical

## Current Status
- [ ] Phase 1 — Basic Gateway
- [ ] Phase 2 — Provider Abstraction
- [ ] Phase 3 — Streaming
- [ ] Phase 4 — Organization Model
- [ ] Phase 5 — Model Catalog & Governance
- [ ] Phase 6 — Usage & Observability
- [ ] Phase 7 — Reliability
- [ ] Phase 8 — Developer Playground
- [ ] Phase 9 — Hardening
