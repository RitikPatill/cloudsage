"""Semantic search over the Qdrant collection - with an optional side-by-side
comparison against Week 1's keyword matching, to show WHY embeddings win.

Usage:
    python app/search.py "How do I avoid surprise bills?"
    python app/search.py "How do I avoid surprise bills?" --compare
"""
import argparse
import re
from pathlib import Path

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from ingest import COLLECTION, MODEL_NAME, chunk_by_section


def keyword_score(question: str, chunk_text: str) -> float:
    """Week 1's naive keyword-overlap scoring (kept for the comparison demo)."""
    q_words = set(re.findall(r"\w+", question.lower()))
    c_words = re.findall(r"\w+", chunk_text.lower())
    hits = sum(1 for w in c_words if w in q_words)
    return hits / (len(c_words) ** 0.5) if c_words else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="semantic search (vs keyword)")
    parser.add_argument("question")
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--url", default="http://localhost:6333")
    parser.add_argument("--doc", default="data/sample_aws_docs.md")
    parser.add_argument("--compare", action="store_true", help="also show keyword ranking")
    args = parser.parse_args()

    model = SentenceTransformer(MODEL_NAME)
    query_vector = model.encode(args.question, normalize_embeddings=True).tolist()
    hits = QdrantClient(url=args.url).query_points(
        collection_name=COLLECTION, query=query_vector, limit=args.k, with_payload=True
    ).points

    print(f"\n=== SEMANTIC search (embeddings + Qdrant) for: {args.question!r} ===")
    for h in hits:
        print(f"  {h.score:.3f}  {h.payload['section']}")

    if args.compare:
        chunks = chunk_by_section(Path(args.doc).read_text(encoding="utf-8"))
        ranked = sorted(chunks, key=lambda c: keyword_score(args.question, c["text"]), reverse=True)
        print(f"\n=== KEYWORD search (Week 1 method) for: {args.question!r} ===")
        for c in ranked[: args.k]:
            print(f"  {keyword_score(args.question, c['text']):.3f}  {c['section']}")


if __name__ == "__main__":
    main()
