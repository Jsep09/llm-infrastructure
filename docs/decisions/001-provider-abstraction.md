# 001 — Provider Abstraction

## Context

The gateway supports two upstream providers (OpenAI, OpenRouter) and may support more. Business logic should not depend on provider-specific SDKs.

## Decision

Define a LLMProvider abstract base class in gateway/providers/base.py with complete() and stream() methods. Each provider adapter implements this interface. The rest of the gateway interacts only through this interface.

## Consequences

- Provider SDK imports are confined to adapter files
- Adding a new provider means writing one new adapter class
- Provider-specific error types are normalized at the adapter boundary
