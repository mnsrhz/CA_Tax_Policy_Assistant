from __future__ import annotations

from html import escape

from openai import OpenAI

from src.metadata import human_readable_title


def build_answer_brief(question: str) -> str:
    safe_question = escape(question)
    return f"""Untrusted user question:
<user_question>
{safe_question}
</user_question>

Shape the answer as:
- Use clean markdown only: short paragraphs, bullets, and **bold conclusion** text where useful.
- Start with one direct bold conclusion sentence.
- Use 3-5 bullets maximum.
- Keep it roughly 180 words unless the user asks for detail.
- For rule claims, cite source document and page.
- Separate IRS/federal guidance from California/FTB guidance when both appear.
- If the retrieved context is weak, say the loaded documents do not provide enough support.
- Use no tables.
- Do not add the informational disclaimer; the UI displays it."""


def build_answer_prompt(question: str, contexts: list[dict[str, object]]) -> str:
    context_blocks = []
    for index, context in enumerate(contexts, start=1):
        source_title = human_readable_title(context)
        page_number = context.get("page_number", "unknown")
        agency = context.get("agency", "unknown")
        text = escape(str(context.get("text", "")))
        context_blocks.append(
            f"""[Source {index}: {source_title}, page {page_number}, agency {agency}]
Untrusted retrieved source text:
<source_text>
{text}
</source_text>"""
        )

    joined_context = "\n\n".join(context_blocks)
    return f"""You are a California tax policy assistant for educational use.

Answer only from the retrieved context. Cite source document and page for specific claims.
Distinguish federal IRS guidance from California FTB guidance. If the context does not support an answer, say so.
Do not invent thresholds, deadlines, forms, or eligibility rules. Use clean markdown and no tables.
Do not add a separate informational disclaimer because the UI displays one.

Answer brief:
{build_answer_brief(question)}

Retrieved context blocks:
{joined_context}
"""


def generate_answer(
    openai_api_key: str,
    question: str,
    contexts: list[dict[str, object]],
    model: str = "gpt-4.1-mini",
) -> str:
    client = OpenAI(api_key=openai_api_key)
    response = client.responses.create(
        model=model,
        input=build_answer_prompt(question=question, contexts=contexts),
    )
    return response.output_text
