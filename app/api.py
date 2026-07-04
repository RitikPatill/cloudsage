"""CloudSage API - Path A (self-hosted, GDPR-safe: nothing leaves this machine).

    POST /ask  ->  retrieve (Qdrant) -> confidence check -> generate (Ollama) -> cited answer
    GET  /healthz  ->  are Qdrant and Ollama reachable?

Key design decisions (interview material):
- The embedding model + DB client load ONCE at startup (lifespan), not per
  request - model loading costs seconds, a request must cost milliseconds.
- CONFIDENCE THRESHOLD: if the best retrieval score is below MIN_CONFIDENCE,
  we answer "I don't know" instead of letting the LLM guess. Low cosine
  similarity = "no document really matches" (the Step-2 lesson, applied).
- Citations always returned, even on "I don't know" - transparency over polish.

Run:  uvicorn app.api:app --port 8000        (interactive docs at /docs)
"""
import time
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from app.ingest import COLLECTION, MODEL_NAME

QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
LLM_MODEL = "llama3.2:3b"
MIN_CONFIDENCE = 0.35  # below this cosine score we refuse to guess

SYSTEM_PROMPT = (
    "You are CloudSage, an assistant that answers questions about AWS. "
    "Answer ONLY using the provided context sections. Be concise. "
    "After every fact, cite its section in brackets, e.g. [Vector stores: the big cost trap]. "
    "If the context does not contain the answer, say you don't know."
)

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["embedder"] = SentenceTransformer(MODEL_NAME)  # load once, reuse forever
    state["qdrant"] = QdrantClient(url=QDRANT_URL)
    yield
    state.clear()


app = FastAPI(title="CloudSage", version="0.1.0", lifespan=lifespan)


class AskRequest(BaseModel):
    question: str
    k: int = 3


class Citation(BaseModel):
    section: str
    score: float


class AskResponse(BaseModel):
    answer: str
    confident: bool
    citations: list[Citation]
    model: str
    latency_ms: int


@app.get("/healthz")
async def healthz() -> dict:
    checks = {}
    async with httpx.AsyncClient(timeout=5) as client:
        for name, url in [("qdrant", f"{QDRANT_URL}/healthz"), ("ollama", f"{OLLAMA_URL}/api/version")]:
            try:
                checks[name] = "ok" if (await client.get(url)).status_code == 200 else "unhealthy"
            except httpx.HTTPError:
                checks[name] = "unreachable"
    checks["status"] = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return checks


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    started = time.perf_counter()

    # 1. RETRIEVE - embed the question, find nearest chunks
    query_vector = state["embedder"].encode(req.question, normalize_embeddings=True).tolist()
    hits = state["qdrant"].query_points(
        collection_name=COLLECTION, query=query_vector, limit=req.k, with_payload=True
    ).points
    citations = [Citation(section=h.payload["section"], score=round(h.score, 3)) for h in hits]

    # 2. CONFIDENCE GATE - don't let the LLM guess on weak retrieval
    if not hits or hits[0].score < MIN_CONFIDENCE:
        return AskResponse(
            answer="I don't know - my documents don't cover this confidently.",
            confident=False,
            citations=citations,
            model=LLM_MODEL,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    # 3. GENERATE - answer only from the retrieved context, with citations
    context = "\n\n---\n\n".join(h.payload["text"] for h in hits)
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": LLM_MODEL,
                "stream": False,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {req.question}"},
                ],
            },
        )
        resp.raise_for_status()
        answer = resp.json()["message"]["content"].strip()

    return AskResponse(
        answer=answer,
        confident=True,
        citations=citations,
        model=LLM_MODEL,
        latency_ms=int((time.perf_counter() - started) * 1000),
    )
