from io import BytesIO


PAGE_WIDTH = 612
PAGE_HEIGHT = 792
LEFT_MARGIN = 54
TOP_MARGIN = 730
FONT_SIZE = 12
LINE_HEIGHT = 16
MAX_LINE_CHARS = 88


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap_text(text: str) -> list[str]:
    words = text.split()
    if not words:
        return ["No summary available."]

    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if len(candidate) <= MAX_LINE_CHARS:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def build_summary_pdf(summary: str, length: str) -> bytes:
    lines = [f"Summary Length: {length.title()}", ""] + _wrap_text(summary)
    content_lines = ["BT", f"/F1 {FONT_SIZE} Tf", f"{LEFT_MARGIN} {TOP_MARGIN} Td"]

    first_line = True
    for line in lines:
        if not first_line:
            content_lines.append(f"0 -{LINE_HEIGHT} Td")
        content_lines.append(f"({_escape_pdf_text(line)}) Tj")
        first_line = False
    content_lines.append("ET")

    stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    objects.append(
        f"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n".encode(
            "ascii"
        )
    )
    objects.append(
        f"4 0 obj << /Length {len(stream)} >> stream\n".encode("ascii") + stream + b"\nendstream endobj\n"
    )
    objects.append(b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")

    buffer = BytesIO()
    buffer.write(b"%PDF-1.4\n")

    offsets = [0]
    for obj in objects:
        offsets.append(buffer.tell())
        buffer.write(obj)

    xref_start = buffer.tell()
    buffer.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    buffer.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.write(f"{offset:010d} 00000 n \n".encode("ascii"))

    trailer = (
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode("ascii")
    )
    buffer.write(trailer)
    return buffer.getvalue()
