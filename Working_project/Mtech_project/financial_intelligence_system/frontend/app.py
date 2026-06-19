# Streamlit Frontend for Financial Intelligence System
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import time
import json
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FinIQ – Financial Intelligence",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }

.hero {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    border-radius: 16px;
    padding: 2.2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: white;
}
.hero h1 { font-size: 2.2rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
.hero p  { font-size: 1rem; margin: 0.4rem 0 0; opacity: 0.80; }

.answer-card {
    background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
    border-left: 5px solid #27ae60;
    border-radius: 12px;
    padding: 1.5rem 1.8rem;
    font-size: 1.05rem;
    line-height: 1.7;
    color: #1a1a2e;
    margin-bottom: 1rem;
}

.kpi-tile {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    color: white;
    box-shadow: 0 4px 14px rgba(0,0,0,0.18);
}
.kpi-tile .kpi-value { font-size: 2.1rem; font-weight: 800; color: #00d2ff; }
.kpi-tile .kpi-label { font-size: 0.82rem; opacity: 0.75; text-transform: uppercase; letter-spacing: 1px; }

.badge { display: inline-block; padding: 0.35rem 1rem; border-radius: 50px; font-weight: 700; font-size: 0.9rem; }
.badge-high   { background: #d4edda; color: #155724; }
.badge-medium { background: #fff3cd; color: #856404; }
.badge-low    { background: #f8d7da; color: #721c24; }

.chip {
    display: inline-block;
    background: #eaf0fb;
    color: #2c5364;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.82rem;
    margin: 0.2rem;
    font-weight: 600;
}

section[data-testid="stSidebar"] { background: #0f2027 !important; }
section[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #00d2ff !important; }

.doc-card {
    background: #f8f9fa;
    border-left: 4px solid #2980b9;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
    font-size: 0.92rem;
}
.doc-score {
    float: right;
    background: #2980b9;
    color: white;
    padding: 0.15rem 0.55rem;
    border-radius: 12px;
    font-size: 0.78rem;
    font-weight: 700;
}

.pipe-step {
    background: #f0f4ff;
    border-left: 3px solid #8e44ad;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    margin-bottom: 0.4rem;
    font-size: 0.88rem;
    color: #2c3e50;
}

.hist-row {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
    border-left: 4px solid #2c5364;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS & HELPERS
# ─────────────────────────────────────────────
API_BASE_URL = "http://localhost:8000"

EXAMPLE_QUERIES = [
    "What is Apple's revenue growth in 2023?",
    "Analyze Microsoft's cloud revenue trends",
    "Debt-to-equity ratio for Tesla 2023",
    "Compare Amazon AWS vs Azure growth",
    "Google's main advertising revenue sources",
]

TOPIC_KEYWORDS = {
    "Revenue":  ["revenue", "sales", "income", "growth"],
    "Risk":     ["risk", "factor", "threat", "challenge"],
    "Debt":     ["debt", "equity", "leverage", "liability"],
    "Cloud":    ["cloud", "aws", "azure", "saas"],
    "Earnings": ["earnings", "profit", "margin", "ebitda"],
}


@st.cache_resource
def get_api_client():
    return requests.Session()


def query_api(query_text: str, use_teacher: bool = False) -> Dict:
    client = get_api_client()
    try:
        response = client.post(
            f"{API_BASE_URL}/query",
            json={"query": query_text, "use_teacher_model": use_teacher, "temperature": 0.7},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot connect to backend at {API_BASE_URL}. Please start the API server first.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"API Error: {e.response.status_code}")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def detect_topic(query: str) -> str:
    q = query.lower()
    for topic, kws in TOPIC_KEYWORDS.items():
        if any(k in q for k in kws):
            return topic
    return "General"


def confidence_badge_html(conf: float) -> str:
    pct = int(conf * 100)
    cls = "badge-high" if conf >= 0.8 else ("badge-medium" if conf >= 0.6 else "badge-low")
    icon = "✅" if conf >= 0.8 else ("⚠️" if conf >= 0.6 else "❌")
    return f'<span class="badge {cls}">{icon} {pct}% Confidence</span>'


def gauge_chart(title: str, value: float, color: str = "#2980b9") -> go.Figure:
    pct = round(value * 100, 1)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        number={"suffix": "%", "font": {"size": 22, "color": "#2c3e50"}},
        title={"text": title, "font": {"size": 13, "color": "#555"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#ccc"},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "white",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50],  "color": "#fdecea"},
                {"range": [50, 75], "color": "#fff8e1"},
                {"range": [75, 100],"color": "#e8f5e9"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": pct},
        },
    ))
    fig.update_layout(height=190, margin=dict(l=15, r=15, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)")
    return fig


# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "total_time_ms" not in st.session_state:
    st.session_state.total_time_ms = 0.0

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💹 FinIQ")
    st.markdown("<small style='opacity:.6'>Financial Intelligence System</small>", unsafe_allow_html=True)
    st.markdown("---")

    mode = st.radio(
        "Navigation",
        ["🔍 Query Assistant", "📊 User Analytics", "📦 Batch Processing", "⚙️ System Statistics"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Model Settings**")
    use_teacher_model = st.toggle(
        "Use Teacher Model", value=False,
        help="Larger model — better accuracy, slower response"
    )
    st.markdown("---")

    st.markdown("**Backend Status**")
    try:
        hresp = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if hresp.status_code == 200:
            st.markdown('<span style="color:#00e676;font-weight:700">● Online</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span style="color:#ff5252;font-weight:700">● Error</span>', unsafe_allow_html=True)
    except Exception:
        st.markdown('<span style="color:#ff5252;font-weight:700">● Offline</span>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑️ Clear Session", use_container_width=True):
        st.session_state.query_history = []
        st.session_state.total_queries = 0
        st.session_state.total_time_ms = 0.0
        st.rerun()

# ─────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>💹 FinIQ – Financial Intelligence System</h1>
  <p>Self-Correcting Multi-Agent RAG Pipeline · Hybrid Retrieval · Teacher-Student Reasoning</p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# MODE: QUERY ASSISTANT
# ══════════════════════════════════════════════
if mode == "🔍 Query Assistant":

    st.markdown("**Quick Examples — click to prefill:**")
    chip_cols = st.columns(len(EXAMPLE_QUERIES))
    for i, ex in enumerate(EXAMPLE_QUERIES):
        with chip_cols[i]:
            if st.button(ex[:28] + "…", key=f"ex_{i}", use_container_width=True):
                st.session_state["query_input"] = ex

    query_text = st.text_area(
        "Ask a financial question:",
        placeholder="e.g. What is Apple's year-over-year revenue growth in 2023?",
        height=90,
        key="query_input",
    )

    col_btn, _ = st.columns([1, 5])
    with col_btn:
        submit = st.button("🔍 Analyse", type="primary", use_container_width=True)

    if submit and query_text.strip():
        with st.spinner("⚙️ Running multi-agent pipeline…"):
            t0 = time.time()
            result = query_api(query_text.strip(), use_teacher_model)
            elapsed_ms = (time.time() - t0) * 1000

        if result:
            result.setdefault("query",               query_text.strip())
            result.setdefault("processing_time_ms",  elapsed_ms)
            result.setdefault("timestamp",           datetime.now().strftime("%H:%M:%S"))
            result.setdefault("topic",               detect_topic(query_text))
            st.session_state.query_history.append(result)
            st.session_state.total_queries += 1
            st.session_state.total_time_ms += result["processing_time_ms"]

            conf = result.get("confidence", 0)

            st.markdown("<br>", unsafe_allow_html=True)
            # Answer
            st.markdown(f'<div class="answer-card">{result.get("answer","No answer returned.")}</div>',
                        unsafe_allow_html=True)

            # Inline chips
            st.markdown(
                confidence_badge_html(conf) +
                f'&nbsp;&nbsp;<span class="chip">🏷 {result["topic"]}</span>'
                f'&nbsp;<span class="chip">⏱ {result["processing_time_ms"]:.0f} ms</span>'
                f'&nbsp;<span class="chip">🔁 {result.get("iterations",0)} iterations</span>',
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)

            # KPI tiles
            k1, k2, k3, k4 = st.columns(4)
            tiles = [
                (k1, f"{int(conf*100)}%",                      "Overall Confidence"),
                (k2, f"{result.get('processing_time_ms',0):.0f}ms", "Response Time"),
                (k3, str(result.get("iterations", 0)),          "Refinement Loops"),
                (k4, result["topic"],                           "Query Topic"),
            ]
            for col, val, lbl in tiles:
                with col:
                    st.markdown(f"""
                    <div class="kpi-tile">
                      <div class="kpi-value">{val}</div>
                      <div class="kpi-label">{lbl}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Evaluation gauges
            scores = result.get("evaluation_scores", {})
            if scores:
                st.markdown("#### 📊 Evaluation Metrics")
                gc1, gc2, gc3, gc4 = st.columns(4)
                metric_cfg = [
                    ("Relevance",           scores.get("relevance", 0),           "#2980b9"),
                    ("Factual Consistency", scores.get("factual_consistency", 0), "#27ae60"),
                    ("Numerical Coherence", scores.get("numerical_coherence", 0), "#8e44ad"),
                    ("Entailment",          scores.get("entailment", 0),          "#e67e22"),
                ]
                for col, (name, val, clr) in zip([gc1, gc2, gc3, gc4], metric_cfg):
                    with col:
                        st.plotly_chart(gauge_chart(name, val, clr), use_container_width=True)

                # Radar chart
                st.markdown("#### 🕸 Quality Radar")
                categories = ["Relevance", "Factual", "Numerical", "Entailment", "Overall"]
                vals = [
                    scores.get("relevance", 0),
                    scores.get("factual_consistency", 0),
                    scores.get("numerical_coherence", 0),
                    scores.get("entailment", 0),
                    scores.get("overall_confidence", conf),
                ]
                fig_radar = go.Figure(go.Scatterpolar(
                    r=[v * 100 for v in vals] + [vals[0] * 100],
                    theta=categories + [categories[0]],
                    fill="toself",
                    fillcolor="rgba(41,128,185,0.2)",
                    line=dict(color="#2980b9", width=2),
                    marker=dict(size=7, color="#2980b9"),
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False, height=320,
                    margin=dict(l=40, r=40, t=30, b=30),
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_radar, use_container_width=True)

            # Supporting docs
            docs = result.get("supporting_documents", [])
            if docs:
                st.markdown("#### 📄 Supporting Documents")
                for i, doc in enumerate(docs):
                    score_pct = f"{doc.get('score', 0):.0%}"
                    st.markdown(
                        f'<div class="doc-card">'
                        f'<span class="doc-score">{score_pct}</span>'
                        f'<strong>Doc {i+1} · {doc.get("source","Unknown")}</strong><br>'
                        f'<span style="color:#555">{doc.get("content","")[:220]}…</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            # Elaborated output: expanded evidence, reasoning metadata and raw response
            with st.expander("🧾 Elaborated Output (evidence, reasoning, raw)", expanded=False):
                # Full supporting documents
                if docs:
                    st.markdown("**Full Supporting Documents**")
                    for i, doc in enumerate(docs):
                        st.markdown(f"**Doc {i+1} — {doc.get('source','Unknown')}**")
                        st.code(doc.get("content", ""), language="text")
                        st.markdown(f"- Score: **{doc.get('score',0):.3f}**")

                # Reasoning metadata if present
                if result.get("reasoning_path") or result.get("model_used") or result.get("correction_actions"):
                    st.markdown("**Reasoning / Correction Metadata**")
                    if result.get("reasoning_path"):
                        st.markdown(f"- Reasoning path: `{result.get('reasoning_path')}`")
                    if result.get("model_used"):
                        st.markdown(f"- Model used: **{result.get('model_used')}**")
                    if result.get("correction_actions"):
                        st.markdown("- Correction actions:")
                        for act in result.get("correction_actions", []):
                            st.markdown(f"  - {act}")

                # Evaluation raw breakdown
                st.markdown("**Evaluation Scores (raw)**")
                st.json(result.get("evaluation_scores", {}))

                # Download / raw view
                raw_json = json.dumps(result, indent=2, ensure_ascii=False)
                st.download_button("⬇️ Download raw response JSON", data=raw_json, file_name="finiq_response.json", mime="application/json")
                st.markdown("**Raw response**")
                st.code(raw_json, language="json")

            # Business-facing summary and guidance
            with st.expander("🧭 Business Summary & Guidance", expanded=True):
                try:
                    conf_pct = int(conf * 100)
                except Exception:
                    conf_pct = 0

                st.markdown("**One-line result:**")
                one_line = result.get("answer", "No answer returned.")
                # keep it short for business users
                st.markdown(f"{one_line[:400]}" + ("…" if len(one_line) > 400 else ""))

                # Confidence and quick interpretation
                st.markdown("**Confidence & actionability**")
                st.markdown(confidence_badge_html(conf), unsafe_allow_html=True)

                # Simple recommended action based on confidence bands
                if conf >= 0.8:
                    st.markdown("**Recommended action:** Actionable — can be used to inform decisions with standard verification.")
                elif conf >= 0.6:
                    st.markdown("**Recommended action:** Use with caution — verify key figures against primary sources before high-impact actions.")
                else:
                    st.markdown("**Recommended action:** Not ready for action — requires manual verification and analyst review.")

                # Short rationale + key supporting sources
                st.markdown("**Why this matters (short):**")
                st.markdown("- The system combines retrieval, reasoning and evaluator checks. Confidence reflects agreement across those components.")

                st.markdown("**Top supporting sources (quick view):**")
                if docs:
                    for i, d in enumerate(docs[:3]):
                        st.markdown(f"- {d.get('source','Unknown')} — score: {d.get('score',0):.2f}")
                else:
                    st.markdown("- No supporting documents identified — verify against official filings.")

                st.markdown("**Suggested next steps for business teams:**")
                st.markdown("1. Verify numerical figures (revenue, EPS, net income) against official filings (10-K/10-Q).")
                st.markdown("2. If decision is high-impact, request analyst review and attach primary-source excerpts.")
                st.markdown("3. Ask follow-up clarifying questions using the assistant to narrow scope.")

                st.markdown("**Note:** Confidence is a model-driven estimate — always confirm material figures with primary sources before acting.")

    # Recent query history
    if st.session_state.query_history:
        st.markdown("---")
        st.markdown("#### 📜 Recent Queries")
        for h in reversed(st.session_state.query_history[-5:]):
            conf_val = h.get("confidence", 0)
            conf_cls = "badge-high" if conf_val >= 0.8 else ("badge-medium" if conf_val >= 0.6 else "badge-low")
            st.markdown(
                f'<div class="hist-row">'
                f'<strong>{h.get("timestamp","")}</strong> &nbsp; '
                f'<span class="chip">🏷 {h.get("topic","General")}</span> &nbsp; '
                f'<span class="badge {conf_cls}" style="font-size:.78rem;padding:.2rem .7rem">'
                f'{int(conf_val*100)}%</span><br>'
                f'<span style="color:#333">{h.get("query","")[:120]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════
# MODE: USER ANALYTICS
# ══════════════════════════════════════════════
elif mode == "📊 User Analytics":
    st.markdown("## 📊 User Session Analytics")

    history = st.session_state.query_history

    if not history:
        st.info("No queries yet. Run some queries in the **Query Assistant** tab first.")
    else:
        n = len(history)
        confs  = [h.get("confidence", 0) for h in history]
        times  = [h.get("processing_time_ms", 0) for h in history]
        iters  = [h.get("iterations", 0) for h in history]
        avg_conf = sum(confs) / n
        avg_time = sum(times) / n

        # ── Session KPIs ──
        st.markdown("### Session Summary")
        kc1, kc2, kc3, kc4 = st.columns(4)
        kpis = [
            (kc1, str(n),              "Queries Analysed"),
            (kc2, f"{avg_conf:.0%}",   "Avg Confidence"),
            (kc3, f"{avg_time:.0f}ms", "Avg Response Time"),
            (kc4, str(sum(iters)),     "Total Refinements"),
        ]
        for col, val, lbl in kpis:
            with col:
                st.markdown(f"""
                <div class="kpi-tile">
                  <div class="kpi-value">{val}</div>
                  <div class="kpi-label">{lbl}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        df = pd.DataFrame({
            "Query #":    list(range(1, n + 1)),
            "Confidence": [c * 100 for c in confs],
            "Time (ms)":  times,
            "Iterations": iters,
            "Topic":      [h.get("topic", "General") for h in history],
            "Query":      [h.get("query", "")[:50] + "…" for h in history],
            "Timestamp":  [h.get("timestamp", "") for h in history],
        })

        # ── Confidence Trend with threshold lines ──
        st.markdown("### 📈 Confidence Over Time")
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df["Query #"], y=df["Confidence"],
            mode="lines+markers+text",
            text=[f"{v:.0f}%" for v in df["Confidence"]],
            textposition="top center",
            marker=dict(size=10, color=df["Confidence"],
                        colorscale="RdYlGn", showscale=True,
                        colorbar=dict(title="Conf %", thickness=12)),
            line=dict(color="#2980b9", width=2.5),
            hovertemplate="<b>Q%{x}</b>: %{customdata}<br>Confidence: %{y:.1f}%<extra></extra>",
            customdata=df["Query"],
        ))
        fig_trend.add_hline(y=80, line_dash="dot", line_color="#27ae60",
                            annotation_text="High (80%)", annotation_position="bottom right")
        fig_trend.add_hline(y=60, line_dash="dot", line_color="#f39c12",
                            annotation_text="Medium (60%)")
        fig_trend.update_layout(
            xaxis_title="Query Number", yaxis_title="Confidence (%)",
            yaxis=dict(range=[0, 110]),
            height=350, margin=dict(l=40, r=20, t=30, b=40),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f9f9f9",
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # ── Time + Iterations ──
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("### ⏱ Response Time per Query")
            fig_time = px.bar(
                df, x="Query #", y="Time (ms)",
                color="Time (ms)", color_continuous_scale="Blues",
                hover_data={"Query": True, "Time (ms)": ":.0f"},
            )
            fig_time.update_layout(
                height=280, showlegend=False,
                margin=dict(l=30, r=10, t=20, b=30),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f9f9f9",
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_time, use_container_width=True)

        with rc2:
            st.markdown("### 🔁 Refinement Iterations")
            fig_iter = px.bar(
                df, x="Query #", y="Iterations",
                color="Iterations", color_continuous_scale="Purples",
            )
            fig_iter.update_layout(
                height=280, showlegend=False,
                margin=dict(l=30, r=10, t=20, b=30),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f9f9f9",
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_iter, use_container_width=True)

        # ── Topic distribution ──
        st.markdown("### 🏷 Query Topic Distribution")
        topic_counts = df["Topic"].value_counts().reset_index()
        topic_counts.columns = ["Topic", "Count"]
        fig_pie = px.pie(
            topic_counts, values="Count", names="Topic",
            color_discrete_sequence=px.colors.qualitative.Bold,
            hole=0.4,
        )
        fig_pie.update_traces(textinfo="percent+label", textfont_size=13)
        fig_pie.update_layout(
            height=320, margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # ── Confidence distribution histogram ──
        st.markdown("### 📉 Confidence Distribution")
        fig_hist = px.histogram(
            df, x="Confidence", nbins=10,
            color_discrete_sequence=["#2980b9"],
            labels={"Confidence": "Confidence (%)"},
        )
        fig_hist.add_vline(x=80, line_dash="dash", line_color="#27ae60",
                           annotation_text="High ≥80%")
        fig_hist.add_vline(x=60, line_dash="dash", line_color="#f39c12",
                           annotation_text="Medium ≥60%")
        fig_hist.update_layout(
            height=260, margin=dict(l=30, r=20, t=20, b=30),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f9f9f9",
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        # ── Scatter — confidence vs time ──
        st.markdown("### ⚡ Confidence vs Response Time")
        fig_scatter = px.scatter(
            df, x="Time (ms)", y="Confidence",
            color="Topic", size="Iterations",
            hover_data=["Query", "Timestamp"],
            color_discrete_sequence=px.colors.qualitative.Safe,
            labels={"Time (ms)": "Response Time (ms)", "Confidence": "Confidence (%)"},
        )
        fig_scatter.update_layout(
            height=300, margin=dict(l=30, r=20, t=20, b=30),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f9f9f9",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # ── Full query log ──
        st.markdown("### 📋 Full Query Log")
        log_df = pd.DataFrame([{
            "#":          i + 1,
            "Time":       h.get("timestamp", ""),
            "Query":      h.get("query", "")[:70] + "…",
            "Topic":      h.get("topic", "General"),
            "Confidence": f"{h.get('confidence',0):.0%}",
            "Resp (ms)":  f"{h.get('processing_time_ms',0):.0f}",
            "Iterations": h.get("iterations", 0),
        } for i, h in enumerate(history)])
        st.dataframe(log_df, use_container_width=True, hide_index=True)

        csv = log_df.to_csv(index=False)
        st.download_button("⬇️ Export Session CSV", data=csv,
                           file_name="finiq_session_log.csv", mime="text/csv")


# ══════════════════════════════════════════════
# MODE: BATCH PROCESSING
# ══════════════════════════════════════════════
elif mode == "📦 Batch Processing":
    st.markdown("## 📦 Batch Query Processing")
    st.markdown("Enter multiple financial questions (one per line) to analyse them in bulk.")

    queries_text = st.text_area(
        "Queries (one per line):",
        placeholder="What is Apple's revenue growth?\nAnalyze Tesla production trends\nMicrosoft cloud revenue 2023",
        height=180,
    )

    if st.button("▶️ Run Batch", type="primary"):
        queries = [q.strip() for q in queries_text.splitlines() if q.strip()]

        if not queries:
            st.warning("Please enter at least one query.")
        else:
            progress = st.progress(0, text="Processing…")
            status_box = st.empty()
            all_results = []

            for idx, q in enumerate(queries):
                status_box.markdown(f"**Running [{idx+1}/{len(queries)}]:** {q[:70]}")
                r = query_api(q, use_teacher_model)
                if r:
                    r.setdefault("query",     q)
                    r.setdefault("topic",     detect_topic(q))
                    r.setdefault("timestamp", datetime.now().strftime("%H:%M:%S"))
                    all_results.append(r)
                    st.session_state.query_history.append(r)
                    st.session_state.total_queries += 1
                    st.session_state.total_time_ms += r.get("processing_time_ms", 0)
                progress.progress((idx + 1) / len(queries), text=f"{idx+1}/{len(queries)} done")

            status_box.success(f"✅ Completed {len(all_results)}/{len(queries)} queries")

            if all_results:
                df_batch = pd.DataFrame([{
                    "Query":      r["query"][:55] + "…",
                    "Topic":      r.get("topic", ""),
                    "Confidence": f"{r.get('confidence',0):.0%}",
                    "Time (ms)":  f"{r.get('processing_time_ms',0):.0f}",
                    "Iterations": r.get("iterations", 0),
                    "Answer":     r.get("answer", "")[:80] + "…",
                } for r in all_results])
                st.dataframe(df_batch, use_container_width=True, hide_index=True)

                fig_b = px.bar(
                    x=[r["query"][:30] + "…" for r in all_results],
                    y=[r.get("confidence", 0) * 100 for r in all_results],
                    color=[r.get("confidence", 0) * 100 for r in all_results],
                    color_continuous_scale="RdYlGn",
                    labels={"x": "Query", "y": "Confidence (%)"},
                    title="Batch Confidence Results",
                )
                fig_b.update_layout(
                    height=300, xaxis_tickangle=-30,
                    margin=dict(l=30, r=20, t=40, b=80),
                    paper_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=False,
                )
                st.plotly_chart(fig_b, use_container_width=True)

                csv_b = df_batch.to_csv(index=False)
                st.download_button("⬇️ Export Batch CSV", data=csv_b,
                                   file_name="finiq_batch_results.csv", mime="text/csv")


# ══════════════════════════════════════════════
# MODE: SYSTEM STATISTICS
# ══════════════════════════════════════════════
elif mode == "⚙️ System Statistics":
    st.markdown("## ⚙️ System Statistics")

    if st.button("🔄 Refresh from API", type="primary"):
        try:
            stats_resp = requests.get(f"{API_BASE_URL}/statistics", timeout=5)
            if stats_resp.status_code == 200:
                stats = stats_resp.json()
                ws = stats.get("workflow_stats", {})
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Total Queries Processed", stats.get("total_queries", 0))
                with c2:
                    st.metric("Avg Confidence", f"{ws.get('avg_overall_confidence', 0):.1%}")
                with c3:
                    st.metric("Self-Corrections", ws.get("total_corrections", "N/A"))
                st.markdown("**Raw Workflow Stats:**")
                st.json(ws)
            else:
                st.error(f"Backend returned {stats_resp.status_code}")
        except Exception as e:
            st.error(f"Cannot reach statistics endpoint: {e}")

    st.markdown("---")
    st.markdown("### 📌 This Session")
    cs1, cs2 = st.columns(2)
    with cs1:
        st.metric("Queries This Session", st.session_state.total_queries)
    with cs2:
        avg = (st.session_state.total_time_ms / st.session_state.total_queries
               if st.session_state.total_queries else 0)
        st.metric("Avg Response Time", f"{avg:.0f} ms")

    st.markdown("---")
    st.markdown("### 🔧 Pipeline Components")
    pipeline_steps = [
        ("🔁 Retriever Agent",  "Hybrid FAISS + BM25 semantic & keyword search"),
        ("📖 Reader Agent",     "Extracts and ranks top-k evidence passages"),
        ("🧠 Reasoning Agent",  "Teacher-Student distillation pipeline"),
        ("🔎 Evaluator Agent",  "Scores relevance, factual consistency, entailment"),
        ("✏️ Correction Agent", "Self-corrects low-confidence responses iteratively"),
        ("✅ Verifier Agent",   "Cross-model verification for the final answer"),
    ]
    for step, desc in pipeline_steps:
        st.markdown(
            f'<div class="pipe-step"><strong>{step}</strong> — {desc}</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown(
    "<hr style='margin-top:2.5rem'>"
    "<p style='text-align:center;font-size:.82rem;color:#999'>"
    "FinIQ · Self-Correcting Financial Intelligence System · "
    "M.Tech Dissertation · Karthik V · May 2026"
    "</p>",
    unsafe_allow_html=True,
)
# Streamlit Frontend for Financial Intelligence System
