from __future__ import annotations


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
</style>
""".strip()


def badge_html(text: str, color: str = "blue") -> str:
    return f'<span class="ct-badge ct-badge-{color}">{text}</span>'


def source_label(metadata: dict[str, object]) -> str:
    title = metadata.get("source_title", metadata.get("source_file", "Unknown source"))
    page = metadata.get("page_number", "?")
    return f"{title} · p.{page}"


def source_chip_html(metadata: dict[str, object]) -> str:
    return f'<span class="ct-source-chip">{source_label(metadata)}</span>'


def retrieval_trace_summary(trace: list[dict[str, object]], source_count: int) -> str:
    return f"{len(trace)} retrieval stages · {source_count} source chunks"
