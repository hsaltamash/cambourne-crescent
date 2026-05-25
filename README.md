# Cambourne Crescent AI Assistant

An AI assistant for [Cambourne Crescent](https://www.cambournecrescent.org/) — caring for local Muslims and the wider community of Cambourne, UK. Answers community questions via WhatsApp and a web chat interface.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Safety & Trust](#safety--trust)
- [Getting Started](#getting-started)
- [Knowledge Base](#knowledge-base)
- [Deployment](#deployment)

## Overview

Cambourne Crescent receives frequent questions from community members about prayer times, programmes, facilities, and events. This assistant provides instant, accurate answers via WhatsApp (no app install needed) and a web chat UI, reducing the burden on volunteers while ensuring information stays trusted and verified.

## Features

- **WhatsApp-first experience** — No app install, no sign-up required
- **Web chat UI** — Available at the root URL (`/`)
- **Exact prayer times** — Fajr, Dhuhr, Asr, Maghrib, Isha from structured data; never AI-generated
- **Jumu'ah information** — Automated Friday prayer details
- **Community programmes & events** — Powered by the Cambourne Crescent knowledge base
- **Facilities & logistics** — Location, services, contact information
- **Safe AI usage** — Strict guardrails (no religious rulings, no guessing on exact values)
- **Graceful fallback** — Clear responses directing to official sources when information is unavailable

## How It Works

The system uses a **tiered answer strategy**:

1. **Deterministic data first** — Exact prayer times from a structured CSV, never AI-generated
2. **Curated knowledge base** — Programmes, events, FAQs, and facilities from maintained Markdown files
3. **Constrained AI reasoning** — Cambourne Crescent–specific questions only, never generic religious guidance

If uncertain, the system clearly says so and directs users to `cambournecrescent.org` or the imam.

## Safety & Trust

- No fatwas or religious rulings provided
- No guessing of times, dates, or prices
- Clear "I don't know" responses when appropriate
- Designed to respect community trust

## Getting Started

### Prerequisites

- Python 3.10 or newer
- Git

Optional (for full WhatsApp + AI functionality):
- Twilio account (WhatsApp Sandbox)
- OpenAI API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd cambourne-crescent
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

5. **Run the server:**
   ```bash
   uvicorn app.main:app --reload --port 3000
   ```

   The service will start at: http://127.0.0.1:3000

### Testing

**Health check:**
```bash
curl http://127.0.0.1:3000/health
```

**Test the WhatsApp webhook locally (without Twilio):**
```bash
curl -X POST "http://127.0.0.1:3000/whatsapp" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Body=What time is Maghrib today?"
```

**Test the web chat API:**
```bash
curl -X POST "http://127.0.0.1:3000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What time is Maghrib today?"}'
```

## Knowledge Base

The assistant reads community information from:

```
kb/
├── cambourne_core.md          # Organisation info, facilities, contact
├── cambourne_prayer.md        # Prayer and Jumu'ah details
├── cambourne_services.md      # Services and recurring programmes
├── cambourne_events.md        # Events, news, activities
├── cambourne_faqs.md          # Frequently asked questions
└── prayer_times_cambourne.csv # Daily prayer times (adhan + jamaat)
```

To update community information, edit the relevant `kb/*.md` file or the CSV — no code changes required.

The CSV format expected by the app:

```
date,fajr_start,fajr_jamaat,dhuhr_start,dhuhr_jamaat,asr_start,asr_jamaat,maghrib_start,maghrib_jamaat,isha_start,isha_jamaat
2026-05-25,03:00,03:20,13:02,,18:27,,21:06,21:10,22:14,22:30
```

## Deployment

The app runs as a Docker container on a Hostinger VPS behind Nginx.

- **URL:** https://cambournecrescent.imaginebest.com
- **VPS path:** `/home/githubdeploy/cambourne-crescent`
- **Host port:** `3006` → container port `8000`

### Docker (manual)

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

### GitHub Actions

Pushing to `main` triggers the deploy workflow automatically. Configure the `PROD` environment in GitHub with:

**Variables:**
- `VPS_HOST`, `VPS_USER`, `VPS_PORT`, `VPS_DEPLOY_PATH`
- `CC_IMAGE=cambourne-crescent:prod`
- `CC_HTTP_PORT=3006`

**Secrets:**
- `VPS_SSH_PRIVATE_KEY`
- `OPENAI_API_KEY`

### Verify deployment

```bash
curl -I https://cambournecrescent.imaginebest.com
curl -X POST "https://cambournecrescent.imaginebest.com/whatsapp" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Body=What time is Maghrib today?"
```
