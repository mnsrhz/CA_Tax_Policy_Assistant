# Answer Sharpness And UX Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make generated answers concise and source-grounded, and make the Streamlit UI visually closer to the supplied HTML mockup.

**Architecture:** Keep retrieval unchanged and add a local answer-brief helper to shape the final OpenAI prompt without an extra LLM call. Move Streamlit presentation helpers into `src/ui.py` so the app can render custom CSS, source chips, badges, and trace summaries while remaining testable.

**Tech Stack:** Python, Streamlit, OpenAI Responses API, pytest, HTML/CSS injected through Streamlit markdown.

---

## File Structure

- Modify `src/generation.py`: add answer brief and stricter prompt.
- Modify `tests/test_generation.py`: cover answer brief and concise prompt contract.
- Modify `src/ui.py`: add CSS, badge, source chip, and trace helper functions.
- Modify `tests/test_ui.py`: cover UI helper output.
- Modify `app.py`: render custom shell, compact filters, styled answer, source chips, and retrieval trace.

## Task 1: Concise Answer Contract

**Files:**
- Modify: `src/generation.py`
- Modify: `tests/test_generation.py`

- [ ] **Step 1: Write failing answer brief tests**

Add to `tests/test_generation.py`:

```python
from src.generation import build_answer_brief


def test_build_answer_brief_requests_sharp_cited_answer():
    brief = build_answer_brief("Can I deduct home office expenses?")

    assert "3-5 bullets" in brief
    assert "180 words" in brief
    assert "cite" in brief.lower()
    assert "Can I deduct home office expenses?" in brief
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_generation.py -v`

Expected: FAIL because `build_answer_brief` does not exist.

- [ ] **Step 3: Implement answer brief and update prompt**

Add to `src/generation.py`:

```python
def build_answer_brief(question: str) -> str:
    return f"""User question:
{question}

Answer style:
- Start with one direct conclusion sentence.
- Then use 3-5 bullets maximum.
- Keep the answer under roughly 180 words unless the user explicitly asks for detail.
- Cite source document and page for rule claims.
- Separate IRS/federal guidance from California/FTB guidance when both appear.
- If retrieved context is weak, say the loaded documents do not provide enough support.
- End with one short informational disclaimer."""
```

Update `build_answer_prompt()` so it includes:

```python
answer_brief = build_answer_brief(question)
```

and labels that section as `Answer brief:` before the retrieved context.

- [ ] **Step 4: Run generation tests**

Run: `.venv/bin/pytest tests/test_generation.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/generation.py tests/test_generation.py
git commit -m "feat: add concise answer prompt contract"
```

## Task 2: UI Styling Helpers

**Files:**
- Modify: `src/ui.py`
- Modify: `tests/test_ui.py`

- [ ] **Step 1: Write failing UI helper tests**

Add to `tests/test_ui.py`:

```python
from src.ui import badge_html, source_chip_html, retrieval_trace_summary


def test_badge_html_formats_class_and_text():
    assert badge_html("FTB", "blue") == '<span class="ct-badge ct-badge-blue">FTB</span>'


def test_source_chip_html_formats_source_label():
    chip = source_chip_html({"source_title": "IRS Publication 587", "page_number": 4})

    assert "ct-source-chip" in chip
    assert "IRS Publication 587 · p.4" in chip


def test_retrieval_trace_summary_includes_stage_count():
    summary = retrieval_trace_summary([{"stage": "strict"}, {"stage": "fallback"}], source_count=5)

    assert summary == "2 retrieval stages · 5 source chunks"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_ui.py -v`

Expected: FAIL because helper functions do not exist.

- [ ] **Step 3: Implement UI helpers**

Add to `src/ui.py`:

```python
def app_css() -> str:
    return """
<style>
.stApp { background: #F7F6F2; color: #1A1915; }
.ct-header { background:#FFFFFF; border:1px solid rgba(0,0,0,.08); border-radius:12px; padding:14px 18px; margin-bottom:12px; }
.ct-title { font-family: Georgia, serif; font-size:20px; color:#1A1915; margin:0; }
.ct-subtitle { font-size:12px; color:#888780; margin-top:2px; }
.ct-badges { display:flex; gap:6px; flex-wrap:wrap; margin-top:10px; }
.ct-badge { padding:3px 9px; border-radius:999px; font-size:11px; font-family:system-ui,sans-serif; }
.ct-badge-blue { background:#E6F1FB; color:#0C447C; }
.ct-badge-gold { background:#FAEEDA; color:#633806; }
.ct-badge-green { background:#EAF3DE; color:#27500A; }
.ct-answer { background:#FFFFFF; border:1px solid rgba(0,0,0,.08); border-radius:12px; padding:14px 16px; line-height:1.55; }
.ct-disclaimer { margin-top:10px; padding:8px 10px; background:#FAEEDA; border-left:2px solid #BA7517; border-radius:6px; font-size:12px; color:#854F0B; }
.ct-source-row { display:flex; gap:6px; flex-wrap:wrap; margin-top:10px; }
.ct-source-chip { display:inline-flex; padding:4px 9px; background:#F1EFE8; border:1px solid rgba(0,0,0,.08); border-radius:999px; font-size:11px; color:#5F5E5A; }
</style>
"""


def badge_html(text: str, color: str = "blue") -> str:
    return f'<span class="ct-badge ct-badge-{color}">{text}</span>'


def source_chip_html(metadata: dict[str, object]) -> str:
    return f'<span class="ct-source-chip">{source_label(metadata)}</span>'


def retrieval_trace_summary(trace: list[dict[str, object]], source_count: int) -> str:
    return f"{len(trace)} retrieval stages · {source_count} source chunks"
```

- [ ] **Step 4: Run UI tests**

Run: `.venv/bin/pytest tests/test_ui.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/ui.py tests/test_ui.py
git commit -m "feat: add styled Streamlit UI helpers"
```

## Task 3: Apply Refined UI In App

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Update imports**

Import the new helpers:

```python
from src.ui import app_css, badge_html, retrieval_trace_summary, source_chip_html
```

- [ ] **Step 2: Apply CSS and header**

At the start of `main()`, render CSS and a compact header:

```python
st.markdown(app_css(), unsafe_allow_html=True)
st.markdown(
    """
    <div class="ct-header">
      <p class="ct-title">CalTax Assistant</p>
      <div class="ct-subtitle">California and federal tax answers grounded in retrieved sources</div>
    </div>
    """,
    unsafe_allow_html=True,
)
```

- [ ] **Step 3: Render badges and styled answer**

After filters and retrieval, render badges with selected tax year, jurisdiction, and source count. Replace the plain assistant output with:

```python
st.markdown(f'<div class="ct-answer">{answer}</div>', unsafe_allow_html=True)
st.markdown('<div class="ct-disclaimer">For informational purposes only. Not a substitute for advice from a licensed tax professional.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ct-source-row">' + "".join(source_chip_html(context) for context in top_contexts) + "</div>",
    unsafe_allow_html=True,
)
```

- [ ] **Step 4: Run app smoke check**

Run: `.venv/bin/streamlit run app.py --server.headless true --server.port 8501`

Expected: App starts. Stop with Ctrl-C after startup.

- [ ] **Step 5: Run full tests and commit**

Run: `.venv/bin/pytest -v`

Expected: PASS.

```bash
git add app.py
git commit -m "feat: refine assistant Streamlit UI"
```

## Final Verification

- [ ] Run `.venv/bin/pytest -v`; expected PASS.
- [ ] Run the Streamlit app locally and ask one indexed tax question.
- [ ] Confirm answer is concise, cited, and visually styled.
- [ ] Push `main` to GitHub after merge.

