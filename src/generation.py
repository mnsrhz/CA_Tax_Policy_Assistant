from __future__ import annotations

from openai import OpenAI


def build_answer_prompt(question: str, contexts: list[dict[str, object]]) -> str:
    context_blocks = []
    for index, context in enumerate(contexts, start=1):
        source_title = context.get("source_title", context.get("source_file", "Unknown source"))
        page_number = context.get("page_number", "unknown")
        agency = context.get("agency", "unknown")
        text = context.get("text", "")
        context_blocks.append(f"[Source {index}: {source_title}, page {page_number}, agency {agency}]\n{text}")

    joined_context = "\n\n".join(context_blocks)
    return f"""You are a California tax policy assistant for educational use.

Answer only from the retrieved context. Cite source document and page for specific claims.
Distinguish federal IRS guidance from California FTB guidance. If the context does not support an answer, say so.
Do not invent thresholds, deadlines, forms, or eligibility rules. Include a brief informational disclaimer.

Question:
{question}

Retrieved context:
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
