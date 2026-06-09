from src.generation import build_answer_prompt


def test_build_answer_prompt_includes_citation_rules_and_context():
    prompt = build_answer_prompt(
        question="Can I deduct home office expenses?",
        contexts=[
            {
                "text": "W-2 employees cannot deduct unreimbursed employee expenses.",
                "source_title": "IRS Publication 529",
                "page_number": 8,
                "agency": "IRS",
            }
        ],
    )

    assert "answer only from the retrieved context" in prompt.lower()
    assert "IRS Publication 529, page 8" in prompt
    assert "Can I deduct home office expenses?" in prompt
