# CloudSage ☁️🧭

**An agentic RAG assistant that is an expert on AWS — with citations, live pricing lookups, and a dual-path (self-hosted ↔ AWS serverless) architecture engineered to run at ~€0.**

> 🚧 **Status: Week 1 of 8 — Foundations & safety net.** Follow progress in [PROGRESS.md](PROGRESS.md).

## What it does

Ask CloudSage a question like *"What's the cheapest way to host a 5 GB vector store on AWS?"* and it:

1. **Retrieves** the relevant passages from ingested AWS documentation (RAG),
2. **Answers with citations** — grounded, no hallucinated facts,
3. Can call a **live AWS pricing tool** via MCP when the question is about costs (agentic tool use).

## Dual-path architecture (one codebase, two backends)

| | Path A — Self-hosted / Sovereign | Path B — AWS Serverless |
|---|---|---|
| LLM | Ollama (Llama / Mistral, quantized) | Amazon Bedrock (EU inference profile) |
| Embeddings | Hugging Face sentence-transformers | Amazon Titan Embeddings V2 |
| Vector store | Qdrant | Amazon S3 Vectors (Bedrock Knowledge Base) |
| Runtime | Docker Compose | AWS Lambda (container) + API Gateway |
| Data residency | Never leaves the machine (GDPR-safe by construction) | Pinned to eu-central-1 (Frankfurt), EU data residency |

Infrastructure is defined in **Terraform**, shipped by **GitHub Actions**, evaluated by a **Ragas + LLM-as-judge harness** (with a prompt-injection red-team suite), and observed via **CloudWatch** (tokens · latency · cost) and **MLflow**.

## Why this project exists

Built as a personal learning + portfolio project: production *practices* (CI/CD, IaC, evaluation gates, observability, least-privilege IAM) applied to a GenAI system, with a hard **€0 cost constraint** documented in a FinOps report.

*Architecture diagram, setup instructions, and the compliance (GDPR / EU data residency) notes land as the build progresses — see [PROGRESS.md](PROGRESS.md).*
