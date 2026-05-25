# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A WhatsApp-based AI assistant for Cambourne Crescent (Cambourne, UK) that answers community questions about prayer times, programmes, events, facilities, and services. Also serves a web chat UI at `/`. Built with FastAPI + Twilio + OpenAI (gpt-4o-mini). Deployed as a Docker container on Hostinger VPS behind Nginx at `cambournecrescent.imaginebest.com`.

## Commands

```bash
# Install dependencies
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 3000

# Health check
curl http://127.0.0.1:3000/health

# Test the WhatsApp webhook without Twilio
curl -X POST "http://127.0.0.1:3000/whatsapp" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Body=What time is Maghrib today?"

# Test the web chat API
curl -X POST "http://127.0.0.1:3000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What time is Maghrib today?"}'

# Docker (production)
docker compose -f docker-compose.prod.yml up --build -d
```

## Required Environment Variables

- `OPENAI_API_KEY` — optional; if missing, the bot runs in "demo mode" (returns raw KB snippets)
- Twilio credentials are only needed when connecting to WhatsApp Sandbox
- `CC_HTTP_PORT` — Docker host port (default `3006`); set in `.env`
- `CC_IMAGE` — Docker image name (default `cambourne-crescent:prod`)

## Architecture

Two entry points share the same answer pipeline:
- `POST /whatsapp` (`app/whatsapp.py`) — Twilio webhook, returns TwiML XML
- `POST /chat` + `GET /` (`app/chat.py`) — JSON API and embedded HTML web chat UI

Both call `check_all_prayers_request` → `check_prayer_time_shortcuts` → `answer_with_ai_or_fallback` → `clamp_reply`.

**Answer pipeline** (strict tier order):

1. **Tier 1 — Deterministic prayer times** (`app/prayers.py`): Regex-parses the message for a prayer name and date. If matched, reads directly from `kb/prayer_times_2026.csv` — no AI involved.

2. **Tier 2 — KB-grounded AI** (`app/ai.py`): `KnowledgeBase.retrieve_context_keyword()` scores paragraphs from all `kb/*.md` files by keyword frequency. If context is found, it is injected into a constrained OpenAI prompt.

3. **Tier 3 — CC-only AI fallback** (`app/ai.py`): If no KB context was found and the question doesn't ask for exact times/dates/prices, OpenAI answers with a stricter Cambourne Crescent-only prompt.

All replies are clamped to 1200 characters by `app/utils.py:clamp_reply`.

On startup, `app/lifespan.py` loads all `kb/*.md` files into memory and parses `kb/prayer_times_cambourne.csv` into the global `PRAYER_TIMES` dict (keyed by ISO date string).

## Key Design Constraints

- **No religious rulings (fatwas)** — system prompts hard-prohibit this.
- **No hallucinated times/dates/prices** — `_is_time_or_price_or_date_question()` guards the Tier 3 path.
- **Content-code separation** — updating community information means editing `kb/*.md` or `kb/prayer_times_2026.csv`; no code changes needed.

## Knowledge Base

`kb/` contains Cambourne Crescent-specific markdown files and a prayer times CSV:

- `kb/prayer_times_cambourne.csv` — columns: `date, fajr_start, fajr_jamaat, dhuhr_start, dhuhr_jamaat, asr_start, asr_jamaat, maghrib_start, maghrib_jamaat, isha_start, isha_jamaat` (plus location and metadata columns)
- `kb/cambourne_prayer.md` — Jumu'ah details, prayer info (used for prayer-specific AI routing)
- `kb/cambourne_services.md` — services and programmes (used for programmes AI routing)
- `kb/cambourne_events.md` — events, news, activities (used for events AI routing)
- `kb/cambourne_core.md` — organisation info, facilities, contact
- `kb/cambourne_faqs.md` — frequently asked questions

## Deployment

- **VPS path:** `/home/githubdeploy/cambourne-crescent`
- **Nginx:** `cambournecrescent.imaginebest.com` → `127.0.0.1:3006`
- **Container port:** 8000 (mapped to host port 3006)

### GitHub Actions (PROD environment)

Variables:
- `VPS_HOST` — Hostinger VPS IP
- `VPS_USER` — `githubdeploy`
- `VPS_PORT` — `22`
- `VPS_DEPLOY_PATH` — `/home/githubdeploy/cambourne-crescent`
- `CC_IMAGE` — `cambourne-crescent:prod`
- `CC_HTTP_PORT` — `3006`

Secrets:
- `VPS_SSH_PRIVATE_KEY` — private deploy SSH key
- `OPENAI_API_KEY` — OpenAI API key
