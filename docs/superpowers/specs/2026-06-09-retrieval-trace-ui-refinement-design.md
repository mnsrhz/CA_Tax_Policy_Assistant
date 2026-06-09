# Retrieval Trace UI Refinement Design

## Goal

Change the visible retrieval trace from a raw JSON-first Streamlit expander into a compact pipeline block matching the supplied `UX Design/california_tax_assistant_ui.html` mockup.

## Current Problem

The app currently shows the trace as a caption plus raw JSON in an expander. This is useful for debugging but does not match the mockup, where retrieval progress appears as a styled inline pipeline with pill steps and arrows.

## Design

Add a visual trace block below the assistant answer and source chips:

- Panel style similar to the HTML mockup's `pipeline-trace`.
- Title: `Retrieval trace`.
- Pill steps:
  - selected tax-year pre-filter
  - selected jurisdiction/filter scope
  - vector search
  - fallback widening only when a fallback trace stage exists
  - reranked top source count
- Arrow separators between pills.
- Raw `st.json(trace)` stays available inside a compact `Raw trace` expander for debugging.

## Implementation

- Add CSS classes in `src/ui.py`:
  - `.ct-pipeline-trace`
  - `.ct-pipeline-title`
  - `.ct-pipeline-steps`
  - `.ct-pipeline-step`
  - `.ct-pipeline-arrow`
- Add `retrieval_trace_html(trace, tax_year, jurisdiction, source_count)` in `src/ui.py`.
- Update `app.py` to render `retrieval_trace_html(...)` with `unsafe_allow_html=True`.
- Keep the raw JSON trace under a separate `Raw trace` expander.

## Testing

Add tests confirming:

- The trace HTML includes the expected pipeline classes.
- The trace HTML includes tax year, jurisdiction, vector search, and reranked count.
- A fallback pill appears only when the trace contains a `fallback` stage.

