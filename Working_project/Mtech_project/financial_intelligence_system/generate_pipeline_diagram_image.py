"""Generate an end-to-end pipeline diagram image for FinIQ."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def add_box(ax, x, y, w, h, text, fc, ec, fs=9):
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.5,
        facecolor=fc,
        edgecolor=ec,
        zorder=2,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color="#111827")


def add_arrow(ax, x1, y1, x2, y2, color="#374151", lw=1.6):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color=color, lw=lw),
        zorder=3,
    )


def main():
    fig, ax = plt.subplots(figsize=(17, 10), dpi=160)
    ax.set_xlim(0, 17)
    ax.set_ylim(0, 10)
    ax.axis("off")
    fig.patch.set_facecolor("#f9fafb")

    ax.text(
        8.5,
        9.6,
        "FinIQ End-to-End Pipeline",
        ha="center",
        va="center",
        fontsize=20,
        fontweight="bold",
        color="#0f172a",
    )

    # Initialization lane
    ax.text(1.1, 8.8, "Initialization", fontsize=11, fontweight="bold", color="#166534")
    add_box(ax, 0.6, 8.0, 2.7, 0.55, "Load .env +\nconfig", "#dcfce7", "#16a34a", 8.5)
    add_box(ax, 3.7, 8.0, 3.2, 0.55, "Data Ingestion\nSnowflake + SEC", "#dcfce7", "#16a34a", 8.5)
    add_box(ax, 7.3, 8.0, 3.0, 0.55, "Embeddings\nall-MiniLM-L6-v2", "#dcfce7", "#16a34a", 8.5)
    add_box(ax, 10.7, 8.0, 2.8, 0.55, "Hybrid Retriever\nFAISS + BM25", "#dcfce7", "#16a34a", 8.5)
    add_box(ax, 13.9, 8.0, 2.6, 0.55, "Pipeline Ready", "#dcfce7", "#16a34a", 8.5)

    add_arrow(ax, 3.3, 8.28, 3.7, 8.28)
    add_arrow(ax, 6.9, 8.28, 7.3, 8.28)
    add_arrow(ax, 10.3, 8.28, 10.7, 8.28)
    add_arrow(ax, 13.5, 8.28, 13.9, 8.28)

    # Runtime lane
    ax.text(1.1, 7.0, "Runtime Query Path", fontsize=11, fontweight="bold", color="#1d4ed8")
    add_box(ax, 0.6, 6.2, 2.7, 0.7, "User Query\n(Streamlit/API)", "#dbeafe", "#2563eb", 8.8)
    add_box(ax, 3.8, 6.2, 2.6, 0.7, "FastAPI\n/query", "#dbeafe", "#2563eb", 8.8)
    add_box(ax, 6.9, 6.2, 3.1, 0.7, "orchestrator\n.execute_workflow", "#dbeafe", "#2563eb", 8.8)

    add_arrow(ax, 3.3, 6.55, 3.8, 6.55)
    add_arrow(ax, 6.4, 6.55, 6.9, 6.55)

    # Orchestration lane
    ax.text(1.1, 5.2, "Multi-Agent Orchestration", fontsize=11, fontweight="bold", color="#7c3aed")
    add_box(ax, 0.6, 4.4, 2.0, 0.7, "1) Retriever", "#ede9fe", "#7c3aed")
    add_box(ax, 2.9, 4.4, 2.0, 0.7, "2) Reader", "#ede9fe", "#7c3aed")
    add_box(ax, 5.2, 4.4, 2.0, 0.7, "3) Reasoning\n(Student)", "#ede9fe", "#7c3aed")
    add_box(ax, 7.5, 4.4, 2.3, 0.7, "4) Evaluator", "#ede9fe", "#7c3aed")
    add_box(ax, 10.2, 4.4, 2.4, 0.7, "Confidence\n>= Threshold?", "#ffedd5", "#ea580c", 8.4)
    add_box(ax, 13.0, 4.4, 2.4, 0.7, "Verifier", "#ede9fe", "#7c3aed")

    add_arrow(ax, 2.6, 4.75, 2.9, 4.75)
    add_arrow(ax, 4.9, 4.75, 5.2, 4.75)
    add_arrow(ax, 7.2, 4.75, 7.5, 4.75)
    add_arrow(ax, 9.8, 4.75, 10.2, 4.75)
    add_arrow(ax, 12.6, 4.75, 13.0, 4.75)

    # Correction loop
    add_box(ax, 7.7, 2.9, 2.8, 0.7, "Correction Agent\n(Teacher-assisted)", "#fee2e2", "#dc2626", 8.4)
    add_box(ax, 11.0, 2.9, 2.5, 0.7, "Re-evaluate", "#fee2e2", "#dc2626", 8.4)
    add_arrow(ax, 11.4, 4.4, 9.1, 3.65, color="#dc2626")
    add_arrow(ax, 10.5, 3.25, 11.0, 3.25, color="#dc2626")
    add_arrow(ax, 13.5, 3.25, 10.0, 4.4, color="#dc2626")
    ax.text(12.2, 3.95, "if No and iterations < max", fontsize=8, color="#b91c1c")

    # Output lane
    ax.text(1.1, 1.8, "Delivery", fontsize=11, fontweight="bold", color="#0f766e")
    add_box(ax, 0.6, 0.9, 3.5, 0.7, "Final Answer + Confidence + Evidence", "#ccfbf1", "#0f766e", 8.6)
    add_box(ax, 4.6, 0.9, 3.3, 0.7, "FastAPI JSON Response", "#ccfbf1", "#0f766e", 8.6)
    add_box(ax, 8.3, 0.9, 3.7, 0.7, "Streamlit UI / API Consumer", "#ccfbf1", "#0f766e", 8.6)
    add_box(ax, 12.4, 0.9, 3.8, 0.7, "Logs + Statistics Endpoints", "#ccfbf1", "#0f766e", 8.6)

    add_arrow(ax, 14.2, 4.4, 2.3, 1.6)
    add_arrow(ax, 4.1, 1.25, 4.6, 1.25)
    add_arrow(ax, 7.9, 1.25, 8.3, 1.25)
    add_arrow(ax, 12.0, 1.25, 12.4, 1.25)

    output_path = "end_to_end_pipeline_diagram.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=220, bbox_inches="tight")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
