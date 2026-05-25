import os
from openai import OpenAI
from app.lifespan import kb
from app.prayers import is_jumuah_question

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

SYSTEM_PROMPT_WITH_CONTEXT = """You are the Cambourne Crescent (Cambourne, UK) AI Assistant.

Rules:
- Use the provided CONTEXT to answer accurately and concisely.
- When the CONTEXT contains a schedule, times table, or specific times, ALWAYS include those details
  in your reply — do not withhold them or redirect to the website instead of providing them.
- After sharing times or schedule details from CONTEXT, you may add a one-line note to verify on
  cambournecrescent.org if the user needs live/holiday updates.
- If CONTEXT is missing/insufficient, you MAY answer ONLY if the answer is specifically about Cambourne Crescent
  (programmes, facilities, typical events, general logistics).
- If exact dates/times/prices are requested and not in CONTEXT, say you do not have that info and
  direct the user to the Cambourne Crescent official website or announcements.
- Do NOT provide fatwas or religious rulings. Advise asking the imam.
- Do NOT answer generic Islamic questions unrelated to Cambourne Crescent.
- Keep the reply short and practical for WhatsApp.
"""

SYSTEM_PROMPT_CC_ONLY = """You are answering ONLY questions about Cambourne Crescent (Cambourne, UK).

Allowed topics:
- Cambourne Crescent programmes and activities (including Ramadan programming at a high level)
- Cambourne Crescent facilities, services, logistics, and how to find official info
- How to navigate Cambourne Crescent information (website/calendar/contact)

Hard constraints:
- If the user asks for exact times/dates/prices and you don't have them, say you don't have that info and
  tell them to check Cambourne Crescent's official schedule or website.
- Do NOT give religious rulings (fatwas). Direct to the imam.
- Do NOT answer generic Islamic questions not specific to Cambourne Crescent.
- If the question isn't clearly about Cambourne Crescent, say you can only answer Cambourne Crescent questions.
- Keep it concise for WhatsApp.
"""

SYSTEM_PROMPT_PROGRAMS_EVENTS = """You are the Cambourne Crescent (Cambourne, UK) AI Assistant answering about programmes and events.

Key distinction — use it when helpful:
- PROGRAMMES: Recurring/ongoing activities (classes, halaqas, youth groups, etc.) — users register or enroll; schedule is consistent.
- EVENTS: One-time or seasonal calendar events (community festivals, special lectures, Eid events, etc.) — check the live calendar for exact dates.

Rules:
- List actual names from CONTEXT, not vague category labels.
- Group by audience when listing multiple: Youth, Children, Sisters/Women, Adults, General Community.
- If the user asked about programmes but upcoming events are also relevant (or vice versa), briefly mention both.
- Keep to the top 3–5 most relevant items; don't list everything.
- Always point to the right page: cambournecrescent.org for programmes and events.
- Do NOT provide fatwas or religious rulings.
- Keep it short and practical for WhatsApp.
"""

FALLBACK_NO_CONTEXT = (
    "I don't have that information in my notes. Please check Cambourne Crescent's official website "
    "at cambournecrescent.org or contact us directly. For religious rulings, please ask the imam."
)

_PROGRAMS_TERMS = [
    "program", "programme", "class", "classes", "course", "activit", "register", "enroll",
    "halaqa", "tajweed", "quran class", "arabic class", "sunday school",
    "scouts", "scouting", "new muslim", "convert",
    "playgroup", "toddler", "after school",
    "book club", "bookclub", "fajr breakfast", "shahada",
    "youth group", "sisters program", "women's program", "kids program",
    "children program", "family program",
]

_EVENTS_TERMS = [
    "event", "upcoming", "coming up", "this week", "next week",
    "this weekend", "next weekend", "what's happening", "whats happening",
    "what is happening", "calendar", "bazar", "bazaar",
    "festival", "tonight", "what's on",
]


def _is_programs_question(q: str) -> bool:
    s = q.lower()
    return any(t in s for t in _PROGRAMS_TERMS)


def _is_events_question(q: str) -> bool:
    s = q.lower()
    return any(t in s for t in _EVENTS_TERMS)


def _is_time_or_price_or_date_question(q: str) -> bool:
    s = q.lower()
    keywords = [
        "what time", "time is", "timing", "schedule", "starts at", "when is", "date", "tonight",
        "tomorrow", "today", "pm", "am",
        "price", "cost", "fee", "£", "$", "how much",
    ]
    return any(k in s for k in keywords)


def answer_with_ai_or_fallback(question: str) -> str:
    """
    Tiered approach:
    - If KB context exists: answer using context (preferred) + allow CC-only fill if needed.
    - If no KB context: allow CC-only high-level answers ONLY (no exact times/dates/prices, no rulings).
    - If no API key: still works in demo mode using KB context; otherwise returns a safe fallback.
    """
    question = (question or "").strip()

    if is_jumuah_question(question):
        context = kb.retrieve_context_from_file("kb/cambourne_prayer.md", f"jumuah juma friday prayer {question}")
        system_prompt = SYSTEM_PROMPT_WITH_CONTEXT
    elif _is_programs_question(question) or _is_events_question(question):
        is_prog = _is_programs_question(question)
        is_evt = _is_events_question(question)
        if is_prog and is_evt:
            prog_ctx = kb.retrieve_context_from_files(
                ["kb/cambourne_services.md", "kb/cambourne_events.md"], question, max_chars=1100
            )
            evt_ctx = kb.retrieve_context_from_file("kb/cambourne_events.md", question, max_chars=1100)
            context = f"[PROGRAMMES & SERVICES]\n{prog_ctx}\n\n[EVENTS]\n{evt_ctx}"
        elif is_prog:
            context = kb.retrieve_context_from_files(
                ["kb/cambourne_services.md", "kb/cambourne_events.md"], question
            )
        else:
            context = kb.retrieve_context_from_file("kb/cambourne_events.md", question)
        system_prompt = SYSTEM_PROMPT_PROGRAMS_EVENTS
    else:
        context = kb.retrieve_context_keyword(question)
        system_prompt = SYSTEM_PROMPT_WITH_CONTEXT

    if not client:
        if context:
            return f"(Demo mode)\nBased on Cambourne Crescent notes:\n{context[:600]}"
        return FALLBACK_NO_CONTEXT

    if context:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION:\n{question}"},
            ],
        )
        return resp.choices[0].message.content.strip()

    if _is_time_or_price_or_date_question(question):
        return FALLBACK_NO_CONTEXT

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_CC_ONLY},
            {"role": "user", "content": question},
        ],
    )
    return resp.choices[0].message.content.strip()
