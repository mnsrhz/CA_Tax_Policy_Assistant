from __future__ import annotations

from html import escape


def app_css() -> str:
    return """
<style>
.stApp {
    background: #F7F6F2;
    color: #1A1915;
}

.ct-header {
    padding: 1rem 0 0.5rem;
}

.ct-title {
    color: #1A1915;
    font-weight: 700;
}

.ct-subtitle {
    color: #5A554B;
}

.ct-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.ct-badge {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    line-height: 1;
    padding: 0.35rem 0.6rem;
}

.ct-badge-blue {
    background: #DCEBFF;
    color: #173E72;
}

.ct-badge-gold {
    background: #F3E2A2;
    color: #5B4300;
}

.ct-badge-green {
    background: #DCEFE2;
    color: #194D2D;
}

.ct-answer {
    color: #1A1915;
    line-height: 1.6;
}

.ct-disclaimer {
    color: #6A6258;
    font-size: 0.88rem;
}

.ct-source-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.ct-source-chip {
    display: inline-flex;
    align-items: center;
    border: 1px solid #D8D1C4;
    border-radius: 999px;
    color: #3D3932;
    font-size: 0.82rem;
    line-height: 1;
    padding: 0.35rem 0.6rem;
}

.ct-pipeline-trace {
    background: #F1EFE8;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 8px;
    margin-top: 0.6rem;
    padding: 0.6rem 0.7rem;
}

.ct-pipeline-title {
    color: #888780;
    font-family: system-ui, sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    margin-bottom: 0.4rem;
    text-transform: uppercase;
}

.ct-pipeline-steps {
    align-items: center;
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
}

.ct-pipeline-step {
    align-items: center;
    background: #EAF3DE;
    border-radius: 999px;
    color: #27500A;
    display: inline-flex;
    font-family: system-ui, sans-serif;
    font-size: 0.72rem;
    line-height: 1;
    padding: 0.25rem 0.55rem;
}

.ct-pipeline-arrow {
    color: #888780;
    font-size: 0.72rem;
}
</style>
""".strip()


def badge_html(text: str, color: str = "blue") -> str:
    safe_color = color if color in {"blue", "gold", "green"} else "blue"
    safe_text = escape(str(text), quote=True)
    return f'<span class="ct-badge ct-badge-{safe_color}">{safe_text}</span>'


def source_label(metadata: dict[str, object]) -> str:
    title = metadata.get("source_title", metadata.get("source_file", "Unknown source"))
    page = metadata.get("page_number", "?")
    return f"{title} · p.{page}"


def source_chip_html(metadata: dict[str, object]) -> str:
    label = escape(source_label(metadata), quote=True)
    return f'<span class="ct-source-chip">{label}</span>'


def retrieval_trace_summary(trace: list[dict[str, object]], source_count: int) -> str:
    return f"{len(trace)} retrieval stages · {source_count} source chunks"


def retrieval_trace_html(
    trace: list[dict[str, object]],
    tax_year: str,
    jurisdiction: str,
    source_count: int,
) -> str:
    stages = {str(item.get("stage", "")) for item in trace}
    step_labels = [
        f"Pre-filter {tax_year}",
        f"Filter {jurisdiction}",
        "Vector search",
    ]
    if "fallback" in stages:
        step_labels.append("Fallback widened")
    step_labels.append(f"Reranked top {source_count}")

    steps: list[str] = []
    for index, label in enumerate(step_labels):
        if index:
            steps.append('<span class="ct-pipeline-arrow">→</span>')
        steps.append(f'<span class="ct-pipeline-step">{escape(label, quote=True)}</span>')

    return (
        '<div class="ct-pipeline-trace">'
        '<div class="ct-pipeline-title">Retrieval trace</div>'
        f'<div class="ct-pipeline-steps">{"".join(steps)}</div>'
        "</div>"
    )
