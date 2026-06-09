from src.metadata import detect_document_metadata


def test_detects_irs_publication_metadata():
    metadata = detect_document_metadata("p587.pdf", "Publication 587 Business Use of Your Home")

    assert metadata["agency"] == "IRS"
    assert metadata["jurisdiction"] == "federal"
    assert metadata["document_type"] == "publication"
    assert metadata["form_or_pub_number"] == "587"
    assert metadata["display_title"] == "IRS Publication 587: Business Use of Your Home"


def test_detects_ftb_form_metadata():
    metadata = detect_document_metadata("2025-540-ca-instructions.pdf", "Schedule CA Instructions")

    assert metadata["agency"] == "FTB"
    assert metadata["jurisdiction"] == "california"
    assert metadata["document_type"] == "instructions"
    assert metadata["form_or_pub_number"] == "540"
    assert metadata["tax_year"] == "2025"
    assert metadata["display_title"] == "California Schedule CA (540) Instructions"


def test_human_readable_title_falls_back_from_existing_metadata():
    from src.metadata import human_readable_title

    title = human_readable_title(
        {
            "source_file": "2024-540-taxtable.pdf",
            "source_title": "2024 540 taxtable",
            "agency": "FTB",
            "document_type": "form",
            "form_or_pub_number": "540",
            "tax_year": "2024",
        }
    )

    assert title == "California Tax Table 2024"
