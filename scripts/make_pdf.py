from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

# ---------- Layout settings (change these, not the code below) ----------
PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)      # about 842 x 595 points
OUTER_MARGIN = 30                            # gap between page edge and border
TEXT_PADDING = 60                            # gap between border and text
MAX_TEXT_WIDTH = PAGE_WIDTH - 2 * (OUTER_MARGIN + TEXT_PADDING)

FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

DARK = HexColor("#1F2A44")
GOLD = HexColor("#B8860B")

# Distance of each line from the TOP of the page (we convert to y later)
TITLE_Y = 150
SUBTITLE_Y = 215
NAME_Y = 280
BODY_Y = 335
COURSE_Y = 380
DATE_FROM_BOTTOM = 90


def y_from_top(distance: float) -> float:
    """reportlab's y=0 is the BOTTOM of the page; this lets us think from the top."""
    return PAGE_HEIGHT - distance


# ---------- Helpers ----------
def fit_font_size(text, font, max_size, min_size, max_width):
    """Shrink the font one point at a time until the text fits in max_width.

    Raises ValueError if it still doesn't fit at min_size.
    """
    size = max_size
    while size > min_size and stringWidth(text, font, size) > max_width:
        size -= 1
    if stringWidth(text, font, size) > max_width:
        raise ValueError(f"Text is too long to fit on the certificate: '{text[:30]}...'")
    return size


def validate_inputs(name: str, course: str, date_str: str) -> None:
    """Check inputs BEFORE drawing, so a bad row never creates a half-made file."""
    for label, value in (("name", name), ("course", course), ("date", date_str)):
        if value is None or not value.strip():
            raise ValueError(f"The {label} is empty")
        try:
            # Helvetica uses WinAnsi (cp1252): it can't draw Kannada, Hindi, etc.
            value.encode("cp1252")
        except UnicodeEncodeError:
            raise ValueError(
                f"The {label} contains characters the certificate font cannot draw"
            )


def draw_border(c: canvas.Canvas) -> None:
    c.setStrokeColor(GOLD)
    c.setLineWidth(4)
    c.rect(OUTER_MARGIN, OUTER_MARGIN,
           PAGE_WIDTH - 2 * OUTER_MARGIN, PAGE_HEIGHT - 2 * OUTER_MARGIN)
    c.setLineWidth(1)
    inner = OUTER_MARGIN + 10
    c.rect(inner, inner, PAGE_WIDTH - 2 * inner, PAGE_HEIGHT - 2 * inner)


# ---------- Main function----------
def generate_certificate(name: str, course: str, date_str: str, out_path: str) -> None:
    # 1. Validate and compute font sizes first. Any problem raises ValueError here.
    validate_inputs(name, course, date_str)
    name_size = fit_font_size(name, FONT_BOLD, max_size=36, min_size=16,
                              max_width=MAX_TEXT_WIDTH)
    course_size = fit_font_size(course, FONT_BOLD, max_size=26, min_size=14,
                                max_width=MAX_TEXT_WIDTH)

    # 2. Only now create the PDF.
    c = canvas.Canvas(out_path, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    center = PAGE_WIDTH / 2

    draw_border(c)

    c.setFillColor(DARK)
    c.setFont(FONT_BOLD, 38)
    c.drawCentredString(center, y_from_top(TITLE_Y), "Certificate of Completion")

    c.setFont(FONT_REGULAR, 18)
    c.drawCentredString(center, y_from_top(SUBTITLE_Y), "This is to certify that")

    c.setFont(FONT_BOLD, name_size)
    c.drawCentredString(center, y_from_top(NAME_Y), name)

    # Line under the name, as wide as the name itself
    name_width = stringWidth(name, FONT_BOLD, name_size)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(center - name_width / 2, y_from_top(NAME_Y) - 8,
           center + name_width / 2, y_from_top(NAME_Y) - 8)

    c.setFont(FONT_REGULAR, 18)
    c.drawCentredString(center, y_from_top(BODY_Y), "has successfully completed")

    c.setFont(FONT_BOLD, course_size)
    c.drawCentredString(center, y_from_top(COURSE_Y), course)

    c.setFont(FONT_REGULAR, 16)
    c.drawCentredString(center, DATE_FROM_BOTTOM, f"Date: {date_str}")

    c.showPage()
    c.save()


if __name__ == "__main__":
    generate_certificate("Asha Rao", "Backend Development", "07 Oct 2026", "test.pdf")

    # Long name: should shrink but still fit
    generate_certificate("Venkata Subramanian Ramachandran Iyer Narasimhan",
                         "Backend Development", "07 Oct 2026", "test_long.pdf")

    # Bad rows: should raise ValueError with a clear reason
    for bad_name in ["", "ಅಶಾ ರಾವ್", "A" * 200]:
        try:
            generate_certificate(bad_name, "Backend Development", "07 Oct 2026", "bad.pdf")
        except ValueError as e:
            print("Rejected:", e)