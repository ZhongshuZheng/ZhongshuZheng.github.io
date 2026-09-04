"""Convert a DOCX note into reviewable Markdown and extracted images.

The converter handles the repeatable mechanical work. It deliberately avoids
guessing semantic structure when the Word document only uses normal paragraphs;
that final editorial pass belongs to the reviewer.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

from docx import Document
from docx.document import Document as DocumentType
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.text.run import Run


def iter_blocks(document: DocumentType) -> Iterable[Paragraph | Table]:
    """Yield top-level paragraphs and tables in document order."""

    for child in document.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, document)
        elif child.tag == qn("w:tbl"):
            yield Table(child, document)


def escape_markdown(text: str) -> str:
    """Escape characters that can accidentally change Markdown semantics."""

    return re.sub(r"([\\*_\[\]])", r"\\\1", text)


def format_run(run: Run) -> str:
    text = escape_markdown(run.text.replace("\t", "    ").replace("\n", "  \n"))
    if not text.strip():
        return text
    if run.bold and run.italic:
        return f"***{text}***"
    if run.bold:
        return f"**{text}**"
    if run.italic:
        return f"*{text}*"
    return text


def image_extension(part: object) -> str:
    partname = str(getattr(part, "partname", ""))
    suffix = Path(partname).suffix.lower()
    if suffix:
        return suffix
    content_type = getattr(part, "content_type", "")
    return {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/svg+xml": ".svg",
        "image/tiff": ".tiff",
        "image/bmp": ".bmp",
        "image/webp": ".webp",
    }.get(content_type, ".bin")


class ImageExporter:
    def __init__(self, document: DocumentType, output_dir: Path) -> None:
        self.document = document
        self.output_dir = output_dir
        self.count = 0

    def export_from_run(self, run: Run) -> list[tuple[str, str]]:
        exported: list[tuple[str, str]] = []
        for relationship_id in run._r.xpath(".//a:blip/@r:embed"):
            part = self.document.part.related_parts[relationship_id]
            self.count += 1
            filename = f"image-{self.count:02d}{image_extension(part)}"
            destination = self.output_dir / "images" / filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(part.blob)
            exported.append((f"图片 {self.count}", f"images/{filename}"))
        return exported


def paragraph_fragments(
    paragraph: Paragraph, exporter: ImageExporter
) -> tuple[str, list[tuple[str, str]]]:
    text_parts: list[str] = []
    images: list[tuple[str, str]] = []

    for item in paragraph.iter_inner_content():
        if isinstance(item, Run):
            text_parts.append(format_run(item))
            images.extend(exporter.export_from_run(item))
            continue

        label = escape_markdown(getattr(item, "text", ""))
        url = getattr(item, "url", "") or ""
        if label and url:
            text_parts.append(f"[{label}]({url})")
        else:
            text_parts.append(label)

    return "".join(text_parts).strip(), images


def heading_level(style_name: str) -> int | None:
    match = re.search(r"(?:heading|标题)\s*([1-6])", style_name, re.IGNORECASE)
    if not match:
        return None
    # The article title is H1, so Word Heading 1 becomes a section-level H2.
    return min(int(match.group(1)) + 1, 6)


def list_details(paragraph: Paragraph) -> tuple[str, int] | None:
    style_name = paragraph.style.name if paragraph.style else ""
    normalized = style_name.casefold()
    paragraph_properties = paragraph._p.pPr
    numbering = paragraph_properties.numPr if paragraph_properties is not None else None

    is_list_style = "list" in normalized or "列表" in normalized
    if numbering is None and not is_list_style:
        return None

    level = 0
    if numbering is not None and numbering.ilvl is not None:
        level = int(numbering.ilvl.val)

    numbered = "number" in normalized or "编号" in normalized
    return ("1." if numbered else "-", level)


def table_markdown(table: Table) -> str:
    rows = []
    for row in table.rows:
        values = []
        for cell in row.cells:
            value = " ".join(cell.text.split()).replace("|", r"\|")
            values.append(value)
        rows.append(values)

    if not rows:
        return ""

    width = max(len(row) for row in rows)
    normalized_rows = [row + [""] * (width - len(row)) for row in rows]
    header = normalized_rows[0]
    body = normalized_rows[1:]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * width) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return "\n".join(lines)


def join_blocks(blocks: list[tuple[str, str]]) -> str:
    output: list[str] = []
    previous_kind: str | None = None
    for kind, text in blocks:
        if not text:
            continue
        separator = "\n" if kind == "list" and previous_kind == "list" else "\n\n"
        if output:
            output.append(separator)
        output.append(text)
        previous_kind = kind
    return "".join(output).rstrip() + "\n"


def convert(source: Path, output: Path, title: str | None = None, force: bool = False) -> dict:
    source = source.resolve()
    output = output.resolve()
    if output.exists() and not force:
        raise FileExistsError(f"Output already exists: {output}. Use --force to replace it.")

    document = Document(source)
    article_title = title or source.stem
    output.parent.mkdir(parents=True, exist_ok=True)
    exporter = ImageExporter(document, output.parent)
    blocks: list[tuple[str, str]] = [("heading", f"# {escape_markdown(article_title)}")]
    style_counts: Counter[str] = Counter()
    normal_paragraphs = 0
    semantic_headings = 0
    semantic_lists = 0
    floating_images = 0
    skipped_title = False

    for block in iter_blocks(document):
        if isinstance(block, Table):
            blocks.append(("table", table_markdown(block)))
            continue

        style_name = block.style.name if block.style else ""
        text, images = paragraph_fragments(block, exporter)
        if text:
            style_counts[style_name or "(none)"] += 1

            if not skipped_title and text == article_title:
                skipped_title = True
            else:
                level = heading_level(style_name)
                list_info = list_details(block)
                if level is not None:
                    semantic_headings += 1
                    blocks.append(("heading", f"{'#' * level} {text}"))
                elif list_info is not None:
                    semantic_lists += 1
                    marker, indent_level = list_info
                    blocks.append(("list", f"{'    ' * indent_level}{marker} {text}"))
                else:
                    normal_paragraphs += 1
                    blocks.append(("paragraph", text))

        if block._p.xpath(".//wp:anchor"):
            floating_images += len(block._p.xpath(".//wp:anchor"))

        for alt_text, relative_path in images:
            figure = (
                '<figure markdown="span">\n'
                f"  ![{alt_text}]({relative_path}){{ loading=lazy }}\n"
                f"  <figcaption>{alt_text}</figcaption>\n"
                "</figure>"
            )
            blocks.append(("image", figure))

    output.write_text(join_blocks(blocks), encoding="utf-8")

    warnings: list[str] = []
    if semantic_headings == 0:
        warnings.append("No semantic Word heading styles were found; review section hierarchy manually.")
    if semantic_lists == 0:
        warnings.append("No semantic Word list styles were found; review list-like paragraphs manually.")
    if floating_images:
        warnings.append(f"Found {floating_images} floating image(s); verify their intended positions.")

    return {
        "source": str(source),
        "output": str(output),
        "images": exporter.count,
        "tables": len(document.tables),
        "normal_paragraphs": normal_paragraphs,
        "semantic_headings": semantic_headings,
        "semantic_lists": semantic_lists,
        "styles": dict(style_counts),
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Source .docx file")
    parser.add_argument("output", type=Path, help="Destination Markdown file")
    parser.add_argument("--title", help="Article title; defaults to the Word filename")
    parser.add_argument("--force", action="store_true", help="Replace an existing Markdown file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = convert(args.source, args.output, title=args.title, force=args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
