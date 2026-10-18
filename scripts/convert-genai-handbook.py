"""Convert the GenAI-FullStack-Handbook (Markdown) into Fumadocs MDX pages under content/docs/genai-handbook.

Usage: python scripts/convert-genai-handbook.py <path-to/GenAI-FullStack-Handbook>

WARNING: this deletes and regenerates content/docs/genai-handbook. The generated pages have since been
hand-edited (Mermaid diagrams, ➕ additions, code examples), so re-running it will discard those edits.
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Downloads" / "GenAI-FullStack-Handbook"
OUT = ROOT / "content" / "docs" / "genai-handbook"
BASE_URL = "/docs/genai-handbook"

FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
H1_RE = re.compile(r"^#\s+(.*?)\s*$")
CHAPTER_RE = re.compile(r"^Chapter\s+(\d+)\s*[—–-]\s*(.*)$")
PART_RE = re.compile(r"^Part(\d+)-(.*)$")
MD_LINK_RE = re.compile(r"\]\(([^)\s]+?\.md)(#[^)]*)?\)")


def slug_of(md: Path) -> str:
    return md.stem.lower()


def escape_prose(line: str) -> str:
    """Escape MDX-significant characters outside inline code spans."""
    parts = re.split(r"(`+[^`]*`+)", line)
    for i, p in enumerate(parts):
        if i % 2 == 0:
            p = p.replace("{", "\\{").replace("}", "\\}")
            p = re.sub(r"<(?!https?://)", "&lt;", p)
            parts[i] = p
    return "".join(parts)


def fix_links(line: str) -> str:
    def repl(m: re.Match) -> str:
        return f"]({BASE_URL}/{Path(m.group(1)).stem.lower()}{m.group(2) or ''})"
    return MD_LINK_RE.sub(repl, line)


def convert_body(lines: list[str]) -> list[str]:
    out, fence = [], None
    for line in lines:
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(2)
                lang = m.group(3).strip() or "text"   # ASCII diagrams
                out.append(f"{m.group(1)}{fence}{lang}")
            else:
                out.append(fix_links(escape_prose(line)))
        else:
            out.append(line)
            if m and m.group(2).startswith(fence[0] * len(fence)) and not m.group(3).strip():
                fence = None
    return out


def first_paragraph(lines: list[str]) -> str:
    buf: list[str] = []
    for line in lines:
        s = line.strip()
        if s.startswith(("#", "```", "|", "-", "*", ">")) or not s:
            if buf:
                break
            continue
        buf.append(s)
    text = re.sub(r"[*_`]", "", " ".join(buf))
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    if len(text) > 160:
        text = text[:157].rsplit(" ", 1)[0] + "..."
    return text


def fm(title: str, description: str) -> str:
    return f"---\ntitle: {json.dumps(title, ensure_ascii=False)}\ndescription: {json.dumps(description, ensure_ascii=False)}\n---\n\n"


def main() -> None:
    if not SRC.is_dir():
        sys.exit(f"source folder not found: {SRC}")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    pages: list[str] = ["index"]
    toc: list[tuple[str, list[tuple[str, str, str]]]] = []

    for part_dir in sorted((p for p in SRC.iterdir() if p.is_dir() and PART_RE.match(p.name)),
                           key=lambda p: int(PART_RE.match(p.name).group(1))):
        num, name = PART_RE.match(part_dir.name).groups()
        part_title = f"Part {num}: {name.replace('-', ' ')}"
        pages.append(f"---{part_title}---")
        entries = []
        for md in sorted(part_dir.glob("*.md")):
            lines = md.read_text(encoding="utf-8").splitlines()
            title, body = md.stem, lines
            for i, line in enumerate(lines):
                h1 = H1_RE.match(line)
                if h1:
                    raw = h1.group(1)
                    c = CHAPTER_RE.match(raw)
                    title = f"{c.group(1)}. {c.group(2)}" if c else raw
                    body = lines[i + 1:]
                    break
            desc = first_paragraph(body) or title
            slug = slug_of(md)
            (OUT / f"{slug}.mdx").write_text(fm(title, desc) + "\n".join(convert_body(body)).strip() + "\n", encoding="utf-8")
            pages.append(slug)
            entries.append((slug, title, desc))
        toc.append((part_title, entries))

    # index from README (intro up to the table of contents) + generated chapter tables
    readme = (SRC / "README.md").read_text(encoding="utf-8").splitlines()
    intro: list[str] = []
    for line in readme[1:]:
        if line.strip().lower().startswith("## table of contents"):
            break
        intro.append(line)
    idx = [fm("GenAI Full Stack Handbook", "Building, deploying and operating production Generative AI systems, from foundations to career.")]
    idx += convert_body(intro)
    idx.append("\n## Table of contents\n")
    for part_title, entries in toc:
        idx.append(f"### {part_title}\n")
        idx.append("| Chapter | What it covers |\n|---|---|")
        for slug, title, desc in entries:
            idx.append(f"| [{title}]({BASE_URL}/{slug}) | {escape_prose(desc).replace('|', '/')} |")
        idx.append("")
    (OUT / "index.mdx").write_text("\n".join(idx).strip() + "\n", encoding="utf-8")

    meta = {"title": "GenAI Full Stack Handbook", "description": "Production Generative AI engineering",
            "root": True, "icon": "Sparkles", "pages": pages}
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(pages) - 1 - len(toc)} chapters in {len(toc)} parts to {OUT}")


if __name__ == "__main__":
    main()
