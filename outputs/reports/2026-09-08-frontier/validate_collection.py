"""Read-only checks for the September frontier literature collection."""
from pathlib import Path
import hashlib
import json
import re
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[3]
COLLECTION = Path(__file__).resolve().parent

def main():
    result = {"pdfs": [], "notes": [], "issues": []}
    for path in sorted(COLLECTION.rglob("*.pdf")):
        data = path.read_bytes()
        valid = data.startswith(b"%PDF-")
        record = {"path": str(path.relative_to(ROOT)), "bytes": len(data),
                  "pdf_header": valid, "sha256": hashlib.sha256(data).hexdigest()}
        if valid:
            try:
                reader = PdfReader(path)
                record["pages"] = len(reader.pages)
                record["all_pages_text_chars"] = [len(p.extract_text() or "") for p in reader.pages]
            except Exception as exc:
                result["issues"].append(f"PDF parse error {path.name}: {exc}")
        result["pdfs"].append(record)
        if not valid:
            result["issues"].append(f"Invalid PDF header: {path.name}")
    pages = list(ROOT.glob("wiki/**/*.md")) + list(ROOT.glob("wiki_array/**/*.md"))
    stems = {p.stem for p in pages}
    for path in sorted(pages):
        content = path.read_text(encoding="utf-8-sig")
        if not re.search(r"created: [\"']?2026-09-08", content):
            continue
        metadata = content.split("---", 2)
        problems = []
        if len(metadata) < 3:
            problems.append("Missing frontmatter")
        else:
            for key in ("title", "type", "created", "updated", "tags", "sources", "related"):
                if not re.search(rf"^{key}:", metadata[1], re.M):
                    problems.append(f"Missing {key}")
        for match in re.findall(r"\[\[([^\]]+)\]\]", content):
            target = match.split("|", 1)[0].split("#", 1)[0]
            if not target:
                continue
            if "/" not in target:
                exists = Path(target).stem in stems
            else:
                if target.startswith(ROOT.name + "/"):
                    target = target[len(ROOT.name) + 1:]
                candidate = ROOT / target
                exists = candidate.exists() or candidate.with_suffix(".md").exists()
            if not exists:
                problems.append(f"Unresolved wiki link: {match}")
        result["notes"].append({"path": str(path.relative_to(ROOT)), "chars": len(content), "issues": problems})
        result["issues"].extend(f"{path.name}: {p}" for p in problems)
    for directory, wiki in (("enhancement", "wiki"), ("localization", "wiki_array")):
        pdf_count = len(list((COLLECTION / directory).glob("*.pdf")))
        source_count = sum(n["path"].replace("\\", "/").startswith(wiki + "/sources/") for n in result["notes"])
        if pdf_count != 5:
            result["issues"].append(f"{directory}: expected 5 PDFs, got {pdf_count}")
        if source_count != 5:
            result["issues"].append(f"{wiki}: expected 5 new source notes, got {source_count}")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
