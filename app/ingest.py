"""Ingest: chunk a document -> embed each chunk -> store vectors in Qdrant.

This replaces Week 1's keyword matching with real semantic search:
- An EMBEDDING turns text into a vector (list of numbers) where texts with
  similar MEANING end up close together - even with zero shared words.
- Qdrant stores those vectors and finds the nearest ones to a query fast.

Chunking strategy: one chunk per '## section' of the markdown doc. Each
section here is a single coherent topic, which is exactly what you want a
retrieved chunk to be (one fact-neighborhood, no topic mixing).

Usage:
    python app/ingest.py                     # ingest data/sample_aws_docs.md
    python app/ingest.py --doc path/to.md    # ingest another document
"""
import argparse
import re
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # 384-dim, small + fast
COLLECTION = "aws_docs"


def chunk_by_section(text: str) -> list[dict]:
    """Split markdown into one chunk per '## heading' section."""
    chunks = []
    for part in re.split(r"(?m)^## ", text)[1:]:  # [0] is the intro/title
        lines = part.strip().splitlines()
        heading = lines[0].strip()
        body = " ".join(line.strip() for line in lines[1:] if line.strip())
        chunks.append({"section": heading, "text": f"{heading}. {body}"})
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="chunk -> embed -> store in Qdrant")
    parser.add_argument("--doc", default="data/sample_aws_docs.md")
    parser.add_argument("--url", default="http://localhost:6333")
    args = parser.parse_args()

    chunks = chunk_by_section(Path(args.doc).read_text(encoding="utf-8"))
    print(f"[chunk] {len(chunks)} sections from {args.doc}")

    model = SentenceTransformer(MODEL_NAME)
    vectors = model.encode(
        [c["text"] for c in chunks], normalize_embeddings=True, show_progress_bar=False
    )
    print(f"[embed] {len(vectors)} vectors of {len(vectors[0])} dimensions ({MODEL_NAME})")

    client = QdrantClient(url=args.url)
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)  # idempotent re-ingest for now
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=len(vectors[0]), distance=Distance.COSINE),
    )
    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(id=i, vector=vec.tolist(), payload=chunk)
            for i, (vec, chunk) in enumerate(zip(vectors, chunks))
        ],
        wait=True,
    )
    print(f"[store] {len(chunks)} chunks in Qdrant collection '{COLLECTION}' - done")


if __name__ == "__main__":
    main()
