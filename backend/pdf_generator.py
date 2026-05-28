from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


BLUE = colors.HexColor("#1457B8")
DARK_BLUE = colors.HexColor("#0B3D91")
LIGHT_BLUE = colors.HexColor("#E6F0FF")
GRID_BLUE = colors.HexColor("#D9E6F7")
GRAY = colors.HexColor("#64748B")
LIGHT_GRAY = colors.HexColor("#F8FAFC")
DARK_GRAY = colors.HexColor("#374151")


def generate_seating_pdf(arrangement, metadata=None, output_dir="reports"):
    metadata = _normalize_metadata(metadata)
    report_dir = Path(output_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    filename = f"exam_seating_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output_path = report_dir / filename

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=landscape(A4),
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.38 * inch,
        bottomMargin=0.38 * inch,
        title="Examination Seating Arrangement",
    )

    story = []
    styles = _build_styles()
    _add_summary_page(story, styles, arrangement, metadata)

    for hall_index, hall in enumerate(arrangement.get("halls", [])):
        story.append(PageBreak())
        _add_hall_page(story, styles, hall, metadata, hall_index + 1)

    document.build(story)
    return output_path


def _build_styles():
    base_styles = getSampleStyleSheet()
    base_styles.add(ParagraphStyle(
        name="UniversityTitle",
        parent=base_styles["Title"],
        alignment=TA_CENTER,
        textColor=DARK_BLUE,
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        spaceAfter=6,
    ))
    base_styles.add(ParagraphStyle(
        name="ReportSubTitle",
        parent=base_styles["Heading2"],
        alignment=TA_CENTER,
        textColor=BLUE,
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        spaceAfter=12,
    ))
    base_styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=base_styles["Heading2"],
        textColor=DARK_BLUE,
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        spaceBefore=6,
        spaceAfter=8,
    ))
    return base_styles


def _add_summary_page(story, styles, arrangement, metadata):
    story.extend([
        Paragraph("UNIVERSITY EXAMINATION CELL", styles["UniversityTitle"]),
        Paragraph("AI-Based Examination Seating Arrangement", styles["ReportSubTitle"]),
        _metadata_table(metadata),
        Spacer(1, 14),
        Paragraph("Hall Summary", styles["SectionHeading"]),
    ])

    summary_rows = [["S.No", "Room No", "Roll Number Range", "Total Strength"]]
    total_students = 0
    total_capacity = 0

    for index, hall in enumerate(arrangement.get("halls", []), start=1):
        rolls = _roll_numbers_for_hall(hall)
        occupied_count = len(rolls)
        capacity = _hall_capacity(hall)
        total_students += occupied_count
        total_capacity += capacity
        summary_rows.append([
            str(index),
            hall.get("hallName", "Hall"),
            _roll_range(rolls),
            str(occupied_count),
        ])

    summary_table = Table(summary_rows, colWidths=[0.7 * inch, 2.3 * inch, 4.0 * inch, 1.5 * inch])
    summary_table.setStyle(_academic_table_style(header_rows=1))
    story.append(summary_table)
    story.append(Spacer(1, 16))

    totals = Table([
        ["Hall Name", "Student Count", "Hall Capacity"],
        ["All Halls", str(total_students), str(total_capacity)],
    ], colWidths=[2.2 * inch, 1.7 * inch, 1.7 * inch])
    totals.setStyle(_academic_table_style(header_rows=1))
    story.append(totals)


def _add_hall_page(story, styles, hall, metadata, hall_number):
    occupied_count = len(_roll_numbers_for_hall(hall))

    story.extend([
        Paragraph("UNIVERSITY EXAMINATION CELL", styles["UniversityTitle"]),
        Paragraph(f"Hall Seating Plan - {hall.get('hallName', f'Hall {hall_number}')}", styles["ReportSubTitle"]),
        _metadata_table(metadata, hall.get("hallName", "")),
        Spacer(1, 12),
    ])

    seating_rows = _build_seating_rows(hall)
    grid_table = Table(seating_rows)
    grid_table.setStyle(_seating_table_style(hall))
    story.append(grid_table)
    story.append(Spacer(1, 16))

    footer_table = Table([
        ["Registered Count", "Present Count", "Absent Count", "Invigilator Signature"],
        [str(occupied_count), "", "", ""],
    ], colWidths=[1.6 * inch, 1.6 * inch, 1.6 * inch, 2.5 * inch], rowHeights=[None, 0.42 * inch])
    footer_table.setStyle(_academic_table_style(header_rows=1))
    story.append(footer_table)


def _metadata_table(metadata, hall_name=None):
    rows = [
        ["Exam Name", metadata["examName"], "Date", metadata["date"]],
        ["Session", metadata["session"], "Exam Time", metadata["examTime"]],
    ]
    if hall_name:
        rows.append(["Hall Name", hall_name, "Generated On", metadata["generatedOn"]])

    table = Table(rows, colWidths=[1.15 * inch, 3.0 * inch, 1.15 * inch, 2.2 * inch])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, GRID_BLUE),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BLUE),
        ("BACKGROUND", (2, 0), (2, -1), LIGHT_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#10233F")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def _build_seating_rows(hall):
    cols = int(hall.get("cols", 0))
    header = [f"C{index}" for index in range(1, cols + 1)]
    rows = [["Row"] + header]

    for row_index, row in enumerate(hall.get("seating", []), start=1):
        rows.append([f"R{row_index}"] + [_format_seat(seat) for seat in row])

    return rows


def _format_seat(seat):
    if seat is None:
        return ""
    if seat == "BLOCKED":
        return "X"
    if isinstance(seat, dict):
        return seat.get("RollNo", "")
    return str(seat)


def _roll_numbers_for_hall(hall):
    rolls = []
    for row in hall.get("seating", []):
        for seat in row:
            if isinstance(seat, dict) and seat.get("RollNo"):
                rolls.append(str(seat["RollNo"]))
    return rolls


def _roll_range(rolls):
    if not rolls:
        return "-"
    if len(rolls) == 1:
        return rolls[0]
    return f"{rolls[0]} - {rolls[-1]}"


def _hall_capacity(hall):
    capacity = 0
    for row in hall.get("seating", []):
        for seat in row:
            if seat != "BLOCKED":
                capacity += 1
    return capacity


def _academic_table_style(header_rows=1):
    commands = [
        ("BACKGROUND", (0, 0), (-1, header_rows - 1), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, header_rows - 1), colors.white),
        ("FONTNAME", (0, 0), (-1, header_rows - 1), "Helvetica-Bold"),
        ("BACKGROUND", (0, header_rows), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID_BLUE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    return TableStyle(commands)


def _seating_table_style(hall):
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (0, -1), LIGHT_BLUE),
        ("TEXTCOLOR", (0, 1), (0, -1), DARK_BLUE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.45, GRID_BLUE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]

    for row_index, row in enumerate(hall.get("seating", []), start=1):
        for col_index, seat in enumerate(row, start=1):
            if seat == "BLOCKED":
                commands.extend([
                    ("BACKGROUND", (col_index, row_index), (col_index, row_index), DARK_GRAY),
                    ("TEXTCOLOR", (col_index, row_index), (col_index, row_index), colors.white),
                    ("FONTNAME", (col_index, row_index), (col_index, row_index), "Helvetica-Bold"),
                ])
            elif seat is None:
                commands.append(("BACKGROUND", (col_index, row_index), (col_index, row_index), LIGHT_GRAY))

    return TableStyle(commands)


def _normalize_metadata(metadata):
    metadata = metadata or {}
    return {
        "examName": metadata.get("examName") or metadata.get("exam") or "End Semester Examination",
        "date": metadata.get("date") or "To be announced",
        "session": metadata.get("session") or "Morning",
        "examTime": metadata.get("examTime") or "10:00 AM - 1:00 PM",
        "generatedOn": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
    }
