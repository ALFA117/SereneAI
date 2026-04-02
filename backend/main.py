import os
import json
import base64
import asyncio
from pathlib import Path
from typing import List

import httpx
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sereneai_system_prompt import (
    detectar_crisis,
    limpiar_respuesta,
    build_system_prompt,
    build_image_prompt,
    MENSAJE_CRISIS,
    PROMPT_FRASE_CIERRE,
    PROMPT_RESUMEN_SESION,
)

load_dotenv()

OXLO_API_KEY = os.getenv("OXLO_API_KEY", "")
OXLO_BASE_URL = os.getenv("OXLO_BASE_URL", "https://api.oxlo.ai/v1")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:5500,http://localhost:5500").split(",")

DATA_DIR = Path(__file__).parent.parent / "data"
KB_PATH = DATA_DIR / "knowledge_base.json"
EMB_PATH = DATA_DIR / "embeddings.json"

app = FastAPI(title="SereneAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory state ──────────────────────────────────────────────────────────
knowledge_base: list = []
embeddings_cache: dict = {}


# ── Models ───────────────────────────────────────────────────────────────────
class Message(BaseModel):
    role: str   # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    transcribed_text: str


# ── Helpers ──────────────────────────────────────────────────────────────────
def oxlo_headers() -> dict:
    return {
        "Authorization": f"Bearer {OXLO_API_KEY}",
        "Content-Type": "application/json",
    }


def cosine_similarity(a: list, b: list) -> float:
    va = np.array(a, dtype=float)
    vb = np.array(b, dtype=float)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


async def get_embedding(text: str) -> list:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{OXLO_BASE_URL}/embeddings",
            headers=oxlo_headers(),
            json={"model": "bge-large", "input": text},
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]


def retrieve_top_k(query_vector: list, k: int = 3) -> list:
    scores = []
    for tech in knowledge_base:
        tech_vec = embeddings_cache.get(tech["id"])
        if tech_vec is None:
            continue
        sim = cosine_similarity(query_vector, tech_vec)
        scores.append((sim, tech))
    scores.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scores[:k]]


def format_tecnicas(tecnicas: list) -> str:
    return "\n\n".join(
        f"[{t['nombre']} — {t['categoria']}]\n{t['descripcion']}\nPasos: {t['pasos']}"
        for t in tecnicas
    )


# ── Startup ──────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    global knowledge_base, embeddings_cache

    if KB_PATH.exists():
        with open(KB_PATH, encoding="utf-8") as f:
            knowledge_base = json.load(f)
    else:
        print("WARNING: knowledge_base.json not found.")
        return

    if EMB_PATH.exists():
        with open(EMB_PATH, encoding="utf-8") as f:
            embeddings_cache = json.load(f)
        print(f"Loaded {len(embeddings_cache)} cached embeddings.")
    else:
        print("No embeddings cache found. Auto-generating in background...")
        asyncio.create_task(auto_generate_embeddings())


async def auto_generate_embeddings():
    global embeddings_cache
    cache = {}
    for tech in knowledge_base:
        if tech["id"] in cache:
            continue
        text = f"{tech['nombre']}. {tech['descripcion']}"
        for attempt in range(3):
            try:
                vec = await get_embedding(text)
                cache[tech["id"]] = vec
                await asyncio.sleep(1.5)
                break
            except Exception:
                if attempt < 2:
                    await asyncio.sleep(5)
    embeddings_cache = cache
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(EMB_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f)
    print(f"Auto-generated {len(cache)} embeddings.")


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "kb_loaded": len(knowledge_base),
        "embeddings_cached": len(embeddings_cache),
    }


@app.post("/generate-embeddings")
async def generate_embeddings():
    if not knowledge_base:
        raise HTTPException(status_code=500, detail="Knowledge base not loaded.")

    cache = dict(embeddings_cache)
    skipped = 0

    for i, tech in enumerate(knowledge_base):
        if tech["id"] in cache:
            skipped += 1
            print(f"[{i+1}/{len(knowledge_base)}] Skipped (cached): {tech['id']}")
            continue

        text = f"{tech['nombre']}. {tech['descripcion']}"
        for attempt in range(3):
            try:
                vector = await get_embedding(text)
                break
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    try:
                        err_body = e.response.json()
                    except Exception:
                        err_body = {}
                    retry_after = int(err_body.get("retry_after", 5))
                    if retry_after > 120:
                        raise HTTPException(status_code=429, detail=f"Daily limit reached. retry_after={retry_after}s")
                    print(f"Rate limited on '{tech['id']}', waiting {retry_after + 1}s...")
                    await asyncio.sleep(retry_after + 1)
                elif attempt < 2:
                    print(f"Oxlo error on '{tech['id']}', retrying in 5s... (attempt {attempt+1})")
                    await asyncio.sleep(5)
                else:
                    raise HTTPException(status_code=502, detail=f"Oxlo error on '{tech['id']}': {e.response.text}")

        cache[tech["id"]] = vector
        with open(EMB_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f)
        embeddings_cache[tech["id"]] = vector
        print(f"[{i+1}/{len(knowledge_base)}] Embedded: {tech['id']} - {tech['nombre']}")
        await asyncio.sleep(1.5)

    embeddings_cache.update(cache)
    return {"embedded": len(cache), "skipped": skipped, "path": str(EMB_PATH)}


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """Transcribe audio using Oxlo Whisper Large v3."""
    audio_bytes = await audio.read()

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{OXLO_BASE_URL}/audio/transcriptions",
            headers={"Authorization": f"Bearer {OXLO_API_KEY}"},
            files={"file": (audio.filename or "audio.webm", audio_bytes, audio.content_type or "audio/webm")},
            data={"model": "whisper-large-v3", "language": "es"},
        )
        resp.raise_for_status()

    return {"text": resp.json().get("text", "")}


@app.post("/chat")
async def chat(req: ChatRequest):
    """RAG pipeline: embed → retrieve → build prompt → LLM → clean → return."""
    user_text = req.transcribed_text

    # 1. Crisis detection — return fixed message immediately, skip LLM
    if detectar_crisis(user_text):
        return {**MENSAJE_CRISIS, "response": MENSAJE_CRISIS["texto"]}

    # 2. RAG retrieval
    tecnicas_contexto = None
    tecnica_principal = None
    if embeddings_cache:
        query_vec = await get_embedding(user_text)
        top_tecnicas = retrieve_top_k(query_vec, k=3)
        tecnicas_contexto = format_tecnicas(top_tecnicas)
        if top_tecnicas:
            tecnica_principal = top_tecnicas[0]["nombre"]

    # 3. Build system prompt with RAG context
    system_prompt = build_system_prompt(tecnicas_contexto=tecnicas_contexto)

    # 4. Build messages payload
    messages_payload = [{"role": "system", "content": system_prompt}]
    for msg in req.messages:
        messages_payload.append({"role": msg.role, "content": msg.content})

    # 5. Call LLM
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{OXLO_BASE_URL}/chat/completions",
            headers=oxlo_headers(),
            json={
                "model": "deepseek-r1-8b",
                "messages": messages_payload,
                "temperature": 0.65,
                "max_tokens": 200,
            },
        )
        resp.raise_for_status()

    raw = resp.json()["choices"][0]["message"]["content"]

    # 6. Strip <think>...</think> blocks from DeepSeek R1
    clean = limpiar_respuesta(raw)

    return {"response": clean, "es_crisis": False, "tecnica_rag": tecnica_principal}


@app.post("/synthesize")
async def synthesize(payload: dict):
    """Convert text to speech using Oxlo Kokoro 82M."""
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    # Limit to first 2 sentences to reduce latency
    sentences = [s.strip() for s in text.replace("?", ".").split(".") if s.strip()]
    tts_text = ". ".join(sentences[:2]) + "."

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{OXLO_BASE_URL}/audio/speech",
            headers=oxlo_headers(),
            json={
                "model": "kokoro-82m",
                "input": tts_text,
                "voice": "af_heart",
            },
        )
        resp.raise_for_status()

    # Validate we got actual audio, not a JSON error
    content_type = resp.headers.get("content-type", "")
    if "application/json" in content_type:
        raise HTTPException(status_code=502, detail=f"Kokoro returned JSON instead of audio: {resp.text}")

    # Detect actual format from magic bytes (RIFF = WAV, else assume mp3)
    fmt = "wav" if resp.content[:4] == b"RIFF" else "mp3"
    audio_b64 = base64.b64encode(resp.content).decode("utf-8")
    return {"audio_base64": audio_b64, "format": fmt}


@app.post("/session-summary")
async def session_summary(payload: dict):
    """Generate a warm session summary using DeepSeek."""
    messages = payload.get("messages", [])
    if not messages:
        raise HTTPException(status_code=400, detail="messages is required")

    messages_payload = [{"role": "system", "content": PROMPT_RESUMEN_SESION}]
    for msg in messages:
        messages_payload.append({"role": msg["role"], "content": msg["content"]})
    messages_payload.append({"role": "user", "content": "Genera el resumen de esta sesión."})

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{OXLO_BASE_URL}/chat/completions",
            headers=oxlo_headers(),
            json={"model": "deepseek-r1-8b", "messages": messages_payload, "temperature": 0.6, "max_tokens": 150},
        )
        resp.raise_for_status()

    raw = resp.json()["choices"][0]["message"]["content"]
    return {"summary": limpiar_respuesta(raw)}


@app.post("/generate-card")
async def generate_card(payload: dict):
    """Generate motivational image using Oxlo Image Pro."""
    phrase = payload.get("phrase", "")
    if not phrase:
        raise HTTPException(status_code=400, detail="phrase is required")

    image_prompt = build_image_prompt(phrase)

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{OXLO_BASE_URL}/images/generations",
            headers=oxlo_headers(),
            json={
                "model": "oxlo-image-pro",
                "prompt": image_prompt,
                "size": "1024x1024",
            },
        )
        resp.raise_for_status()

    item = resp.json()["data"][0]
    b64 = item.get("b64_json")
    url = item.get("url")
    image_src = f"data:image/png;base64,{b64}" if b64 else url
    return {"image_url": image_src}
