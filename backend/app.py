"""FastAPI application for LLMShield Day 1."""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from .providers import get_provider
from .security_tests import run_security_scan

app = FastAPI(
    title="LLMShield API",
    description="Starter API for a local LLM security testing platform.",
    version="0.1.0",
)

# Development-only CORS configuration for the Vite dashboard.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)

class ChatResponse(BaseModel):
    reply: str
    provider: str
    demo_mode: bool

@app.get("/")
async def root():
    return {"name": "LLMShield API", "version": "0.1.0", "docs": "/docs"}

@app.get("/health")
async def health():
    provider = os.getenv("LLM_PROVIDER", "demo").strip().lower()
    return {"status": "ok", "provider": provider}

@app.get("/providers")
async def providers():
    selected = os.getenv("LLM_PROVIDER", "demo").strip().lower()
    return {
        "selected": selected,
        "supported": ["demo", "ollama", "openai"],
        "note": "Provider selection is configured on the backend using environment variables.",
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    provider_name = os.getenv("LLM_PROVIDER", "demo").strip().lower()
    try:
        provider = get_provider()
        reply = await provider.reply(request.message)
        return ChatResponse(
            reply=reply,
            provider=provider_name,
            demo_mode=(provider_name == "demo"),
        )
    except (httpx.HTTPError, RuntimeError, KeyError, IndexError) as exc:
        raise HTTPException(status_code=502, detail=f"Model provider error: {exc}") from exc
@app.post("/scan")
async def scan():
    try:
        return await run_security_scan()
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Security scan could not complete: {type(exc).__name__}",
        ) from exc