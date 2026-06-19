# FinIQ End-to-End Pipeline Diagram

This diagram captures the full system path from data sources through ingestion, retrieval, multi-agent orchestration, and delivery via API/UI.

```mermaid
flowchart TD
    %% =========================
    %% Initialization Path
    %% =========================
    subgraph INIT[System Initialization]
        A0[main.py / backend startup] --> A1[Load .env + system_config.yaml]
        A1 --> A2[Configure data sources]
        A2 --> A3[SnowflakeSource / SECFilingSource]
        A3 --> A4[Fetch and normalize documents]
        A4 --> A5[Generate embeddings\nall-MiniLM-L6-v2]
        A5 --> A6[Build HybridRetriever\nFAISS + BM25]
        A6 --> A7[Initialize DistillationPipeline\nTeacher + Student]
        A7 --> A8[Initialize EvaluatorAgent]
        A8 --> A9[Initialize MultiAgentOrchestrator]
        A9 --> A10[Pipeline Ready]
    end

    %% =========================
    %% Runtime Query Path
    %% =========================
    U1[User Query\nStreamlit or API Client] --> B1[FastAPI /query]
    B1 --> B2[orchestrator.execute_workflow]

    subgraph ORCH[Multi-Agent Orchestration Workflow]
        B2 --> C1[1) Retriever Agent\nHybrid retrieve top-k docs]
        C1 --> C2[2) Reader Agent\nPrepare top context]
        C2 --> C3[3) Reasoning Agent\nStudent inference]
        C3 --> C4[4) Evaluator Agent\nScore relevance/factual/numerical/entailment]
        C4 --> D1{Confidence >= threshold?}

        D1 -->|No| D2[Correction Agent\nTeacher-assisted refinement]
        D2 --> D3[Re-evaluate]
        D3 --> D4{Iterations < max?}
        D4 -->|Yes| D2
        D4 -->|No| C5

        D1 -->|Yes| C5[Verifier Agent\nCross-check vs context]
    end

    C5 --> E1[Final answer + confidence + evidence]
    E1 --> E2[FastAPI response payload]
    E2 --> E3[Streamlit UI cards/charts\nor API JSON consumer]

    %% =========================
    %% Side Outputs
    %% =========================
    E1 --> O1[Query logs / processing history]
    E1 --> O2[Workflow statistics endpoint]

    classDef init fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,color:#1b5e20;
    classDef run fill:#e3f2fd,stroke:#1565c0,stroke-width:1px,color:#0d47a1;
    classDef decision fill:#fff3e0,stroke:#ef6c00,stroke-width:1px,color:#e65100;
    classDef output fill:#f3e5f5,stroke:#6a1b9a,stroke-width:1px,color:#4a148c;

    class A0,A1,A2,A3,A4,A5,A6,A7,A8,A9,A10 init;
    class U1,B1,B2,C1,C2,C3,C4,D2,D3,D4,C5 run;
    class D1 decision;
    class E1,E2,E3,O1,O2 output;
```

## Notes

- Data ingestion supports Snowflake and SEC filing sources, with fallback sample data when required.
- Retrieval uses weighted fusion of dense (FAISS) and sparse (BM25) scores.
- The evaluator-driven correction loop retries up to configured max iterations.
- Final responses include answer text, confidence metrics, and supporting documents.
