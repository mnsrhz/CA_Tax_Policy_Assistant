from __future__ import annotations

import re


IRS_PUBLICATION_TITLES = {
    "17": "Your Federal Income Tax",
    "334": "Tax Guide for Small Business",
    "502": "Medical and Dental Expenses",
    "503": "Child and Dependent Care Expenses",
    "504": "Divorced or Separated Individuals",
    "505": "Tax Withholding and Estimated Tax",
    "514": "Foreign Tax Credit for Individuals",
    "523": "Selling Your Home",
    "526": "Charitable Contributions",
    "527": "Residential Rental Property",
    "529": "Miscellaneous Deductions",
    "550": "Investment Income and Expenses",
    "587": "Business Use of Your Home",
    "936": "Home Mortgage Interest Deduction",
    "946": "How To Depreciate Property",
    "970": "Tax Benefits for Education",
}

EXACT_DISPLAY_TITLES = {
    "2024-1031-publication.pdf": "FTB Publication 1031: Guidelines for Determining Resident Status",
    "2024-1067-publication.pdf": "FTB Publication 1067: Guidelines for Filing a Group Form 540NR",
    "2024-3514.pdf": "California Form 3514: Earned Income Tax Credit",
    "2024-540-booklet.pdf": "California Form 540 Personal Income Tax Booklet",
    "2024-540-taxtable.pdf": "California Tax Table 2024",
    "2025-1005-publication.pdf": "FTB Publication 1005: Pension and Annuity Guidelines",
    "2025-3514-booklet.pdf": "California Earned Income Tax Credit Booklet",
    "2025-3840-instructions.pdf": "California Form FTB 3840 Instructions: Like-Kind Exchanges",
    "2025-540-ca-instructions.pdf": "California Schedule CA (540) Instructions",
    "2025-540-ca.pdf": "California Schedule CA (540)",
    "2025-540-d.pdf": "California Schedule D (540)",
    "i1040sca.pdf": "IRS Schedule A (Form 1040) Instructions: Itemized Deductions",
    "tax news _ ftb.ca.gov.pdf": "FTB Tax News",
    "pub31.pdf": "CDTFA Publication 31: Grocery Stores",
    "pub73.pdf": "CDTFA Publication 73: Your Rights and Responsibilities",
    "rp-23-34.pdf": "IRS Revenue Procedure 2023-34",
}


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

    display_title = display_title_for_document(filename, agency, document_type, form_or_pub_number, tax_year)

    return {
        "source_title": source_file.replace(".pdf", "").replace("-", " "),
        "display_title": display_title,
        "tax_year": tax_year,
        "agency": agency,
        "jurisdiction": jurisdiction,
        "document_type": document_type,
        "form_or_pub_number": form_or_pub_number,
    }


def display_title_for_document(
    filename: str,
    agency: str,
    document_type: str,
    form_or_pub_number: str,
    tax_year: str,
) -> str:
    if filename in EXACT_DISPLAY_TITLES:
        return EXACT_DISPLAY_TITLES[filename]
    if agency == "IRS" and document_type == "publication" and form_or_pub_number in IRS_PUBLICATION_TITLES:
        return f"IRS Publication {form_or_pub_number}: {IRS_PUBLICATION_TITLES[form_or_pub_number]}"
    if agency == "IRS" and form_or_pub_number != "unknown":
        return f"IRS {document_type.title()} {form_or_pub_number}"
    if agency == "FTB" and form_or_pub_number != "unknown":
        label = "California"
        if document_type == "instructions":
            return f"{label} Form {form_or_pub_number} Instructions"
        if document_type == "booklet":
            return f"{label} Form {form_or_pub_number} Booklet"
        return f"{label} Form {form_or_pub_number}"
    return filename.replace(".pdf", "").replace("-", " ").title()


def human_readable_title(metadata: dict[str, object]) -> str:
    display_title = str(metadata.get("display_title", "")).strip()
    if display_title:
        return display_title

    source_file = str(metadata.get("source_file", "")).lower()
    agency = str(metadata.get("agency", ""))
    document_type = str(metadata.get("document_type", "unknown"))
    form_or_pub_number = str(metadata.get("form_or_pub_number", "unknown"))
    tax_year = str(metadata.get("tax_year", "unknown"))
    if source_file:
        return display_title_for_document(source_file, agency, document_type, form_or_pub_number, tax_year)

    source_title = str(metadata.get("source_title", "")).strip()
    if source_title:
        return source_title
    return "Unknown source"
