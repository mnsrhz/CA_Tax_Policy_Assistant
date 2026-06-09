from __future__ import annotations

import re


def detect_document_metadata(source_file: str, sample_text: str = "") -> dict[str, str]:
    filename = source_file.lower()
    text = sample_text.lower()
    combined = f"{filename} {text}"

    tax_year_match = re.search(r"(20\d{2})", filename)
    tax_year = tax_year_match.group(1) if tax_year_match else "unknown"

    agency = "FTB" if filename.startswith("202") or "california" in combined or "schedule ca" in combined else "IRS"
    jurisdiction = "california" if agency == "FTB" else "federal"

    if "instructions" in combined:
        document_type = "instructions"
    elif "booklet" in combined:
        document_type = "booklet"
    elif "publication" in combined or re.match(r"p\d+\.pdf", filename) or filename.startswith("pub"):
        document_type = "publication"
    elif "form" in combined or re.search(r"540", filename):
        document_type = "form"
    else:
        document_type = "unknown"

    number_matches = re.findall(r"(?:p|pub)?(\d{2,4})", filename)
    form_or_pub_number = "unknown"
    for number in number_matches:
        if number != tax_year:
            form_or_pub_number = number
            break

    return {
        "source_title": source_file.replace(".pdf", "").replace("-", " "),
        "tax_year": tax_year,
        "agency": agency,
        "jurisdiction": jurisdiction,
        "document_type": document_type,
        "form_or_pub_number": form_or_pub_number,
    }
