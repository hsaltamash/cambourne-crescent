from fastapi import FastAPI
from app.lifespan import lifespan
from app.whatsapp import router as whatsapp_router
from app.chat import router as chat_router

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(whatsapp_router)
app.include_router(chat_router)
