from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from app.prayers import check_prayer_time_shortcuts, check_all_prayers_request
from app.ai import answer_with_ai_or_fallback
from app.utils import clamp_reply

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(req: ChatRequest):
    try:
        user_msg = (req.message or "").strip()
        reply = check_all_prayers_request(user_msg)
        if not reply:
            reply = check_prayer_time_shortcuts(user_msg)
        if not reply:
            reply = answer_with_ai_or_fallback(user_msg)
        reply = clamp_reply(reply)
    except Exception:
        reply = "Sorry — the assistant hit an error. Please try again."
    return JSONResponse({"reply": reply})


_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Cambourne Crescent AI Assistant</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: #f0f4f8;
      height: 100dvh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }

    .shell {
      width: 100%;
      max-width: 700px;
      height: 100dvh;
      max-height: 820px;
      display: flex;
      flex-direction: column;
      background: #fff;
      border-radius: 20px;
      box-shadow: 0 8px 40px rgba(0,0,0,0.13);
      overflow: hidden;
    }

    /* ── Header ── */
    .header {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 18px 24px;
      background: linear-gradient(135deg, #1a6b3c 0%, #2d9b60 100%);
      flex-shrink: 0;
    }

    .header img {
      width: 48px;
      height: 48px;
      object-fit: contain;
      border-radius: 10px;
      background: #fff;
      padding: 6px;
      flex-shrink: 0;
    }

    .header-text h1 {
      font-size: 1.15rem;
      font-weight: 700;
      color: #fff;
      letter-spacing: 0.01em;
    }

    .header-text p {
      font-size: 0.78rem;
      color: rgba(255,255,255,0.78);
      margin-top: 2px;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      background: #6ef59a;
      border-radius: 50%;
      display: inline-block;
      margin-right: 5px;
    }

    /* ── Messages ── */
    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 24px 20px 16px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      scroll-behavior: smooth;
    }

    .messages::-webkit-scrollbar { width: 5px; }
    .messages::-webkit-scrollbar-track { background: transparent; }
    .messages::-webkit-scrollbar-thumb { background: #d0d7de; border-radius: 4px; }

    .bubble-row {
      display: flex;
      align-items: flex-end;
      gap: 8px;
    }

    .bubble-row.user { flex-direction: row-reverse; }

    .avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.8rem;
      font-weight: 700;
    }

    .avatar.bot {
      background: linear-gradient(135deg, #1a6b3c, #2d9b60);
      color: #fff;
    }

    .avatar.user-av {
      background: #e8f4fd;
      color: #1a6b3c;
    }

    .bubble {
      max-width: 72%;
      padding: 12px 16px;
      border-radius: 18px;
      font-size: 0.93rem;
      line-height: 1.55;
      word-wrap: break-word;
      white-space: pre-wrap;
    }

    .bubble.bot {
      background: #f4faf7;
      color: #1a2e1f;
      border-bottom-left-radius: 4px;
      border: 1px solid #d6ede3;
    }

    .bubble.user {
      background: linear-gradient(135deg, #1a6b3c, #2d9b60);
      color: #fff;
      border-bottom-right-radius: 4px;
    }

    .time {
      font-size: 0.68rem;
      color: #9aab9e;
      margin-top: 4px;
      padding: 0 4px;
      text-align: right;
    }

    .bubble-row.user .time { text-align: right; }

    /* typing indicator */
    .typing-row { display: flex; align-items: flex-end; gap: 8px; }
    .typing-bubble {
      background: #f4faf7;
      border: 1px solid #d6ede3;
      border-radius: 18px;
      border-bottom-left-radius: 4px;
      padding: 14px 18px;
      display: flex;
      gap: 5px;
      align-items: center;
    }
    .dot {
      width: 7px; height: 7px;
      background: #2d9b60;
      border-radius: 50%;
      animation: bounce 1.2s infinite ease-in-out;
    }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
      0%, 60%, 100% { transform: translateY(0); }
      30% { transform: translateY(-6px); }
    }

    /* ── Input bar ── */
    .input-bar {
      display: flex;
      align-items: flex-end;
      gap: 10px;
      padding: 14px 20px 18px;
      background: #fff;
      border-top: 1px solid #e8edf0;
      flex-shrink: 0;
    }

    textarea {
      flex: 1;
      resize: none;
      border: 1.5px solid #c8d6cc;
      border-radius: 14px;
      padding: 12px 16px;
      font-size: 0.93rem;
      font-family: inherit;
      color: #1a2e1f;
      line-height: 1.5;
      max-height: 130px;
      overflow-y: auto;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
    }

    textarea:focus {
      border-color: #2d9b60;
      box-shadow: 0 0 0 3px rgba(45,155,96,0.12);
    }

    textarea::placeholder { color: #a8b9ae; }

    .send-btn {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      border: none;
      background: linear-gradient(135deg, #1a6b3c, #2d9b60);
      color: #fff;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: opacity 0.15s, transform 0.1s;
    }

    .send-btn:hover:not(:disabled) { opacity: 0.88; transform: scale(1.04); }
    .send-btn:disabled { opacity: 0.45; cursor: not-allowed; }

    .send-btn svg { width: 20px; height: 20px; fill: none; stroke: #fff; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }

    /* ── Footer ── */
    .footer {
      text-align: center;
      font-size: 0.7rem;
      color: #b0bcb5;
      padding: 0 0 12px;
      flex-shrink: 0;
    }
  </style>
</head>
<body>
<div class="shell">

  <div class="header">
    <img src="http://www.cambournecrescent.org/wp-content/uploads/2018/01/cambourne-crescent-logo3.svg" alt="Cambourne Crescent logo" />
    <div class="header-text">
      <h1>Cambourne Crescent AI Assistant</h1>
      <p><span class="status-dot"></span>Caring for the community of Cambourne</p>
    </div>
  </div>

  <div class="messages" id="messages">
    <div class="bubble-row">
      <div class="avatar bot">C</div>
      <div>
        <div class="bubble bot">As-salamu alaykum! I'm the Cambourne Crescent AI Assistant. I can answer questions about prayer times, programmes, facilities, and community services. How can I help you today?</div>
        <div class="time" id="init-time"></div>
      </div>
    </div>
  </div>

  <div class="input-bar">
    <textarea id="input" rows="1" placeholder="Ask about prayer times, programmes, community…" maxlength="500"></textarea>
    <button class="send-btn" id="send-btn" onclick="sendMessage()" title="Send">
      <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
    </button>
  </div>

  <div class="footer">Powered by Cambourne Crescent &bull; AI responses may not be 100% accurate &mdash; always verify with Cambourne Crescent directly</div>

</div>

<script>
  const messagesEl = document.getElementById('messages');
  const inputEl = document.getElementById('input');
  const sendBtn = document.getElementById('send-btn');

  document.getElementById('init-time').textContent = now();

  function now() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function scrollBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function addBubble(text, who) {
    const row = document.createElement('div');
    row.className = 'bubble-row' + (who === 'user' ? ' user' : '');

    const av = document.createElement('div');
    av.className = 'avatar ' + (who === 'user' ? 'user-av' : 'bot');
    av.textContent = who === 'user' ? 'You' : 'C';

    const wrap = document.createElement('div');

    const bubble = document.createElement('div');
    bubble.className = 'bubble ' + who;
    bubble.textContent = text;

    const t = document.createElement('div');
    t.className = 'time';
    t.textContent = now();

    wrap.appendChild(bubble);
    wrap.appendChild(t);
    row.appendChild(av);
    row.appendChild(wrap);
    messagesEl.appendChild(row);
    scrollBottom();
    return row;
  }

  function showTyping() {
    const row = document.createElement('div');
    row.className = 'typing-row';
    row.id = 'typing';

    const av = document.createElement('div');
    av.className = 'avatar bot';
    av.textContent = 'C';

    const bubble = document.createElement('div');
    bubble.className = 'typing-bubble';
    bubble.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';

    row.appendChild(av);
    row.appendChild(bubble);
    messagesEl.appendChild(row);
    scrollBottom();
  }

  function hideTyping() {
    const el = document.getElementById('typing');
    if (el) el.remove();
  }

  inputEl.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  inputEl.addEventListener('input', () => {
    inputEl.style.height = 'auto';
    inputEl.style.height = Math.min(inputEl.scrollHeight, 130) + 'px';
  });

  async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text) return;

    addBubble(text, 'user');
    inputEl.value = '';
    inputEl.style.height = 'auto';
    sendBtn.disabled = true;
    showTyping();

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      hideTyping();
      addBubble(data.reply || 'No response received.', 'bot');
    } catch (err) {
      hideTyping();
      addBubble('Connection error. Please try again.', 'bot');
    } finally {
      sendBtn.disabled = false;
      inputEl.focus();
    }
  }
</script>
</body>
</html>"""


@router.get("/", response_class=HTMLResponse)
async def cambourne_crescent_assistant():
    return HTMLResponse(_HTML)
