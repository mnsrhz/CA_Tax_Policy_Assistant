from __future__ import annotations

from html import escape
import re


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

.ct-answer-card {
    background: #FFFFFF;
    border: 1px solid #D8D1C4;
    border-radius: 8px;
    border-top-left-radius: 3px;
    color: #1A1915;
    line-height: 1.62;
    margin-bottom: 0.7rem;
    padding: 0.85rem 0.95rem;
}

.ct-answer-header {
    align-items: center;
    color: #6A6258;
    display: flex;
    font-family: system-ui, sans-serif;
    font-size: 0.78rem;
    gap: 0.35rem;
    margin-bottom: 0.55rem;
}

.ct-answer-body {
    font-family: system-ui, sans-serif;
    font-size: 0.95rem;
}

.ct-answer-body p {
    margin: 0 0 0.65rem;
}

.ct-answer-body p:last-child {
    margin-bottom: 0;
}

.ct-answer-body ul {
    margin: 0.25rem 0 0.65rem 1.15rem;
    padding: 0;
}

.ct-answer-body li {
    margin-bottom: 0.35rem;
}

.ct-disclaimer {
    background: #FFF4D6;
    border-left: 2px solid #BA7517;
    border-radius: 5px;
    color: #6A4A12;
    font-size: 0.78rem;
    line-height: 1.5;
    margin-top: 0.7rem;
    padding: 0.5rem 0.65rem;
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


def _inline_markdown_html(text: str) -> str:
    safe_text = escape(text, quote=True)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe_text)


def format_answer_html(answer: str) -> str:
    blocks: list[str] = []
    bullet_items: list[str] = []

    def flush_bullets() -> None:
        if bullet_items:
            blocks.append(f"<ul>{''.join(bullet_items)}</ul>")
            bullet_items.clear()

    for raw_line in str(answer).splitlines():
        line = raw_line.strip()
        if not line:
            flush_bullets()
            continue
        if line.startswith(("- ", "* ")):
            bullet_items.append(f"<li>{_inline_markdown_html(line[2:].strip())}</li>")
            continue
        flush_bullets()
        blocks.append(f"<p>{_inline_markdown_html(line)}</p>")
    flush_bullets()
    return "".join(blocks)


def answer_card_html(answer: str, source_count: int, tax_year: str) -> str:
    source_word = "source document" if source_count == 1 else "source documents"
    safe_tax_year = escape(str(tax_year), quote=True)
    return (
        '<div class="ct-answer-card">'
        '<div class="ct-answer-header">Answer based on '
        f"{source_count} {source_word} · Tax year {safe_tax_year}</div>"
        f'<div class="ct-answer-body">{format_answer_html(answer)}</div>'
        '<div class="ct-disclaimer">For informational purposes only. '
        "Not a substitute for advice from a licensed tax professional.</div>"
        "</div>"
    )


def retrieval_trace_summary(trace: list[dict[str, object]], source_count: int) -> str:
    return f"{len(trace)} retrieval stages · {source_count} source chunks"


def retrieval_trace_html(
    trace: list[dict[str, object]],
    tax_year: str,
    jurisdiction: str,
    source_count: int,
) -> str:
    stages = {str(item.get("stage", "")) for item in trace}
    final_stage = trace[-1] if trace else {}
    step_labels = [
        f"Pre-filter {tax_year}",
        f"Filter {jurisdiction}",
        f"Vector · {int(final_stage.get('vector_hits', 0))} hits",
        f"BM25 · {int(final_stage.get('bm25_hits', 0))} hits",
    ]
    if "fallback" in stages:
        step_labels.append("Fallback widened")
    step_labels.append(f"Merged · {int(final_stage.get('merged_candidates', 0))} candidates")
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
