# LLM Infrastructure — Implementation Specification

## 1. Project Overview

### Project Name

`llm-infrastructure`

### Tagline

> One infrastructure layer to control how your organization uses LLMs.

### Description

A production-oriented LLM infrastructure project exploring centralized access, cost control, observability, reliability, and governance across LLM providers.

---

# 2. Project Purpose

This project implements an **organization-owned LLM control plane** between applications and external LLM providers.

Applications should not need to directly manage:

- Provider API keys
- Provider-specific SDKs
- Provider-specific models
- Provider-specific errors
- Token usage
- Cost tracking
- Rate limits
- Quotas
- Retry behavior
- Provider fallback
- Logging
- Observability

Instead:

```text
Applications
     │
     ▼
┌──────────────────────────────┐
│      LLM Infrastructure      │
│                              │
│ Authentication               │
│ Policy Enforcement           │
│ Model Abstraction            │
│ Rate Limiting                │
│ Quotas                       │
│ Usage Tracking               │
│ Cost Tracking                │
│ Observability                │
│ Reliability                  │
│ Provider Abstraction         │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
     OpenAI         OpenRouter
                         │
                    LLM Providers
```

The primary objective is educational and portfolio-oriented:

**Demonstrate understanding of production-oriented LLM infrastructure rather than simply wrapping an LLM API.**

---

# 3. Core Design Principle

Every infrastructure feature MUST answer:

> What problem does this solve that would otherwise need to be handled independently by applications calling LLM providers directly?

Do NOT add features merely because they are common in AI products.

Keep the system focused on LLM infrastructure.

---

# 4. Non-Goals

The project MUST NOT become:

- A chatbot product
- A RAG framework
- A vector database
- An agent framework
- A LangChain replacement
- A prompt management platform
- An OpenRouter clone
- A model training platform
- A fine-tuning platform
- A SaaS billing system
- A full enterprise IAM system
- A Kubernetes project
- A generic API gateway
- A complex model router

Do NOT implement:

- RAG
- Embeddings
- Vector search
- Agents
- Tool calling workflows
- Fine-tuning
- Model training
- Complex RBAC
- Payment processing
- AI-based model routing
- Kubernetes
- Service mesh
- Complex microservice architecture

Prefer a modular monolith.

---

# 5. Primary Use Case

Consider an organization with multiple AI applications:

```text
Company
│
├── Support Team
│   ├── Support Bot
│   └── Email Assistant
│
└── Engineering Team
    └── Coding Assistant
```

Without centralized infrastructure:

```text
Support Bot ───────→ OpenAI
Email Assistant ───→ OpenRouter
Coding Assistant ──→ OpenAI
```

Each application independently manages provider integration and infrastructure concerns.

With this project:

```text
Support Bot ───────┐
Email Assistant ───┼──→ LLM Infrastructure
Coding Assistant ──┘           │
                               ├── OpenAI
                               └── OpenRouter
```

The organization gains centralized control over LLM usage.

---

# 6. Organizational Domain Model

The system MUST model:

```text
Organization
    │
    └── Team
         │
         └── Project
              │
              └── API Key
```

## Organization

Represents the top-level organization using the infrastructure.

Example:

```text
Acme Corporation
```

## Team

Belongs to exactly one organization.

Examples:

```text
Support
Engineering
Marketing
```

## Project

Belongs to exactly one team.

Represents an application or workload consuming LLM resources.

Examples:

```text
support-bot
email-assistant
coding-agent
```

## API Key

Belongs to exactly one project.

Applications authenticate against the gateway using this key.

Provider credentials MUST NOT be exposed to applications.

---

# 7. Request Identity

Every successful authenticated LLM request MUST be attributable to:

```text
Organization
    ↓
Team
    ↓
Project
    ↓
API Key
    ↓
LLM Request
```

This relationship is fundamental to:

- Usage tracking
- Cost attribution
- Policies
- Quotas
- Auditing

---

# 8. Technology Stack

## Backend

```text
Python
FastAPI
Pydantic
SQLAlchemy
Alembic
PostgreSQL
Pytest
```

Use asynchronous APIs where appropriate.

## Frontend

```text
React
TypeScript
TanStack Query
```

Keep frontend dependencies minimal.

The frontend is a developer console, NOT a consumer chatbot.

## Streaming

Use:

```text
Server-Sent Events (SSE)
```

## Development

The system MUST run locally.

Docker Compose MAY be used for PostgreSQL.

Do not require Kubernetes.

---

# 9. Repository Structure

Preferred high-level structure:

```text
llm-infrastructure/
│
├── apps/
│   └── playground/
│
├── gateway/
│   ├── api/
│   ├── core/
│   ├── providers/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── schemas/
│   ├── policies/
│   └── tests/
│
├── migrations/
│
├── docs/
│   └── architecture.md
│
├── .env.example
├── .gitignore
├── README.md
├── SPEC.md
└── docker-compose.yml
```

Exact internal structure may evolve if justified.

Avoid unnecessary abstraction layers.

---

# 10. Gateway API

The primary inference endpoint:

```http
POST /v1/chat/completions
```

Example request:

```json
{
  "model": "support-standard",
  "messages": [
    {
      "role": "user",
      "content": "Explain vector embeddings."
    }
  ],
  "temperature": 0.7,
  "max_tokens": 500,
  "stream": true
}
```

IMPORTANT:

`model` represents an **internal model alias**, not necessarily the provider's actual model name.

---

# 11. Gateway Request Flow

Every LLM request should conceptually follow:

```text
Request
   ↓
Generate / Attach Request ID
   ↓
Authenticate API Key
   ↓
Resolve Organization / Team / Project
   ↓
Validate Request
   ↓
Load Project Policy
   ↓
Check Rate Limit
   ↓
Check Quota / Budget
   ↓
Resolve Model Alias
   ↓
Select Provider Adapter
   ↓
Execute Provider Request
   ↓
Normalize Response / Stream
   ↓
Collect Usage
   ↓
Calculate Estimated Cost
   ↓
Persist Request Metadata
   ↓
Emit Structured Logs / Metrics
   ↓
Return Response
```

The implementation should make this lifecycle understandable from the codebase.

---

# 12. Provider Abstraction

Create a common provider interface.

Conceptually:

```python
class LLMProvider:
    async def complete(...):
        ...

    async def stream(...):
        ...
```

Initial adapters:

```text
OpenAIProvider
OpenRouterProvider
```

Anthropic MAY be added later but is NOT required for the initial completion criteria.

Provider-specific SDK/API behavior MUST remain inside provider adapters whenever practical.

Business/application logic MUST NOT depend directly on the OpenAI SDK.

---

# 13. Why OpenRouter Is Supported

OpenRouter is treated as an **upstream provider**, not as the architecture of this system.

```text
Our LLM Infrastructure
          │
     ┌────┴─────────┐
     ▼              ▼
OpenAI Direct    OpenRouter
                    │
               Multiple Models
```

Our infrastructure owns organizational concerns such as:

- Project identity
- Internal API keys
- Internal policies
- Organizational quotas
- Cost attribution
- Auditability
- Internal model aliases

The organization MUST NOT be tightly coupled to OpenRouter.

---

# 14. Internal Model Catalog

Applications SHOULD NOT need to know provider-specific model identifiers.

Instead of:

```json
{
  "model": "provider-specific-model-name"
}
```

Applications can request:

```json
{
  "model": "support-standard"
}
```

Example internal configuration:

```text
Alias:
support-standard

Provider:
openrouter

Provider Model:
provider/model-name
```

Another alias:

```text
Alias:
coding-fast

Provider:
openai

Provider Model:
provider-model-name
```

---

# 15. Model Alias Resolution

Conceptually:

```text
support-standard
       ↓
Model Catalog
       ↓
Provider = OpenRouter
Provider Model = X
       ↓
OpenRouterProvider
```

The application should remain unchanged if administrators later configure:

```text
support-standard
       ↓
Provider = OpenAI
Provider Model = Y
```

This decoupling is a core demonstration of the project.

---

# 16. Authentication

Applications authenticate with gateway API keys.

Example:

```http
Authorization: Bearer <gateway-api-key>
```

Gateway API keys are NOT provider API keys.

Conceptually:

```text
Application
     │
Gateway API Key
     ↓
LLM Infrastructure
     │
Provider Credential
     ↓
LLM Provider
```

---

# 17. API Key Security

Requirements:

- Never store raw project API keys if avoidable.
- Store a secure hash of API keys.
- Display raw key only when created.
- Support revocation.
- Associate each key with a project.
- Track creation timestamp.
- Track revocation/status.
- Never log raw API keys.

Provider credentials MUST come from secure server-side configuration/environment variables for the MVP.

Never expose provider credentials to the frontend.

---

# 18. Project Policies

Each project may have an LLM usage policy.

Minimum supported policies:

```text
Allowed model aliases
Maximum input tokens
Maximum output tokens
Streaming allowed
```

Optional later policy:

```text
Allowed providers
```

Policy validation MUST occur before making an upstream request whenever possible.

---

# 19. Policy Example

Example:

```json
{
  "allowed_models": ["support-standard", "support-premium"],
  "max_input_tokens": 8000,
  "max_output_tokens": 1000,
  "streaming_allowed": true
}
```

If an application requests:

```text
coding-smart
```

but the project does not allow that alias, reject the request BEFORE calling the provider.

---

# 20. Rate Limiting

Implement project-level rate limiting.

Minimum MVP requirement:

```text
Requests per minute
```

Design should allow future support for:

```text
Tokens per minute
```

Do not overengineer distributed rate limiting for the first version.

A simple implementation is acceptable if clearly documented.

---

# 21. Quotas

Support at least one usage quota.

Recommended:

```text
Daily token quota
```

OR:

```text
Monthly estimated cost budget
```

If implementation complexity permits, support both.

The gateway should reject requests when a hard quota has been exceeded.

---

# 22. Cost Control Philosophy

The infrastructure should prevent avoidable upstream spending.

Checks that can occur before inference SHOULD occur before calling providers.

Example:

```text
Authentication failed
→ No provider call

Model forbidden
→ No provider call

Rate limit exceeded
→ No provider call

Quota exceeded
→ No provider call
```

---

# 23. Usage Tracking

Every completed LLM request MUST capture available usage information.

Minimum fields:

```text
request_id

organization_id
team_id
project_id
api_key_id

model_alias
provider
provider_model

input_tokens
output_tokens
total_tokens

estimated_cost

latency_ms
status

created_at
```

---

# 24. Cost Calculation

Create a centralized pricing mechanism.

Do NOT scatter model prices throughout provider code.

Conceptually:

```text
PricingRegistry
    │
    ├── model A
    │    ├── input price
    │    └── output price
    │
    └── model B
```

Estimated cost:

```text
input cost
+
output cost
=
request estimated cost
```

Pricing MUST be configurable because provider pricing changes over time.

Clearly label calculated values as estimated cost.

---

# 25. Observability

Every request MUST receive a unique:

```text
request_id
```

The same request ID should appear in:

- Logs
- Error responses
- Usage records
- Request records

This allows one inference request to be traced through the system.

---

# 26. Structured Logging

Prefer structured logs.

Example conceptual event:

```json
{
  "event": "llm_request_completed",
  "request_id": "req_xxx",
  "project_id": "project_xxx",
  "provider": "openai",
  "model_alias": "support-standard",
  "provider_model": "model-x",
  "latency_ms": 1420,
  "input_tokens": 400,
  "output_tokens": 120,
  "estimated_cost": 0.0012,
  "status": "success"
}
```

Do NOT log secrets.

Prompt/response logging should NOT be required for the MVP.

Prefer metadata logging to avoid unnecessary privacy risk.

---

# 27. LLM Metrics

Capture where practical:

```text
Request count
Success count
Failure count
Latency
Time to first token (TTFT)
Input tokens
Output tokens
Total tokens
Estimated cost
Provider
Provider model
Model alias
```

Do NOT build a full monitoring platform.

---

# 28. Error Normalization

Provider-specific exceptions MUST NOT leak directly to applications.

Normalize errors into gateway error codes.

Minimum error codes:

```text
INVALID_REQUEST
UNAUTHORIZED
MODEL_NOT_ALLOWED
POLICY_VIOLATION
RATE_LIMIT_EXCEEDED
QUOTA_EXCEEDED

PROVIDER_RATE_LIMITED
PROVIDER_TIMEOUT
PROVIDER_UNAVAILABLE
PROVIDER_ERROR

INTERNAL_ERROR
```

Example:

```json
{
  "error": {
    "code": "PROVIDER_TIMEOUT",
    "message": "The upstream LLM provider timed out.",
    "request_id": "req_xxx"
  }
}
```

---

# 29. Timeout Handling

Every provider request MUST have a configured timeout.

Provider requests must not wait indefinitely.

Timeout values should be configurable.

Timeouts MUST be observable through logs and request status.

---

# 30. Retry

Implement bounded retry behavior for appropriate transient failures.

Possible retryable failures:

```text
Temporary network failure
Provider 5xx
Selected provider rate-limit conditions
```

Do NOT retry indefinitely.

Use:

```text
Maximum retry count
Backoff
```

Retry attempts should be observable.

---

# 31. Retry Safety

Do not blindly retry every error.

Do NOT retry:

```text
Invalid request
Authentication failure
Policy violation
Unsupported model
Most deterministic client errors
```

Document retry policy.

---

# 32. Fallback

Support basic provider/model fallback.

Example:

```text
support-standard
      │
      ▼
OpenAI Model A
      │
    failure
      ▼
OpenRouter Model A
```

Fallback configuration MUST be explicit.

Do NOT implement intelligent/AI-based routing.

---

# 33. Fallback Observability

If fallback occurs, record:

```text
Original provider
Original model
Failure reason
Fallback provider
Fallback model
Retry/fallback count
```

The developer should be able to understand what happened to a request.

---

# 34. Streaming

Streaming is a core requirement.

Support:

```text
Provider Stream
      ↓
Gateway
      ↓
SSE
      ↓
Client
```

The gateway MUST NOT require buffering the complete LLM response before forwarding it.

---

# 35. Streaming Requirements

Handle:

```text
Normal stream completion
Provider stream error
Client disconnect
Provider disconnect
Final usage accounting
```

Measure:

```text
Time to First Token
Total latency
```

where technically possible.

---

# 36. Non-Streaming

The gateway should also support:

```json
{
  "stream": false
}
```

Both streaming and non-streaming requests should share as much infrastructure logic as reasonably possible.

---

# 37. Database

Use PostgreSQL.

Minimum logical entities:

```text
organizations
teams
projects
api_keys

model_aliases
project_policies

llm_requests
llm_usage
```

The exact normalization strategy may evolve.

---

# 38. Suggested Organization Schema

```text
organizations

id
name
created_at
updated_at
```

---

# 39. Suggested Team Schema

```text
teams

id
organization_id
name
created_at
updated_at
```

---

# 40. Suggested Project Schema

```text
projects

id
team_id
name
status
created_at
updated_at
```

---

# 41. Suggested API Key Schema

```text
api_keys

id
project_id
name
key_prefix
key_hash
status
created_at
revoked_at
```

Never store the raw API key.

---

# 42. Suggested Model Alias Schema

```text
model_aliases

id
alias
provider
provider_model
fallback_provider
fallback_model
enabled
created_at
updated_at
```

Exact fallback modeling may be changed if a cleaner design is justified.

---

# 43. Suggested Project Policy Schema

```text
project_policies

id
project_id

max_requests_per_minute
daily_token_quota
monthly_cost_budget

max_input_tokens
max_output_tokens
streaming_allowed

created_at
updated_at
```

Allowed model aliases may use a relation table if appropriate.

---

# 44. Suggested LLM Request Schema

```text
llm_requests

id
request_id

organization_id
team_id
project_id
api_key_id

model_alias
provider
provider_model

status
latency_ms
ttft_ms

retry_count
fallback_used

error_code

created_at
completed_at
```

---

# 45. Suggested Usage Schema

```text
llm_usage

id
llm_request_id

input_tokens
output_tokens
total_tokens

estimated_input_cost
estimated_output_cost
estimated_total_cost

created_at
```

---

# 46. Administrative APIs

Provide minimal APIs necessary to demonstrate infrastructure management.

At minimum support:

```text
Organizations
Teams
Projects
API Keys
Model Aliases
Project Policies
Usage
```

Exact endpoint naming may follow standard REST conventions.

Do NOT build a massive CRUD system.

Only implement operations needed to demonstrate the project.

---

# 47. Example Administrative Endpoints

Possible design:

```http
POST   /admin/organizations
POST   /admin/teams
POST   /admin/projects

POST   /admin/projects/{project_id}/keys
DELETE /admin/keys/{key_id}

POST   /admin/model-aliases
PATCH  /admin/model-aliases/{id}

PUT    /admin/projects/{project_id}/policy

GET    /admin/projects/{project_id}/usage
GET    /admin/usage
```

Admin authentication may be simplified for the portfolio MVP but MUST be documented.

Do not expose administrative mutation endpoints publicly without protection.

---

# 48. Developer Playground

Build a small web application.

Purpose:

> Test and observe the LLM infrastructure.

It is NOT a chatbot product.

---

# 49. Playground — Request Panel

Allow developer to configure:

```text
Project / API Key
Model Alias
Prompt
Temperature
Max Output Tokens
Streaming
```

Provide:

```text
Run
Cancel
```

---

# 50. Playground — Response Panel

Display:

```text
Response

Request ID
Model Alias
Provider
Actual Provider Model

Input Tokens
Output Tokens
Total Tokens

Estimated Cost

Latency
Time to First Token

Status
```

---

# 51. Playground — Usage View

Provide a lightweight usage page.

Show:

```text
Total Requests
Successful Requests
Failed Requests
Total Tokens
Estimated Cost
```

Allow basic grouping/filtering by:

```text
Project
Provider
Model
```

Avoid building a large analytics dashboard.

---

# 52. Playground Security

The frontend MUST NOT contain:

```text
OPENAI_API_KEY
OPENROUTER_API_KEY
Database credentials
Server secrets
```

The browser communicates only with our Gateway.

---

# 53. Configuration

Use environment variables for secrets.

Example `.env.example`:

```env
DATABASE_URL=

OPENAI_API_KEY=
OPENROUTER_API_KEY=

API_KEY_HASH_SECRET=

LOG_LEVEL=INFO
```

Do NOT commit `.env`.

---

# 54. Secret Safety

The public repository MUST contain no real credentials.

`.gitignore` MUST exclude:

```text
.env
.env.*
```

except:

```text
.env.example
```

Never include real credentials in:

- Tests
- Fixtures
- Documentation
- Screenshots
- Logs
- Git history

---

# 55. Testing Strategy

Testing is a core part of the project.

Use:

```text
Unit Tests
Integration Tests
Provider Contract Tests
```

Real provider API calls should NOT be required for the normal CI pipeline.

---

# 56. Unit Tests

Unit test infrastructure logic such as:

```text
API key verification
Model alias resolution
Policy validation
Rate limiting
Quota checks
Cost calculation
Error normalization
Retry decisions
Fallback decisions
```

---

# 57. Provider Tests

Provider adapters should be testable without real API calls.

Mock provider SDK/API responses.

Test:

```text
Successful completion
Streaming
Timeout
Rate limit
Provider error
Malformed response
Usage extraction
```

---

# 58. Integration Tests

Integration tests should verify gateway flow:

```text
API Request
    ↓
Authentication
    ↓
Policy
    ↓
Model Resolution
    ↓
Mock Provider
    ↓
Usage Persistence
    ↓
Response
```

Use a fake/mock provider rather than spending API credits.

---

# 59. Failure Scenario Tests

Explicitly test:

```text
Invalid API key
Revoked API key
Forbidden model
Exceeded rate limit
Exceeded quota
Provider timeout
Provider 5xx
Retry success
Retry exhaustion
Fallback success
Fallback failure
Client streaming disconnect
```

Infrastructure quality is demonstrated especially through failure behavior.

---

# 60. CI

CI should run:

```text
Lint
Type checks where configured
Unit tests
Integration tests
```

CI MUST NOT require real provider credentials.

CI MUST NOT call paid LLM APIs.

---

# 61. Database Migrations

Use Alembic.

Database schema changes MUST be represented by migrations.

Do not manually mutate production/development schema without migrations once the migration system is established.

---

# 62. Documentation

Maintain:

```text
README.md
SPEC.md
docs/architecture.md
```

README should explain the project at portfolio level.

SPEC defines implementation requirements.

Architecture documentation explains important design decisions and trade-offs.

---

# 63. Architecture Documentation

Document at least:

```text
Why a gateway exists
Why applications do not call providers directly
Why OpenRouter is an upstream provider
Why model aliases exist
Why organization/team/project identity exists
Why costs are attributed by project
Why retries are bounded
Why fallback is explicit
Why prompts are not logged by default
```

---

# 64. Architecture Decision Records

For significant decisions, optionally maintain:

```text
docs/decisions/
```

Example:

```text
001-provider-abstraction.md
002-model-aliases.md
003-streaming-sse.md
004-api-key-storage.md
```

Keep ADRs short.

The goal is to demonstrate reasoning, not documentation volume.

---

# 65. Development Principles

Follow:

```text
Simple before clever
Explicit before magical
Modular before microservices
Testable before abstract
Observable before optimized
```

Do not prematurely optimize.

---

# 66. Avoid Over-Abstraction

Do NOT create interfaces/classes merely for theoretical future use.

Abstractions should exist because at least one real boundary requires them.

Provider abstraction is justified because multiple upstream providers exist.

Do not build generic framework machinery without an actual use case.

---

# 67. Phase 1 — Basic Gateway

Goal:

```text
Client
  ↓
Gateway
  ↓
OpenAI
```

Implement:

- FastAPI application
- Configuration
- Request schema
- OpenAI provider adapter
- Non-streaming completion
- Basic error handling
- Basic tests

No database dependency should be necessary to understand the first vertical slice.

Success:

A request can travel through our gateway to OpenAI and return a normalized response.

---

# 68. Phase 2 — Provider Abstraction

Implement:

```text
LLMProvider interface
OpenAIProvider
OpenRouterProvider
```

Success:

Gateway business logic is not tied directly to one provider SDK.

Provider can be selected through configuration.

---

# 69. Phase 3 — Streaming

Implement:

```text
stream=true
SSE
provider streaming
client disconnect handling
TTFT measurement
```

Success:

Tokens are forwarded progressively without waiting for the complete answer.

---

# 70. Phase 4 — Organization Model

Implement:

```text
PostgreSQL
Alembic

Organization
Team
Project
API Key
```

Implement project API key authentication.

Success:

Every inference request can be attributed to a project/team/organization.

---

# 71. Phase 5 — Model Catalog & Governance

Implement:

```text
Model aliases
Project policies
Allowed models
Max token limits
Rate limiting
Quota
```

Success:

The gateway can reject an unauthorized/over-budget request before contacting the provider.

---

# 72. Phase 6 — Usage & Observability

Implement:

```text
Request persistence
Usage persistence
Token accounting
Estimated cost
Structured logging
Latency
TTFT
```

Success:

A developer can trace one request and determine:

```text
Who called it?
Which project?
Which alias?
Which provider?
Which actual model?
How many tokens?
How much estimated cost?
How long did it take?
Did it succeed?
```

---

# 73. Phase 7 — Reliability

Implement:

```text
Timeout
Retry
Backoff
Fallback
Error normalization
```

Success:

Provider failures behave predictably and are observable.

---

# 74. Phase 8 — Developer Playground

Implement React application.

Pages:

```text
Playground
Usage
```

Do not create unnecessary product pages.

Success:

The infrastructure can be demonstrated visually without external API clients.

---

# 75. Phase 9 — Hardening

Complete:

```text
Unit tests
Integration tests
Failure scenario tests
Security review
README
Architecture documentation
Example configuration
CI
```

---

# 76. Definition of Done — Main Demo

The final project MUST support this demonstration.

### Step 1

Create:

```text
Organization: Acme

Team: Support

Project: Support Bot
```

### Step 2

Generate an API key for:

```text
Support Bot
```

### Step 3

Configure:

```text
support-standard
    ↓
OpenRouter
    ↓
Provider Model A
```

### Step 4

Configure project policy:

```text
Allowed model:
support-standard

Max output:
500 tokens

Rate limit:
configured value

Quota:
configured value
```

### Step 5

Application sends:

```json
{
  "model": "support-standard",
  "messages": [
    {
      "role": "user",
      "content": "Explain RAG simply."
    }
  ],
  "stream": true
}
```

### Step 6

Gateway performs:

```text
Authenticate
↓
Resolve Project
↓
Check Policy
↓
Check Rate Limit
↓
Check Quota
↓
Resolve Alias
↓
Select Provider
↓
Call Provider
↓
Stream Response
↓
Collect Usage
↓
Calculate Cost
↓
Persist Metadata
↓
Log Completion
```

### Step 7

Developer can inspect:

```text
Request ID
Organization
Team
Project

Alias
Provider
Actual Model

Tokens
Estimated Cost
Latency
TTFT
Status
```

### Step 8

Change:

```text
support-standard
```

from:

```text
OpenRouter → Model A
```

to:

```text
OpenAI → Model B
```

### Step 9

Run the same application request without changing application integration.

The request should now use the newly configured provider/model.

This demonstrates the value of the infrastructure boundary.

---

# 77. Definition of Done — Failure Demo

The final project should also demonstrate failure scenarios.

Show:

```text
Forbidden model
→ rejected by policy

Exceeded rate limit
→ rejected before provider

Exceeded quota
→ rejected before provider

Provider timeout
→ bounded retry

Provider failure
→ configured fallback

Fallback failure
→ normalized error
```

Each should produce an observable request lifecycle.

---

# 78. Portfolio Objective

A reviewer should understand from the repository that the developer understands:

```text
LLM provider integration
Provider abstraction
LLM streaming
Token economics
Cost control
API security
LLM governance
Rate limiting
Quota enforcement
Observability
Reliability
Failure handling
Model abstraction
Production-oriented API design
Testing LLM infrastructure
```

The repository should demonstrate engineering reasoning, not only working code.

---

# 79. Expected Interview Explanation

The project should support the following explanation:

> I built an organization-owned LLM control plane that sits between applications and LLM providers.

> Applications authenticate using project-level API keys and request internal model aliases rather than depending directly on provider models.

> The gateway enforces project policies and quotas, resolves the configured provider, handles streaming and provider failures, and centrally records token usage, estimated cost, latency, and request metadata.

> OpenAI and OpenRouter are treated as interchangeable upstream providers rather than becoming architectural dependencies of individual applications.

---

# 80. Final Constraint

Do NOT attempt to build everything at once.

Implement one vertical slice at a time.

Each phase MUST:

1. Work.
2. Have tests.
3. Be understandable.
4. Be documented when architectural behavior changes.

Do not begin the next major phase while the current phase is fundamentally broken.

---

# 81. Agent Working Instructions

When implementing this specification:

- Read this entire specification before modifying architecture.
- Preserve the project's core purpose.
- Do not add unrelated AI features.
- Do not introduce a framework solely to reduce implementation effort if doing so hides the infrastructure concept being learned.
- Prefer standard libraries and focused dependencies.
- Keep provider-specific logic isolated.
- Keep domain/infrastructure boundaries understandable.
- Never commit secrets.
- Never call paid APIs from automated tests.
- Add tests alongside infrastructure behavior.
- Explain significant architectural decisions in documentation.
- Do not silently change API contracts.
- Do not overengineer for hypothetical scale.
- Do not convert the modular monolith into microservices.
- Treat OpenRouter as an upstream provider, not as a replacement for our gateway.
- Optimize for learning, code quality, and demonstrable infrastructure understanding.

If a requirement is ambiguous:

1. Prefer the simplest implementation satisfying the stated goal.
2. Avoid scope expansion.
3. Document the assumption.
4. Continue unless the decision would materially alter the architecture.

---

# 82. Guiding Question

Throughout development, continuously ask:

> Why should an application call this gateway instead of calling OpenAI or OpenRouter directly?

Every major feature in this repository should contribute to answering that question.
