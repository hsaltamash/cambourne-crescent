# MCC East Bay WhatsApp Assistant

**Hackathon Submission – MCC Campus**

A WhatsApp-based AI assistant designed specifically for MCC East Bay (Pleasanton, CA) that provides instant, accurate, and trusted answers to common community questions.

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Features](#features)
- [How It Works](#how-it-works)
- [Safety & Trust](#safety--trust)
- [Design](#design)
- [Getting Started](#getting-started)
- [Future Enhancements](#future-enhancements)
- [Repository & License](#repository--license)

## Overview

During Ramadan and major community events, MCC East Bay receives a large number of repetitive questions from families, elders, and youth — especially around prayer times, programs, parking, kids' activities, and logistics. Most of this information already exists on websites, flyers, or announcements, but it is fragmented, time-sensitive, and hard to access quickly.

WhatsApp was chosen intentionally because it requires **no new app**, has **zero learning curve**, and is already widely used across all age groups.

## Problem Statement

- Repeated questions overload volunteers and staff during Ramadan
- Families struggle to find correct, up-to-date information quickly
- Websites are not always convenient for elders or busy parents
- Incorrect or guessed information can reduce trust

This assistant reduces friction by delivering **reliable answers instantly** in a channel people already use.

## Features

- **WhatsApp-first experience** — No app install, no sign-up required
- **Exact prayer times** — Fajr, Maghrib, Isha, Taraweeh from structured data
- **Ramadan programs & schedules** — Complete community calendar
- **Kids & family information** — Youth programs, accessibility, events
- **Facilities & logistics** — Parking, prayer space, services
- **Policies & contacts** — Official MCC information and support
- **Safe AI usage** — Strict guardrails (no religious rulings, no guessing)
- **Graceful fallback** — Clear responses when information is unavailable

## How It Works

The system uses a **tiered answer strategy**:

1. **Deterministic data first** — Exact prayer times and schedules from structured data (CSV), never AI-generated
2. **Curated knowledge base** — Policies, programs, and FAQs from MCC-maintained documents
3. **Constrained AI reasoning** — MCC East Bay–specific questions only, never generic religious guidance

If uncertain, the system clearly says so and directs users to official MCC sources or the imam.

## Safety & Trust

- No fatwas or religious rulings provided
- No guessing of times, dates, or prices
- Clear "I don't know" responses when appropriate
- Rate limiting and guardrails to prevent abuse
- AI usage is optional and controlled
- Designed to respect community trust

## Design

- **Separation of concerns** — Code, content, and configuration are cleanly separated
- **Content-driven updates** — MCC can update FAQs and schedules without touching code
- **Cost control** — "Bring Your Own API Key" so MCC controls AI usage and cost
- **Deployment flexibility** — Can be deployed as a locked-down Docker image if needed

## Getting Started

### Prerequisites

- Python 3.10 or newer
- Git
- Terminal (Command Prompt, PowerShell, or Mac/Linux terminal)

Optional (for full WhatsApp + AI functionality):
- Twilio account (WhatsApp Sandbox)
- OpenAI API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hsaltamash/mcc-whatsapp-bot
   cd mcc-whatsapp-bot
   ```

2. **Create and activate virtual environment:**

   On Windows:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   On macOS / Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   On Windows:
   ```bash
   setx OPENAI_API_KEY "your_api_key_here"
   ```

   On macOS / Linux:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

5. **Run the server:**
   ```bash
   python -m uvicorn app.main:app --reload --port 3000
   ```

   The service will start at: http://127.0.0.1:3000

### Testing

**Health check:**
```bash
curl http://127.0.0.1:3000/
```

**Test the WhatsApp webhook locally (without Twilio):**
```bash
curl -X POST "http://127.0.0.1:3000/whatsapp" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Body=What time is Maghrib today?"
```

## Knowledge Base

The assistant reads community information from:

```
kb/
├── faq_*.md                        # FAQs, programs, policies, facilities
├── daily_prayer_times.csv          # Daily prayer & Taraweeh times
└── README.md                       # This file
```

## Future Enhancements

- Multi-language support (English / Urdu / Hindi)
- Event reminders and broadcasts
- Analytics for unanswered questions
- Reusable framework for other community centers

## Notes for Reviewers

- The system prioritizes accuracy over novelty
- Exact prayer times are never generated by AI
- Religious rulings are intentionally excluded
- AI usage is constrained to MCC East Bay context only
- The project is designed to be immediately usable by the community

## Repository & License

**GitHub:** https://github.com/hsaltamash/mcc-whatsapp-bot

Developed as a hackathon project focused on **responsible, accurate, and community-centered use of AI** for MCC East Bay.
