"""
Generate Architecture Diagram for FinIQ – Financial Intelligence System
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

fig, ax = plt.subplots(1, 1, figsize=(22, 14))
ax.set_xlim(0, 22)
ax.set_ylim(0, 14)
ax.axis("off")
fig.patch.set_facecolor("#0f1923")
ax.set_facecolor("#0f1923")

# ── Colour palette ────────────────────────────────────────────────────────────
C = {
    "title_bg":    "#1a2a3a",
    "data_bg":     "#1b3a5c",
    "data_bdr":    "#2980b9",
    "ingest_bg":   "#1a3a2a",
    "ingest_bdr":  "#27ae60",
    "agent_bg":    "#2d1b4e",
    "agent_bdr":   "#8e44ad",
    "reason_bg":   "#3a1a1a",
    "reason_bdr":  "#e74c3c",
    "eval_bg":     "#1a2a3a",
    "eval_bdr":    "#2ecc71",
    "api_bg":      "#1a2535",
    "api_bdr":     "#3498db",
    "ui_bg":       "#1a3025",
    "ui_bdr":      "#00d2ff",
    "text":        "#ecf0f1",
    "subtext":     "#bdc3c7",
    "arrow":       "#7f8c8d",
    "highlight":   "#f39c12",
}

def box(ax, x, y, w, h, bg, border, radius=0.3, lw=2.0):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle=f"round,pad=0,rounding_size={radius}",
                          facecolor=bg, edgecolor=border,
                          linewidth=lw, zorder=3)
    ax.add_patch(rect)

def label(ax, x, y, txt, fs=9, color="#ecf0f1", bold=False, ha="center", va="center"):
    weight = "bold" if bold else "normal"
    ax.text(x, y, txt, fontsize=fs, color=color, ha=ha, va=va,
            fontweight=weight, zorder=5,
            fontfamily="DejaVu Sans")

def arrow(ax, x1, y1, x2, y2, color="#7f8c8d", lw=1.5, style="->"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, connectionstyle="arc3,rad=0.0"),
                zorder=4)

def section_header(ax, x, y, w, h, title, bg, border):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0,rounding_size=0.25",
                          facecolor=border, edgecolor=border,
                          linewidth=0, zorder=3)
    ax.add_patch(rect)
    label(ax, x + w/2, y + h/2, title, fs=8.5, bold=True, color="#ffffff")

# ═════════════════════════════════════════════════════════════════════════════
# TITLE BAR
# ═════════════════════════════════════════════════════════════════════════════
box(ax, 0.3, 12.8, 21.4, 1.0, "#1a2a3a", "#00d2ff", radius=0.4, lw=2.5)
label(ax, 11.0, 13.37, "FinIQ – Financial Intelligence System", fs=17, bold=True, color="#00d2ff")
label(ax, 11.0, 13.02, "Self-Correcting Multi-Agent RAG Pipeline  ·  Hybrid Retrieval  ·  Teacher-Student Knowledge Distillation",
      fs=9, color="#bdc3c7")

# ═════════════════════════════════════════════════════════════════════════════
# LAYER 1 — DATA SOURCES
# ═════════════════════════════════════════════════════════════════════════════
box(ax, 0.3, 10.9, 21.4, 1.65, "#0e1d2e", C["data_bdr"], radius=0.35, lw=1.5)
section_header(ax, 0.3, 12.2, 4.0, 0.35, "DATA SOURCES", C["data_bg"], C["data_bdr"])

# Snowflake
box(ax, 0.6, 11.0, 5.5, 1.0, C["data_bg"], C["data_bdr"], radius=0.3)
label(ax, 3.35, 11.72, "[SF] Snowflake", fs=10, bold=True, color="#2980b9")
label(ax, 3.35, 11.40, "FINANCIAL_DB · RAW_DATA", fs=8, color=C["subtext"])
label(ax, 3.35, 11.13, "APPLE_FIN_US_2025  (500 rows OHLCV)", fs=7.5, color=C["subtext"])

# SEC EDGAR
box(ax, 6.8, 11.0, 4.5, 1.0, C["data_bg"], C["data_bdr"], radius=0.3)
label(ax, 9.05, 11.65, "[DOC] SEC EDGAR", fs=10, bold=True, color="#2980b9")
label(ax, 9.05, 11.33, "10-K / 10-Q Filings", fs=8, color=C["subtext"])
label(ax, 9.05, 11.08, "Annual & Quarterly Reports", fs=7.5, color=C["subtext"])

# Real-time KB
box(ax, 12.0, 11.0, 4.2, 1.0, C["data_bg"], C["data_bdr"], radius=0.3)
label(ax, 14.1, 11.65, "[RT] Real-Time KB", fs=10, bold=True, color="#2980b9")
label(ax, 14.1, 11.33, "Market / Earnings Data", fs=8, color=C["subtext"])
label(ax, 14.1, 11.08, "Earnings Calls · Analyst Notes", fs=7.5, color=C["subtext"])

# python-dotenv
box(ax, 17.0, 11.0, 4.4, 1.0, C["data_bg"], C["data_bdr"], radius=0.3)
label(ax, 19.2, 11.65, "[KEY] .env Config", fs=10, bold=True, color="#2980b9")
label(ax, 19.2, 11.33, "python-dotenv", fs=8, color=C["subtext"])
label(ax, 19.2, 11.08, "Credentials & System Config", fs=7.5, color=C["subtext"])

# ═════════════════════════════════════════════════════════════════════════════
# LAYER 2 — INGESTION PIPELINE
# ═════════════════════════════════════════════════════════════════════════════
box(ax, 0.3, 9.3, 21.4, 1.3, "#0e1d14", C["ingest_bdr"], radius=0.35, lw=1.5)
section_header(ax, 0.3, 10.25, 5.0, 0.35, "DATA INGESTION · src/ingestion.py", C["ingest_bg"], C["ingest_bdr"])

box(ax, 0.6, 9.45, 5.5, 0.7, C["ingest_bg"], C["ingest_bdr"], radius=0.25)
label(ax, 3.35, 9.82, "SnowflakeSource", fs=9.5, bold=True, color="#27ae60")
label(ax, 3.35, 9.57, "connect · fetch_documents · _row_to_text", fs=7.5, color=C["subtext"])

box(ax, 7.0, 9.45, 4.2, 0.7, C["ingest_bg"], C["ingest_bdr"], radius=0.25)
label(ax, 9.1, 9.82, "SECFilingSource", fs=9.5, bold=True, color="#27ae60")
label(ax, 9.1, 9.57, "EDGAR API · cache_dir", fs=7.5, color=C["subtext"])

box(ax, 12.0, 9.45, 5.2, 0.7, C["ingest_bg"], C["ingest_bdr"], radius=0.25)
label(ax, 14.6, 9.82, "DataIngestionPipeline", fs=9.5, bold=True, color="#27ae60")
label(ax, 14.6, 9.57, "register_source · ingest_all", fs=7.5, color=C["subtext"])

box(ax, 18.0, 9.45, 3.4, 0.7, C["ingest_bg"], C["ingest_bdr"], radius=0.25)
label(ax, 19.7, 9.82, "Document Store", fs=9.5, bold=True, color="#27ae60")
label(ax, 19.7, 9.57, "List[Document]", fs=7.5, color=C["subtext"])

# ═════════════════════════════════════════════════════════════════════════════
# LAYER 3 — HYBRID RETRIEVAL
# ═════════════════════════════════════════════════════════════════════════════
box(ax, 0.3, 7.6, 21.4, 1.4, "#1a1a0e", "#e67e22", radius=0.35, lw=1.5)
section_header(ax, 0.3, 8.65, 5.5, 0.35, "HYBRID RETRIEVAL · src/retrieval/hybrid_retriever.py", "#1a1a0e", "#e67e22")

box(ax, 0.6, 7.75, 6.0, 0.75, "#2a1e0a", "#e67e22", radius=0.25)
label(ax, 3.6, 8.18, "FAISS Vector Index", fs=9.5, bold=True, color="#e67e22")
label(ax, 3.6, 7.92, "SentenceTransformer  all-MiniLM-L6-v2  (dim=384)", fs=7.5, color=C["subtext"])

box(ax, 7.5, 7.75, 5.0, 0.75, "#2a1e0a", "#e67e22", radius=0.25)
label(ax, 10.0, 8.18, "BM25 Sparse Retriever", fs=9.5, bold=True, color="#e67e22")
label(ax, 10.0, 7.92, "Okapi BM25 · keyword scoring", fs=7.5, color=C["subtext"])

box(ax, 13.5, 7.75, 5.0, 0.75, "#2a1e0a", "#e67e22", radius=0.25)
label(ax, 16.0, 8.18, "HybridRetriever  (α=0.5, β=0.5)", fs=9.5, bold=True, color="#e67e22")
label(ax, 16.0, 7.92, "Score fusion · top-k=5 results", fs=7.5, color=C["subtext"])

box(ax, 19.4, 7.75, 2.0, 0.75, "#2a1e0a", "#e67e22", radius=0.25)
label(ax, 20.4, 8.18, "Re-rank", fs=9.5, bold=True, color="#e67e22")
label(ax, 20.4, 7.92, "Fusion score", fs=7.5, color=C["subtext"])

# ═════════════════════════════════════════════════════════════════════════════
# LAYER 4 — MULTI-AGENT ORCHESTRATOR
# ═════════════════════════════════════════════════════════════════════════════
box(ax, 0.3, 4.5, 21.4, 2.85, "#150d2a", C["agent_bdr"], radius=0.35, lw=1.5)
section_header(ax, 0.3, 7.0, 7.0, 0.35, "MULTI-AGENT ORCHESTRATOR · src/orchestration/langgraph_orchestrator.py", "#150d2a", C["agent_bdr"])

agents = [
    (0.6,  "[1] Retriever\nAgent",      "Query embedding\nFAISS lookup",         C["agent_bg"],  C["agent_bdr"]),
    (3.9,  "[2] Reader\nAgent",          "Context extraction\nTop-3 docs",         C["agent_bg"],  C["agent_bdr"]),
    (7.2,  "[3] Reasoning\nAgent",       "Student model\nExtractive QA",           C["reason_bg"], C["reason_bdr"]),
    (10.5, "[4] Evaluator\nAgent",       "TF-IDF cosine sim\nConfidence scoring",  C["eval_bg"],   C["eval_bdr"]),
    (13.8, "[5] Correction\nAgent",      "Teacher model\nMax 3 iterations",        C["reason_bg"], C["reason_bdr"]),
    (17.1, "[6] Verifier\nAgent",         "Cross-model check\nVerification score",  C["eval_bg"],   C["eval_bdr"]),
]

for i, (x, title, sub, bg, bdr) in enumerate(agents):
    box(ax, x, 4.65, 3.0, 2.2, bg, bdr, radius=0.28)
    lines = title.split("\n")
    label(ax, x+1.5, 6.42, lines[0], fs=9, bold=True, color=bdr)
    if len(lines) > 1:
        label(ax, x+1.5, 6.20, lines[1], fs=8.5, bold=True, color=bdr)
    sublines = sub.split("\n")
    label(ax, x+1.5, 5.85, sublines[0], fs=7.5, color=C["subtext"])
    if len(sublines) > 1:
        label(ax, x+1.5, 5.60, sublines[1], fs=7.5, color=C["subtext"])
    # Step number badge
    badge = plt.Circle((x+2.7, 6.6), 0.22, color=bdr, zorder=6)
    ax.add_patch(badge)
    label(ax, x+2.7, 6.61, str(i+1), fs=7.5, bold=True, color="white")
    # Arrow to next agent
    if i < len(agents) - 1:
        arrow(ax, x+3.0, 5.75, x+3.3, 5.75, color=C["agent_bdr"], lw=2.0)

# Self-correction loop arrow
ax.annotate("", xy=(13.8+0.8, 4.65), xytext=(10.5+0.8, 4.65),
            arrowprops=dict(arrowstyle="->", color="#e74c3c", lw=1.8,
                            connectionstyle="arc3,rad=-0.4"), zorder=4)
label(ax, 12.15, 4.2, "Self-Correction Loop (max 3 iterations)", fs=7.5,
      color="#e74c3c", bold=False)

# ═════════════════════════════════════════════════════════════════════════════
# LAYER 5 — TEACHER-STUDENT DISTILLATION
# ═════════════════════════════════════════════════════════════════════════════
box(ax, 0.3, 3.0, 10.0, 1.25, C["reason_bg"], C["reason_bdr"], radius=0.3, lw=1.5)
section_header(ax, 0.3, 3.9, 4.5, 0.35, "TEACHER-STUDENT DISTILLATION · src/reasoning/distillation.py",
               C["reason_bg"], C["reason_bdr"])

box(ax, 0.6, 3.1, 4.2, 0.65, "#4a1010", C["reason_bdr"], radius=0.22)
label(ax, 2.7, 3.52, "Teacher Model  glm-130b", fs=9, bold=True, color=C["reason_bdr"])
label(ax, 2.7, 3.25, "Deep reasoning · High accuracy", fs=7.5, color=C["subtext"])

box(ax, 5.5, 3.1, 4.2, 0.65, "#4a1010", C["reason_bdr"], radius=0.22)
label(ax, 7.6, 3.52, "Student Model  mistral-7b", fs=9, bold=True, color=C["reason_bdr"])
label(ax, 7.6, 3.25, "Fast inference · Distilled knowledge", fs=7.5, color=C["subtext"])

# Distillation arrow
arrow(ax, 4.8, 3.43, 5.5, 3.43, color=C["reason_bdr"], lw=1.8)
label(ax, 5.15, 3.65, "Knowledge\nDistillation T=4.0", fs=6.5, color=C["reason_bdr"])

# ── EVALUATOR METRICS ───────────────────────────────────────────────────────
box(ax, 11.3, 3.0, 10.4, 1.25, C["eval_bg"], C["eval_bdr"], radius=0.3, lw=1.5)
section_header(ax, 11.3, 3.9, 5.5, 0.35, "EVALUATION METRICS · src/evaluation/evaluator.py",
               C["eval_bg"], C["eval_bdr"])

metrics = [
    (11.6, "Relevance\n(TF-IDF cosine)"),
    (14.0, "Factual\nConsistency"),
    (16.3, "Numerical\nCoherence"),
    (18.6, "Entailment\n(cosine sim)"),
]
for x, m in metrics:
    box(ax, x, 3.1, 2.0, 0.65, "#0a2a1a", C["eval_bdr"], radius=0.2)
    lines = m.split("\n")
    label(ax, x+1.0, 3.55, lines[0], fs=8, bold=True, color=C["eval_bdr"])
    if len(lines) > 1:
        label(ax, x+1.0, 3.27, lines[1], fs=7, color=C["subtext"])

# ═════════════════════════════════════════════════════════════════════════════
# LAYER 6 — API + FRONTEND
# ═════════════════════════════════════════════════════════════════════════════
box(ax, 0.3, 0.7, 10.0, 2.0, C["api_bg"], C["api_bdr"], radius=0.35, lw=1.5)
section_header(ax, 0.3, 2.35, 4.0, 0.35, "FastAPI BACKEND · backend/api.py", C["api_bg"], C["api_bdr"])

box(ax, 0.6, 0.8, 4.2, 1.4, "#0d1a2a", C["api_bdr"], radius=0.25)
label(ax, 2.7, 1.85, "POST  /query", fs=9.5, bold=True, color=C["api_bdr"])
label(ax, 2.7, 1.58, "GET   /health", fs=9, color=C["subtext"])
label(ax, 2.7, 1.35, "GET   /statistics", fs=9, color=C["subtext"])
label(ax, 2.7, 1.07, "uvicorn  ·  port 8000  ·  --reload", fs=7.5, color=C["subtext"])

box(ax, 5.5, 0.8, 4.2, 1.4, "#0d1a2a", C["api_bdr"], radius=0.25)
label(ax, 7.6, 1.80, "CORS Middleware", fs=9.5, bold=True, color=C["api_bdr"])
label(ax, 7.6, 1.55, "Pydantic  QueryRequest", fs=8.5, color=C["subtext"])
label(ax, 7.6, 1.32, "QueryResponse  ·  EvaluationScores", fs=7.5, color=C["subtext"])
label(ax, 7.6, 1.07, "Background startup  ·  pipeline global", fs=7.5, color=C["subtext"])

box(ax, 11.3, 0.7, 10.4, 2.0, C["ui_bg"], C["ui_bdr"], radius=0.35, lw=1.5)
section_header(ax, 11.3, 2.35, 5.0, 0.35, "STREAMLIT FRONTEND · frontend/app.py", C["ui_bg"], C["ui_bdr"])

tabs = [
    (11.6, "[Q] Query\nAssistant",   "Prefill chips\nAnswer + confidence badge"),
    (14.2, "[A] User\nAnalytics",    "6 charts · CSV export\nConfidence trends"),
    (16.8, "[B] Batch\nProcessing",  "Multi-query · Progress\nBar chart + export"),
    (19.4, "[S] System\nStatistics", "KPI tiles · Gauges\nRadar chart"),
]
for x, t, s in tabs:
    box(ax, x, 0.8, 2.2, 1.4, "#0a1e14", C["ui_bdr"], radius=0.22)
    lines = t.split("\n")
    label(ax, x+1.1, 1.85, lines[0], fs=8.5, bold=True, color=C["ui_bdr"])
    if len(lines) > 1:
        label(ax, x+1.1, 1.62, lines[1], fs=8, bold=True, color=C["ui_bdr"])
    sublines = s.split("\n")
    label(ax, x+1.1, 1.35, sublines[0], fs=7, color=C["subtext"])
    if len(sublines) > 1:
        label(ax, x+1.1, 1.12, sublines[1], fs=7, color=C["subtext"])

# ═════════════════════════════════════════════════════════════════════════════
# INTER-LAYER ARROWS
# ═════════════════════════════════════════════════════════════════════════════
# Data Sources → Ingestion
arrow(ax, 11.0, 10.9, 11.0, 10.6, color=C["data_bdr"], lw=2.0)

# Ingestion → Retrieval
arrow(ax, 11.0, 9.3, 11.0, 9.0, color=C["ingest_bdr"], lw=2.0)

# Retrieval → Orchestrator
arrow(ax, 11.0, 7.6, 11.0, 7.35, color="#e67e22", lw=2.0)

# Orchestrator → Distillation / Evaluator
arrow(ax, 5.0, 4.5, 5.0, 4.25, color=C["agent_bdr"], lw=2.0)
arrow(ax, 16.0, 4.5, 16.0, 4.25, color=C["agent_bdr"], lw=2.0)

# Distillation + Eval → API
arrow(ax, 5.0, 3.0, 5.0, 2.7, color=C["reason_bdr"], lw=2.0)
arrow(ax, 16.0, 3.0, 16.0, 2.7, color=C["eval_bdr"], lw=2.0)

# API → Frontend
arrow(ax, 10.3, 1.7, 11.3, 1.7, color=C["api_bdr"], lw=2.5)
label(ax, 10.8, 1.95, "HTTP\nREST", fs=7, color=C["api_bdr"])

# ═════════════════════════════════════════════════════════════════════════════
# LEGEND
# ═════════════════════════════════════════════════════════════════════════════
legend_items = [
    (C["data_bdr"],    "Data Sources"),
    (C["ingest_bdr"],  "Ingestion"),
    ("#e67e22",        "Retrieval"),
    (C["agent_bdr"],   "Agents"),
    (C["reason_bdr"],  "Reasoning"),
    (C["eval_bdr"],    "Evaluation"),
    (C["api_bdr"],     "API"),
    (C["ui_bdr"],      "Frontend"),
]
for i, (color, lbl) in enumerate(legend_items):
    cx = 0.5 + i * 2.68
    sq = FancyBboxPatch((cx, 0.15), 0.28, 0.25,
                        boxstyle="round,pad=0,rounding_size=0.05",
                        facecolor=color, edgecolor=color, linewidth=0, zorder=5)
    ax.add_patch(sq)
    label(ax, cx + 0.55, 0.275, lbl, fs=7.5, color=C["subtext"], ha="left")

plt.tight_layout(pad=0)
out = "architecture_diagram.png"
plt.savefig(out, dpi=180, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print(f"Saved → {out}")
plt.close()
