"""Convert XML requirements documents into Markdown files for ingestion."""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def clean_tag(tag: str) -> str:
    return tag.split("}", 1)[-1]


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def node_text(node: ET.Element) -> str:
    return clean_text(" ".join(part for part in node.itertext() if clean_text(part)))


def child_text(node: ET.Element, name: str) -> str:
    for child in node:
        if clean_tag(child.tag) == name:
            return node_text(child)
    return ""


def safe_filename(value: str) -> str:
    value = re.sub(r"[^\w.-]+", "_", value.strip().lower())
    return value.strip("_") or "requirements_document"


def section_heading(node: ET.Element) -> str:
    title = child_text(node, "title")
    section_id = node.attrib.get("id", "").strip()
    if title and section_id:
        return f"{section_id} {title}"
    return title or section_id or "Section"


def convert_xml_to_markdown(xml_path: Path) -> str:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    title = child_text(root, "title") or xml_path.stem
    version = child_text(root, "version")
    issue_date = child_text(root, "issue_date")
    file_number = child_text(root, "file_number")

    lines = [
        f"# {title}",
        "",
        f"- Source file: `{xml_path.name}`",
    ]
    if version:
        lines.append(f"- Version: {version}")
    if issue_date:
        lines.append(f"- Issue date: {issue_date}")
    if file_number:
        lines.append(f"- File number: {file_number}")
    lines.append("")

    def walk(node: ET.Element, depth: int = 2) -> None:
        tag = clean_tag(node.tag)
        if tag == "p":
            heading = section_heading(node)
            lines.append(f"{'#' * min(depth, 6)} {heading}")
            lines.append("")
            body = child_text(node, "text_body")
            if body:
                lines.append(body)
                lines.append("")
        elif tag == "req":
            req_id = node.attrib.get("id", "").strip() or "unlabeled"
            body = child_text(node, "text_body") or node_text(node)
            lines.append(f"## Requirement {req_id}")
            lines.append("")
            if body:
                lines.append(f"REQ-{safe_filename(xml_path.stem).upper()}-{req_id}: {body}")
                lines.append("")

        for child in node:
            if clean_tag(child.tag) in {"p", "req"}:
                walk(child, depth + (1 if tag == "p" else 0))

    for child in root:
        if clean_tag(child.tag) in {"p", "req"}:
            walk(child)

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path, help="Folder containing XML files.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("converted_dataset/requirements_markdown"),
        help="Folder for generated Markdown files.",
    )
    args = parser.parse_args()

    xml_files = sorted(args.input_dir.rglob("*.xml")) + sorted(args.input_dir.rglob("*.XML"))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for xml_path in xml_files:
        markdown = convert_xml_to_markdown(xml_path)
        output_path = args.output_dir / f"{safe_filename(xml_path.stem)}.md"
        output_path.write_text(markdown, encoding="utf-8")
        print(f"Converted {xml_path} -> {output_path}")

    print(f"Converted {len(xml_files)} XML file(s).")


if __name__ == "__main__":
    main()
