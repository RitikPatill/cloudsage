# CloudSage — Build Tracker

> One sprint per week · each week = branch → PR → merge · every core component gets a 3-sentence
> **"how it works / why this tradeoff"** note written *by me* (the explain-it rule — no un-understood code).

**Current sprint: Week 2 — Path A: self-hosted RAG** *(Week 1 completed 2026-07-04 — same day!)*

## Sprint checklist

### Week 1 — Foundations & safety net 🔄
- [x] Local repo scaffolded (git init, .gitignore, README, tracker)
- [x] Public GitHub repo created + branch protection on `main` ✅ 2026-07-04 (github.com/RitikPatill/cloudsage, PR #1 merged — PRs required on main)
- [ ] GitHub Project board with the 8-week backlog
- [x] AWS **Free account plan** created (NOT the paid plan!) ✅ 2026-07-04
- [x] Zero-spend budget + Free-Tier usage alerts (85%) enabled ✅ 2026-07-04
- [x] IAM admin user + AWS CLI configured (`aws sts get-caller-identity` works) ✅ 2026-07-04 (`ritik-dev`, eu-central-1)
- [x] Docker Desktop installed & running ✅ (pre-existing)
- [x] AWS MCP servers installed in IDE ✅ (.mcp.json: Docs + Terraform + Pricing + Billing/Cost)
- [x] `ollama pull llama3.2:3b` for Week 2 ✅ 2026-07-04
- [x] **Demo win:** "hello RAG" — local script answering questions over one document ✅ (2026-07-04, `app/hello_rag.py` + `data/sample_aws_docs.md`; ran with deepseek-r1:1.5b — note: retrieval picked weak chunks (keyword overlap) and the tiny model garbled one fact → exactly what Week 2 (embeddings) and Week 5 (eval) fix)

### Week 2 — Path A: self-hosted RAG 🔄
- [x] **Step 1: Qdrant vector DB in Docker** ✅ 2026-07-04 — `deploy/docker-compose.yml`, image pinned v1.18.2; verified: healthz OK + full smoke test (create collection → insert vector → search scored 1.0 → cleanup)
- [x] **Step 2: Embeddings + semantic search** ✅ 2026-07-04 — `app/ingest.py` (chunk by section → all-MiniLM-L6-v2 embeddings → Qdrant) + `app/search.py --compare`. Findings: semantic won decisively on the vector-store question (0.842 vs #2 at 0.560); on a no-shared-words question the low top score (0.274) exposed *confidence* — something keyword scores can't do. Lesson: production systems use hybrid search (BM25 + vectors) + rerankers.
- [ ] Step 3: FastAPI service (`POST /ask`) + llama3.2 generation with citations
- [ ] Step 4: full stack in docker-compose (Qdrant + API together)
- [ ] **Demo win:** `docker compose up` → local GDPR-safe RAG with citations

### Week 3 — First AWS deploy (Terraform) ⬜
- [ ] Console-first walkthrough (S3, Lambda, HTTP API) → then codify in Terraform
- [ ] Least-privilege IAM roles; everything in eu-central-1
- [ ] **Demo win:** `terraform apply` → live cloud URL

### Week 4 — Managed cloud RAG = MVP ⬜
- [ ] Bedrock Knowledge Base + S3 Vectors; Nova 2 Lite via EU (Geo) profile
- [ ] Pluggable-backend refactor (Path A / Path B behind one interface)
- [ ] **Demo win (MVP):** cloud RAG answering with citations

### Week 5 — Evaluation + guardrails ⬜
- [ ] Golden Q&A set · Ragas + LLM-as-judge · MLflow tracking
- [ ] Prompt-injection / red-team suite
- [ ] Bedrock Guardrails + PII redaction
- [ ] **Demo win:** eval scorecard posted in every PR

### Week 6 — Agentic layer ⬜
- [ ] LangGraph agent + live AWS Pricing/Cost MCP tool
- [ ] Container-image Lambda (ECR lifecycle policy) + DynamoDB session memory
- [ ] **Demo win:** agent visibly calls the live cost tool in the trace

### Week 7 — Buffer + hardening ⬜
- [ ] Catch-up slack · CloudWatch dashboard (tokens/latency/cost) · SSM Parameter Store · IAM audit
- [ ] Optional stretch: LoRA reranker / kind K8s / Cognito / Athena+Glue / Langfuse / AgentCore

### Week 8 — Polish + demo + résumé ⬜
- [ ] Architecture diagram (Diagram MCP) · FinOps cost report proving ~€0
- [ ] README compliance section (GDPR / EU data residency) · 3-min demo video · `v1.0` release
- [ ] Résumé bullets + interview-prep dry run · cert plan (MLA-C01 → Terraform Associate)

## Cost-safety rules (never break)
Free account plan only · zero-spend budget before any resource · ❌ OpenSearch Serverless / NAT GW / EKS / ALB / RDS Multi-AZ / provisioned SageMaker endpoints / VPC-attached Lambdas · SSM Parameter Store (not Secrets Manager) · DuckDB (not Athena) by default · agent on Lambda (not AgentCore) · 7-day log retention · `terraform destroy` when idle.

## Explain-it notes ("how it works / why this tradeoff")
*(One short note per component, written by me after building it.)*

- **Week 1 — repo/git setup:** _pending_
- **Week 2 / Qdrant:** _DRAFT (Ritik: read, verify, rewrite in your own words):_ Qdrant is a database built for one job — storing vectors (lists of numbers representing meaning) and finding the closest ones fast. We run it as a Docker container with a named volume so the data survives restarts, and we pinned image v1.18.2 because "latest" can silently change under you. Chose Qdrant over alternatives because it's free/self-hosted (GDPR story), German-founded (interview talking point), and has a clean REST API.
- **Week 2 / Embeddings:** _DRAFT (Ritik: rewrite in your own words):_ An embedding model (all-MiniLM-L6-v2, 384 dims, runs on PyTorch) converts text to vectors where similar *meanings* land close together — so "keeps charging me money" can find "bill traps" without sharing words. Cosine similarity between the question vector and chunk vectors gives a *confidence score*: high = trust the match, low = say "I'm not sure" instead of hallucinating. Keyword matching can luck into right answers but its scores carry no meaning — that's why production RAG uses hybrid search (keywords + vectors) and rerankers.
