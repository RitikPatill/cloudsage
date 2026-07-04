"""hello RAG — the entire RAG idea in ~50 lines, stdlib only.

    retrieve -> augment -> generate

1. Split a document into overlapping chunks.
2. RETRIEVE: score every chunk against the question (simple keyword overlap
   for now — Week 2 replaces this with real embeddings + Qdrant, and you'll
   see exactly WHY embeddings beat keywords).
3. AUGMENT: paste the top chunks into the prompt as context.
4. GENERATE: ask a local Ollama model to answer ONLY from that context,
   with a quoted citation. No context match -> it must say "I don't know".

Usage:
    python app/hello_rag.py "What is the cheapest way to host a vector store on AWS?"
    python app/hello_rag.py "..." --model deepseek-r1:8b --doc data/sample_aws_docs.md
"""
import argparse
import json
import re
import urllib.request
from pathlib import Path

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"

SYSTEM_PROMPT = (
    "You are CloudSage, an assistant that answers questions about AWS. "
    "Answer ONLY using the provided context. Quote the sentence you used as a citation. "
    "If the context does not contain the answer, say exactly: "
    "'I don't know — that is not in my documents.'"
)


def chunk(text: str, size: int = 180, overlap: int = 40) -> list[str]:
    """Split text into overlapping word-windows so facts never get cut in half."""
    words = text.split()
    step = size - overlap
    return [" ".join(words[i : i + size]) for i in range(0, max(len(words), 1), step)]


def score(question: str, chunk_text: str) -> float:
    """Keyword-overlap relevance (the Week-2 lesson: embeddings do this better)."""
    q_words = set(re.findall(r"\w+", question.lower()))
    c_words = re.findall(r"\w+", chunk_text.lower())
    hits = sum(1 for w in c_words if w in q_words)
    return hits / (len(c_words) ** 0.5) if c_words else 0.0


def retrieve(question: str, chunks: list[str], k: int = 3) -> list[str]:
    return sorted(chunks, key=lambda ch: score(question, ch), reverse=True)[:k]


def generate(question: str, context_chunks: list[str], model: str) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    }
    req = urllib.request.Request(
        OLLAMA_URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        answer = json.loads(resp.read())["message"]["content"]
    return re.sub(r"<think>.*?</think>", "", answer, flags=re.S).strip()  # strip R1 thinking


def main() -> None:
    parser = argparse.ArgumentParser(description="hello RAG — CloudSage day one")
    parser.add_argument("question")
    parser.add_argument("--doc", default="data/sample_aws_docs.md")
    parser.add_argument("--model", default="deepseek-r1:8b")
    args = parser.parse_args()

    chunks = chunk(Path(args.doc).read_text(encoding="utf-8"))
    top = retrieve(args.question, chunks)
    print(f"[retrieved {len(top)} of {len(chunks)} chunks]")
    for i, ch in enumerate(top, 1):
        print(f"  {i}. {ch[:90]}...")
    print("\n" + generate(args.question, top, args.model))


if __name__ == "__main__":
    main()
