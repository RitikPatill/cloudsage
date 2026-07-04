# CloudSage — Build Tracker

> One sprint per week · each week = branch → PR → merge · every core component gets a 3-sentence
> **"how it works / why this tradeoff"** note written *by me* (the explain-it rule — no un-understood code).

**Current sprint: Week 1 — Foundations & safety net**

## Sprint checklist

### Week 1 — Foundations & safety net 🔄
- [x] Local repo scaffolded (git init, .gitignore, README, tracker)
- [x] Public GitHub repo created + branch protection on `main` ✅ 2026-07-04 (github.com/RitikPatill/cloudsage, PR #1 merged — PRs required on main)
- [ ] GitHub Project board with the 8-week backlog
- [x] AWS **Free account plan** created (NOT the paid plan!) ✅ 2026-07-04
- [x] Zero-spend budget + Free-Tier usage alerts (85%) enabled ✅ 2026-07-04
- [ ] IAM admin user + AWS CLI configured (`aws sts get-caller-identity` works) — CLI v2 installed ✅; IAM user + `aws configure` pending
- [x] Docker Desktop installed & running ✅ (pre-existing)
- [x] AWS MCP servers installed in IDE ✅ (.mcp.json: Docs + Terraform; Pricing/Cost follow once AWS credentials exist)
- [x] `ollama pull llama3.2:3b` for Week 2 ✅ 2026-07-04
- [x] **Demo win:** "hello RAG" — local script answering questions over one document ✅ (2026-07-04, `app/hello_rag.py` + `data/sample_aws_docs.md`; ran with deepseek-r1:1.5b — note: retrieval picked weak chunks (keyword overlap) and the tiny model garbled one fact → exactly what Week 2 (embeddings) and Week 5 (eval) fix)

### Week 2 — Path A: self-hosted RAG ⬜
- [ ] FastAPI service + Ollama (Llama/Mistral) + Qdrant via docker-compose
- [ ] Chunking + HF sentence-transformers embeddings; ingest AWS docs sample
- [ ] **Demo win:** `docker-compose up` → local GDPR-safe RAG with citations

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
