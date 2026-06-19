# Mid-Semester Report

Project: Self-Correcting Financial Intelligence System

Student: [Your Name]

Department: M.Tech (BITS WILP)

Supervisor: [Supervisor Name]

Date: June 2026

---

## 1. Abstract

This project implements a Self-Correcting Financial Intelligence System that combines hybrid retrieval (FAISS + BM25), a teacher-student reasoning pipeline (large teacher model + lightweight student model), and an evaluator-in-the-loop to automatically detect and correct low-confidence or inconsistent outputs. The system ingests SEC filings and other financial documents, performs hybrid retrieval to obtain supporting evidence, generates answers via a distilled reasoning pipeline, evaluates outputs across multiple criteria (relevance, factual consistency, numerical coherence, entailment), and iteratively refines responses when confidence is below thresholds. The implementation includes a FastAPI backend, Streamlit frontend, containerization, monitoring, and documentation.

## 2. Objectives (Mid-Semester)

- Build a robust data ingestion pipeline for SEC filings and local documents.
- Implement hybrid retrieval combining dense (FAISS) and sparse (BM25) methods.
- Design and implement a teacher-student distillation workflow for financial reasoning.
- Create an evaluator agent to score answers and trigger self-correction loops.
- Provide a working prototype with API endpoints and a simple UI for demonstrations.

## 3. Progress to Date

All core components required for the mid-semester milestone are implemented and integrated:

- Data ingestion: `src/ingestion.py` with SEC EDGAR integration and Snowflake connector.
- Hybrid retrieval: `src/retrieval/hybrid_retriever.py` (FAISS + BM25, ranking logic).
- Reasoning pipeline: `src/reasoning/distillation.py` with teacher and student model flows.
- Evaluator: `src/evaluation/evaluator.py` providing multi-criteria assessment and correction recommendations.
- Orchestration: `src/orchestration/langgraph_orchestrator.py` implementing multi-agent workflows.
- Backend and frontend: `backend/api.py` (FastAPI) and `frontend/app.py` (Streamlit).
- Containerization: `Dockerfile`, `Dockerfile.frontend`, and `docker-compose.yml`.

Quantitative summary:

- Source code: ~4,000+ LOC across modules.
- Files added: project documentation, configuration, and deployment manifests.

## 4. Methodology and Implementation Details

- Hybrid Retrieval: embeddings (sentence-transformers) index stored in FAISS; BM25 for lexical matching; combined scoring via tunable weights.
- Knowledge Distillation: teacher (large LLM) produces soft targets; student model trained with combined distillation + task loss. Temperature scaling applied during distillation.
- Evaluator Agent: computes relevance, factual consistency, numerical coherence, and entailment scores; triggers re-querying or answer refinement when thresholds not met.
- Orchestration: LangGraph-based workflows that route requests between retriever, reader, reasoning, evaluator, and correction agents.

## 5. Results So Far

- Working prototype capable of answering financial queries with supporting evidence and confidence scores.
- Automatic correction loop demonstrated on sample queries: confidence improvements observed after 1–2 refinement iterations.
- End-to-end demo available locally via `docker-compose up` (API: `localhost:8000`, Frontend: `localhost:8501`).

## 6. Issues, Risks and Mitigations

- Large model resource requirements — mitigation: use teacher for offline distillation and student for inference.
- Potential for large repo size due to nested history backups (`.git.backup`) — mitigation: consider removing backups from repo or using submodules.
- Data privacy and access to paid APIs — mitigation: support on-premise adapters and local models where possible.

## 7. Remaining Work and Timeline

- Finalize evaluation metrics and automated reporting (2 weeks).
- Clean up repository (remove `.git.backup` from tracked files or convert to submodule) (1 week).
- Prepare mid-sem presentation materials and demo notebooks (1 week).
- Complete thesis chapter drafts and finalize documentation (3 weeks).

Planned milestones before end of semester:

1. Complete automated evaluation reports and benchmark results.
2. Stabilize deployment scripts and CI checks.
3. Finalize project report and presentation slides.

## 8. References

- Project documentation in repository: `README.md`, `QUICKSTART.md`, and architecture diagrams.
- Code modules: `src/ingestion.py`, `src/retrieval/hybrid_retriever.py`, `src/reasoning/distillation.py`, `src/evaluation/evaluator.py`, `src/orchestration/langgraph_orchestrator.py`.

## 9. Appendices

Appendix A — How to run locally

```bash
docker-compose up -d
# API: http://localhost:8000
# Frontend: http://localhost:8501
```

Appendix B — Notes on repository backups

- Nested repository metadata was backed up as `.git.backup` directories inside `Working_project/Mtech_project` to preserve history. If you want those removed from the public repo, I can remove them and add appropriate `.gitignore` entries.
