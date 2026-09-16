from __future__ import annotations

import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from gateway.api.admin import router as admin_router
from gateway.api.chat import router as chat_router
from gateway.config import get_api_key, mask_key, settings
from gateway.core.errors import GatewayError

app = FastAPI(title="LLM Infrastructure Gateway", version="0.1.0")
app.include_router(chat_router)
app.include_router(admin_router)


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LLM Infrastructure</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; display: flex; justify-content: center; padding: 40px 20px; }
    .container { max-width: 640px; width: 100%; }
    h1 { font-size: 1.5rem; margin-bottom: 4px; }
    p.sub { color: #8b949e; margin-bottom: 24px; font-size: 0.9rem; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 16px; }
    label { display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px; color: #8b949e; }
    .input-row { display: flex; gap: 8px; margin-bottom: 16px; }
    .input-row input { flex: 1; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 10px 12px; color: #c9d1d9; font-size: 0.9rem; }
    .input-row input:focus { outline: none; border-color: #58a6ff; }
    .input-row input::placeholder { color: #484f58; }
    .btn { background: #238636; border: none; border-radius: 6px; color: #fff; padding: 10px 16px; font-size: 0.85rem; cursor: pointer; white-space: nowrap; }
    .btn:hover { background: #2ea043; }
    .btn-outline { background: transparent; border: 1px solid #30363d; color: #c9d1d9; }
    .btn-outline:hover { border-color: #58a6ff; color: #58a6ff; }
    .status { font-size: 0.8rem; margin-top: 4px; min-height: 1.2em; }
    .status.ok { color: #3fb950; }
    .status.info { color: #8b949e; }
    .badge { display: inline-block; background: #21262d; border-radius: 12px; padding: 2px 8px; font-size: 0.75rem; color: #8b949e; margin-left: 6px; }
    .badge.green { background: #23863620; color: #3fb950; border: 1px solid #23863640; }
  </style>
</head>
<body>
  <div class="container">
    <h1>LLM Infrastructure</h1>
    <p class="sub">Gateway Configuration</p>

    <div class="card">
      <h2 style="font-size:1rem;margin-bottom:16px;">Provider API Keys</h2>

      <form id="settings-form">
        <label>OpenAI API Key <span class="badge" id="openai-badge">not set</span></label>
        <div class="input-row">
          <input type="password" id="openai-key" placeholder="sk-..." autocomplete="off">
          <button type="submit" class="btn" data-provider="openai">Save</button>
        </div>

        <label>OpenRouter API Key <span class="badge" id="openrouter-badge">not set</span></label>
        <div class="input-row">
          <input type="password" id="openrouter-key" placeholder="sk-or-..." autocomplete="off">
          <button type="submit" class="btn" data-provider="openrouter">Save</button>
        </div>
      </form>
      <div class="status info" id="status-msg">Keys are stored in memory for this session.</div>
    </div>
  </div>

  <script>
    async function loadSettings() {
      const res = await fetch('/admin/settings');
      const data = await res.json();
      updateBadge('openai', data.openai_api_key, data.has_openai_env);
      updateBadge('openrouter', data.openrouter_api_key, data.has_openrouter_env);
    }

    function updateBadge(name, masked, hasEnv) {
      const badge = document.getElementById(name + '-badge');
      if (masked) {
        badge.textContent = masked + (hasEnv ? ' (env)' : '');
        badge.className = 'badge green';
      } else if (hasEnv) {
        badge.textContent = 'set via .env';
        badge.className = 'badge green';
      } else {
        badge.textContent = 'not set';
        badge.className = 'badge';
      }
    }

    document.getElementById('settings-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {};
      const openaiVal = document.getElementById('openai-key').value.trim();
      const orVal = document.getElementById('openrouter-key').value.trim();
      if (openaiVal) payload.openai_api_key = openaiVal;
      if (orVal) payload.openrouter_api_key = orVal;
      if (!Object.keys(payload).length) return;

      const res = await fetch('/admin/settings', { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
      const msg = document.getElementById('status-msg');
      if (res.ok) {
        msg.textContent = 'Keys saved for this session.';
        msg.className = 'status ok';
        document.getElementById('openai-key').value = '';
        document.getElementById('openrouter-key').value = '';
        loadSettings();
      } else {
        msg.textContent = 'Failed to save.';
        msg.className = 'status';
      }
    });

    loadSettings();
  </script>
</body>
</html>
"""  # noqa: E501


@app.exception_handler(GatewayError)
async def gateway_error_handler(request: Request, exc: GatewayError):
    request_id = request.headers.get("X-Request-ID", "")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(request_id=request_id),
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    request_id = request.headers.get("X-Request-ID", "")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "request_id": request_id,
            }
        },
    )


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level)
    uvicorn.run(
        "gateway.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
