"""Register only this collection's newly created pages; preserve older content."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
COLLECTION = Path(__file__).resolve().parent
DATE = "2026-09-08"
BEGIN = "<!-- frontier-2026-09-08:start -->"
END = "<!-- frontier-2026-09-08:end -->"

def replace_block(path, body):
    text = path.read_text(encoding="utf-8-sig")
    block = f"{BEGIN}\n{body.rstrip()}\n{END}"
    if BEGIN in text:
        text = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    if text.startswith("---"):
        text = re.sub(r"^updated:.*$", f"updated: {DATE}", text, count=1, flags=re.M)
    path.write_text(text, encoding="utf-8")

def main():
    entry_lines = ["## 中文笔记直达", ""]
    for folder, label in (("wiki_array", "定位"), ("wiki", "增强")):
        groups = {}
        for kind in ("sources", "concepts", "topics"):
            groups[kind] = [p for p in sorted((ROOT/folder/kind).glob("*.md"))
                            if re.search(r"created: [\"']?2026-09-08", p.read_text(encoding="utf-8-sig"))]
        index = ["## 2026-09-08 前沿论文专题", "",
                 "> [!updated] 本次收录", "> 新增五篇论文及中文技术笔记；全文与检索说明见 [[outputs/reports/2026-09-08-frontier/README]]。", ""]
        for kind, heading in (("sources", "论文笔记"), ("concepts", "关联概念"), ("topics", "综合比较")):
            index.extend([f"### {heading}", ""])
            for p in groups[kind]:
                index.append(f"- [[{folder}/{kind}/{p.stem}]]")
            index.append("")
        replace_block(ROOT/folder/"index.md", "\n".join(index))
        log = [f"## [{DATE}] ingest | {label}前沿论文五篇", "",
               "- 依据 `CLAUDE.md`，按用户授权并行检索、下载官方全文和整理中文笔记。",
               f"- 新增 {len(groups['sources'])} 个 source、{len(groups['concepts'])} 个 concept、{len(groups['topics'])} 个 topic；更新索引。",
               "- PDF 保存于 [[outputs/reports/2026-09-08-frontier/README|本次论文包]]，原有 raw 资料未改动。",
               "- 笔记记录关键公式、图表证据、复现条件与限制；本轮没有执行模型训练或独立复现实验。", ""]
        log.extend(f"- [[{folder}/sources/{p.stem}]]" for p in groups["sources"])
        replace_block(ROOT/folder/"log.md", "\n".join(log))
        entry_lines.extend([f"### {label}", ""])
        entry_lines.extend(f"- [[{folder}/{kind}/{p.stem}]]" for kind in ("topics", "sources") for p in groups[kind])
        entry_lines.append("")
    replace_block(COLLECTION/"README.md", "\n".join(entry_lines))

if __name__ == "__main__":
    main()
