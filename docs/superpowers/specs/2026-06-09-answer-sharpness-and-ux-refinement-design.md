# Answer Sharpness And UX Refinement Design

## Goal

Improve the assistant so answers are concise, source-grounded, and visually closer to the provided `UX Design/california_tax_assistant_ui.html` mockup.

## Current Problems

- Generated answers are too long for the classroom assistant experience.
- The final prompt does not impose a clear answer shape, word budget, or citation rhythm.
- The Streamlit UI is functional but does not yet match the supplied HTML mockup's compact chat shell, source chips, badges, retrieval trace, and assistant styling.

## Answer Behavior

Add a testable answer-brief helper before final prompt construction. This helper will not make an extra OpenAI call. It will transform the raw user question into a local instruction bundle for answer generation.

The final answer should follow this contract:

- Start with one direct conclusion sentence.
- Use 3-5 bullets maximum.
- Stay under roughly 180 words unless the user explicitly asks for detail.
- Cite source document and page for rule claims.
- Distinguish IRS/federal guidance from California/FTB guidance.
- State when the retrieved context does not provide enough support.
- End with a short informational disclaimer.

Retrieval should continue using the original user question. The answer brief only shapes the final LLM response.

## Prompting Changes

`src/generation.py` will add:

- `build_answer_brief(question)` to create concise answer instructions.
- A stricter `build_answer_prompt()` that includes the answer brief, source context, citation rules, and unsupported-evidence behavior.

The OpenAI call will still use one generation request.

## UX Changes

The Streamlit app should adopt the visual language of the HTML mockup while staying practical in Streamlit:

- Apply custom CSS using the mockup palette, typography, borders, and compact spacing.
- Keep a sidebar with app identity, filters, and recent question examples from session state.
- Render a compact top status row with badges for selected jurisdiction, tax year, and source count.
- Render user and assistant messages as custom-styled bubbles.
- Render citations as source chips below the answer.
- Render retrieval trace in a compact expander.
- Preserve Streamlit-native filter controls for reliability.

The UI should feel like a focused assistant rather than a default Streamlit demo.

## Testing

Add tests for:

- Answer brief includes concise-answer requirements and citation expectations.
- Prompt includes the answer brief and source/page context.
- Source chip HTML/helper formats document/page labels.
- Retrieval trace formatting remains stable for UI display.

Run the full pytest suite after implementation.
