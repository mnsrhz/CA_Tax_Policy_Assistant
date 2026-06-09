from src.metadata import detect_document_metadata


def test_detects_irs_publication_metadata():
    metadata = detect_document_metadata("p587.pdf", "Publication 587 Business Use of Your Home")

    assert metadata["agency"] == "IRS"
    assert metadata["jurisdiction"] == "federal"
    assert metadata["document_type"] == "publication"
    assert metadata["form_or_pub_number"] == "587"


def test_detects_ftb_form_metadata():
    metadata = detect_document_metadata("2025-540-ca-instructions.pdf", "Schedule CA Instructions")

    assert metadata["agency"] == "FTB"
    assert metadata["jurisdiction"] == "california"
    assert metadata["document_type"] == "instructions"
    assert metadata["form_or_pub_number"] == "540"
    assert metadata["tax_year"] == "2025"
