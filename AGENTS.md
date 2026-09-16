# LLM Infrastructure — Agent Instructions

## Project Context

This is an **organization-owned LLM control plane** between applications and external LLM providers (OpenAI, OpenRouter). It is a portfolio project demonstrating production-oriented LLM infrastructure.

**Guiding question:** Why should an application call this gateway instead of calling OpenAI/OpenRouter directly?

## Critical Rules

1. **Read SPEC.md fully** before modifying architecture — every section matters.
2. **Never commit secrets** — no real credentials in code, tests, docs, logs, or git history.
3. **Never call paid LLM APIs from tests** — mock/fake providers only.
4. **One vertical slice at a time** — each phase must work, have tests, be understandable, be documented before moving on.
5. **Do not overengineer** — simple before clever, modular before microservices, observable before optimized.

## Non-Goals (Do NOT implement)

- Chatbot product, RAG, embeddings, vector search, agents, tool calling, fine-tuning, model training
- Complex RBAC, payment processing, AI-based model routing, Kubernetes, service mesh, microservices
- LangChain replacement, prompt management platform, OpenRouter clone

## Architecture Constraints

- **Modular monolith** — do NOT split into microservices.
- **Provider abstraction** — provider-specific logic MUST stay inside provider adapters.
- **Business logic** MUST NOT depend directly on the OpenAI SDK.
- **OpenRouter** is an upstream provider, NOT a replacement for our gateway.
- **Model aliases** — applications request internal aliases, not provider model names.
- **Error normalization** — provider errors MUST NOT leak to applications.
- **Streaming via SSE** — no buffering before forwarding.
- **PostgreSQL + Alembic** for persistence.
- **Python/FastAPI/Pydantic** backend, **React/TypeScript** frontend.
- **Prefer standard libraries and focused dependencies.**

## Pre-Development Checklist

- [ ] Read SPEC.md
- [ ] Check current phase of implementation
- [ ] Confirm no secrets in code being written
- [ ] Plan tests alongside feature code
- [ ] Document significant architectural decisions in docs/

## When Requirements Are Ambiguous

1. Prefer simplest implementation satisfying the stated goal.
2. Avoid scope expansion.
3. Document the assumption.
4. Continue unless the decision materially alters the architecture.
