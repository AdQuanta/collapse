"""Render the Markdown study report plus completion figures to a polished PDF."""
from __future__ import annotations

from html import escape
from pathlib import Path
import re
import textwrap

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle,
    KeepTogether, Preformatted,
)

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "reports" / "resonant_hz_study_2026-07-12.md"
OUT = ROOT / "reports" / "resonant_hz_study_2026-07-12.pdf"
FIG = ROOT / "figures" / "single_pixel_quspin_fresh_2026-07-12"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("ReportTitle", parent=styles["Title"], fontSize=22, leading=26, textColor=colors.HexColor("#17324d"), spaceAfter=12))
styles.add(ParagraphStyle("H1x", parent=styles["Heading1"], fontSize=15, leading=18, textColor=colors.HexColor("#17324d"), spaceBefore=10, spaceAfter=6))
styles.add(ParagraphStyle("BodyX", parent=styles["BodyText"], fontSize=9.2, leading=12.2, spaceAfter=6))
styles.add(ParagraphStyle("CaptionX", parent=styles["BodyText"], fontSize=8, leading=10, textColor=colors.HexColor("#40566b"), alignment=TA_CENTER, spaceAfter=8))
styles.add(ParagraphStyle("CodeX", parent=styles["Code"], fontSize=6.8, leading=8.2, backColor=colors.HexColor("#f2f5f7"), leftIndent=5, rightIndent=5, spaceAfter=7))


def clean_inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font name='Courier'>\1</font>", text)
    return text


def markdown_story() -> list:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    story: list = []
    index = 0
    in_code = False
    code_lines: list[str] = []
    while index < len(lines):
        line = lines[index]
        if line.startswith("```"):
            if in_code:
                wrapped = []
                for code_line in code_lines:
                    wrapped.extend(textwrap.wrap(code_line, width=108, subsequent_indent="    ", replace_whitespace=False) or [""])
                story.append(Preformatted("\n".join(wrapped), styles["CodeX"]))
                code_lines = []
            in_code = not in_code
            index += 1
            continue
        if in_code:
            code_lines.append(line)
            index += 1
            continue
        if not line.strip():
            index += 1
            continue
        if line.startswith("# "):
            story.append(Paragraph(clean_inline(line[2:]), styles["ReportTitle"]))
            index += 1
            continue
        if line.startswith("## "):
            story.append(Paragraph(clean_inline(line[3:]), styles["H1x"]))
            index += 1
            continue
        if line.startswith("|") and index + 1 < len(lines) and lines[index + 1].startswith("|"):
            table_lines = []
            while index < len(lines) and lines[index].startswith("|"):
                table_lines.append(lines[index])
                index += 1
            rows = [[cell.strip() for cell in row.strip("|").split("|")] for row in table_lines]
            if len(rows) > 1 and all(set(cell) <= set(":-") for cell in rows[1]):
                rows.pop(1)
            data = [[Paragraph(clean_inline(cell), styles["BodyX"]) for cell in row] for row in rows]
            widths = [6.8 * inch / len(data[0])] * len(data[0])
            table = Table(data, colWidths=widths, repeatRows=1, hAlign="CENTER")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce8f2")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17324d")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9fb3c5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            story.extend([table, Spacer(1, 6)])
            continue
        if line.startswith("- ") or re.match(r"^\d+\. ", line):
            bullet = line.split(" ", 1)[1]
            story.append(Paragraph("- " + clean_inline(bullet), styles["BodyX"]))
            index += 1
            continue
        if line.strip() in ("\\[", "\\]") or line.strip().startswith("\\["):
            equation = []
            while index < len(lines):
                equation.append(lines[index])
                if lines[index].strip() == "\\]":
                    index += 1
                    break
                index += 1
            story.append(Preformatted("\n".join(equation), styles["CodeX"]))
            continue
        paragraph = [line]
        index += 1
        while index < len(lines) and lines[index].strip() and not lines[index].startswith(("#", "|", "- ", "```")) and not re.match(r"^\d+\. ", lines[index]):
            paragraph.append(lines[index])
            index += 1
        story.append(Paragraph(clean_inline(" ".join(paragraph)), styles["BodyX"]))
    return story


def figure_page(filename: str, caption: str, height: float = 6.5) -> list:
    image = Image(str(FIG / filename), width=6.9 * inch, height=height * inch, kind="proportional")
    return [PageBreak(), KeepTogether([image, Paragraph(caption, styles["CaptionX"])])]


story = markdown_story()
story += figure_page("N8_near_resonance_resolution.png", "Figure 1. Fresh near-resonance sweep at offsets down to 0.01 around all three lines and every required time.", 7.2)
story += figure_page("N10_required_times_metrics_and_conditioning.png", "Figure 2. Required-time canonical Born similarity, ratio residual, and U00 conditioning.", 4.2)
story += figure_page("N10_all_required_Ptheta_reflection_theory.png", "Figure 3. Every mandatory N=10 field/time point: P(theta), its reflection, and the no-fit wrapped-Gaussian prediction.", 8.5)
story += figure_page("N10_all_required_R_minus_Born.png", "Figure 4. Residual R(theta)-cos^2(theta/2) for every mandatory point.", 8.2)
story += figure_page("N8_long_time_average_with_block_uncertainty.png", "Figure 5. Genuine equal-time-weighted average over 66 distinct times above 10^3; shading is the time-block standard error.", 5.5)
story += figure_page("N8_long_time_stability.png", "Figure 6. Long-time sensitivity to interleaved grids, lower cutoff, and angular binning.", 4.2)
story += figure_page("N8_N10_finite_size_Sborn.png", "Figure 7. Required-time finite-size comparison between N=8 and N=10.", 3.3)
story += figure_page("N10_full_and_detector_spectra_shifted.png", "Figure 8. Mean-shifted full and detector spectral CDFs.", 5.4)
story += figure_page("N10_detector_sector_level_statistics.png", "Figure 9. Detector spacings in one resolved symmetry sector, with Poisson/GOE/GUE references; retained samples are small.", 5.4)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#9fb3c5"))
    canvas.line(0.65 * inch, 0.48 * inch, 7.85 * inch, 0.48 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#40566b"))
    canvas.drawString(0.68 * inch, 0.32 * inch, "Single-pixel resonant-field study | 2026-07-12")
    canvas.drawRightString(7.82 * inch, 0.32 * inch, f"page {doc.page}")
    canvas.restoreState()


SimpleDocTemplate(
    str(OUT), pagesize=letter, rightMargin=0.65 * inch, leftMargin=0.65 * inch,
    topMargin=0.58 * inch, bottomMargin=0.62 * inch,
    title="Single-pixel Hamiltonian resonant-field comparison",
    author="Collapse and Chaos project",
).build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
