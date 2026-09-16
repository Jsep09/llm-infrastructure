# Architecture — LLM Infrastructure

## Why a Gateway?

Applications should not need to manage provider API keys, SDKs, token tracking, cost attribution, or error handling independently. The gateway centralizes these concerns.

## Why Not Call Providers Directly?

| Concern | Without Gateway | With Gateway |
|---------|----------------|--------------|
| API keys | Each app stores its own | Centralized, never exposed |
| Provider SDKs | Each app integrates separately | One adapter per provider |
| Model changes | Each app updates code | Change alias config |
| Token tracking | Each app implements | Built-in |
| Cost attribution | Manual or absent | Automatic |
| Rate limiting | Each app manages | Project-level enforcement |
| Fallback | Each app implements | Configured once |

## Why OpenRouter is an Upstream Provider

OpenRouter provides access to multiple models through one API, but it does not provide organizational identity, project-level API keys, internal policies, quotas, or cost attribution. Our gateway owns those concerns. Switching from OpenRouter to a direct provider should not affect applications.

## Why Model Aliases

Applications request internal aliases (e.g. support-standard) rather than provider model names. This decouples applications from provider-specific model identifiers and allows administrators to change the underlying model without application changes.

## Why Organization/Team/Project Identity

Every request is attributable to a specific project within a team within an organization. This enables usage tracking, cost attribution, policy enforcement, and auditing at the right granularity.

## Why Costs Are Attributed by Project

Organizations need to understand which workloads consume LLM budget. Project-level attribution enables this without application-level instrumentation.

## Why Retries Are Bounded

Unbounded retries can amplify costs, exceed rate limits, and mask underlying failures. Bounded retries with backoff provide resilience without uncontrolled spending.

## Why Fallback Is Explicit

Explicit fallback configuration ensures predictable behavior. Automatic/AI-based routing introduces non-determinism and complicates debugging.

## Why Prompts Are Not Logged by Default

Prompts may contain sensitive data. The infrastructure logs metadata (who, what model, how many tokens, cost) sufficient for observability without logging prompt content by default.

## Technology Decisions

- **Python/FastAPI**: Matches the async, I/O-bound nature of LLM proxy workloads
- **PostgreSQL**: Relational model fits the organizational hierarchy naturally
- **SSE**: Simple, standard, works with existing HTTP infrastructure
- **Modular monolith**: Avoids microservice complexity while maintaining separation of concerns
