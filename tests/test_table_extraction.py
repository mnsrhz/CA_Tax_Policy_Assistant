from src.table_extraction import blocks_outside_tables, should_detect_tables, table_to_prose


def test_table_to_prose_denormalizes_if_then_table():
    rows = [
        ["IF YOU...", "", "THEN USE...", ""],
        ["Have additional income, such as business income.", "Schedule 1, Part I", None, None],
        ["Owe alternative minimum tax.", "Schedule 2, Part I", None, None],
    ]

    prose = table_to_prose(rows, page_number=3)

    assert "Table on page 3:" in prose
    assert "If you have additional income, such as business income, then use Schedule 1, Part I." in prose
    assert "If you owe alternative minimum tax, then use Schedule 2, Part I." in prose
    assert "IF YOU" not in prose


def test_table_to_prose_denormalizes_generic_header_rows():
    rows = [
        ["Taxable income", "Single", "Married/RDP filing jointly"],
        ["$0 to $10,756", "$0", "$0"],
    ]

    prose = table_to_prose(rows, page_number=1)

    assert (
        "For Taxable income $0 to $10,756, Single is $0, and Married/RDP filing jointly is $0."
        in prose
    )


def test_blocks_outside_tables_removes_blocks_inside_table_bbox():
    blocks = [
        (0, 0, 100, 30, "normal text", 0, 0),
        (10, 50, 90, 80, "table text", 1, 0),
    ]

    outside = blocks_outside_tables(blocks, table_bboxes=[(0, 40, 100, 100)])

    assert [block[4] for block in outside] == ["normal text"]


def test_should_detect_tables_only_for_table_like_pages():
    assert should_detect_tables("IF YOU...\nTHEN USE...\nSchedule 1")
    assert should_detect_tables("2025 California Tax Rate Schedules")
    assert not should_detect_tables("This page mentions filing status but has ordinary instructions.")
