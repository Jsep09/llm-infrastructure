# llm-infrastructure

> **"One infrastructure layer to control how your organization uses LLMs."**

A production-oriented LLM infrastructure project exploring centralized access, cost control, observability, reliability, and governance across LLM providers.

## Getting Started

Works the same on macOS, Linux, and Windows. Requires [uv](https://docs.astral.sh/uv/getting-started/installation/) (it installs the right Python version for you).

```bash
# 1. Install dependencies (creates .venv from uv.lock)
uv sync

# 2. Configure secrets
cp .env.example .env        # Windows PowerShell: Copy-Item .env.example .env

# 3. Run
uv run run.py dev           # gateway with hot reload at http://127.0.0.1:8000/docs
uv run run.py test          # test suite; extra args go to pytest, e.g. uv run run.py test -k chat
```
