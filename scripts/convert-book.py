"""Split TypeScript_LLD_Book.md into Fumadocs MDX pages under content/docs/lld.

Usage: python scripts/convert-book.py [path-to-book.md]
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Downloads" / "TypeScript_LLD_Book.md"
OUT = ROOT / "content" / "docs" / "lld"
BASE_URL = "/docs/lld"

FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
CHAPTER_RE = re.compile(r"^(\d+)\.\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.(\d+)\s+(.*)$")
ALLOWED_TAGS = r"(?:details|summary|br|sup|sub|kbd|b|i|em|strong|u|s|mark|small)"

PART_BEFORE = {
    2: "I. Foundations",
    4: "II. Patterns",
    8: "III. Method",
    9: "IV. Case Studies",
    15: "V. Frontend",
    16: "VI. Practice",
}

warnings: list[str] = []


# ---------------------------------------------------------------- mojibake ---
MOJI_RE = re.compile(
    "[Â-ô][\u0080-¿ŒœŠšŸŽž"
    "ƒˆ˜–—‘-„†-•…‰‹"
    "›€™]{1,3}"
)


def _to_byte(ch: str) -> int:
    if ord(ch) < 256:
        return ord(ch)
    return ch.encode("cp1252")[0]


def fix_mojibake(text: str) -> str:
    def repl(m: re.Match) -> str:
        s = m.group(0)
        for end in range(len(s), 1, -1):
            try:
                fixed = bytes(_to_byte(c) for c in s[:end]).decode("utf-8")
                return fixed + s[end:]
            except (UnicodeDecodeError, UnicodeEncodeError):
                continue
        return s

    return MOJI_RE.sub(repl, text)


# ------------------------------------------------------------------ slugs ----
def plain_heading(text: str) -> str:
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return text.replace("`", "").replace("**", "").replace("__", "").strip()


def github_slug(text: str) -> str:
    s = plain_heading(text).lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def page_slug(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", plain_heading(title).lower()).strip("-")
    if len(s) > 50:
        s = s[:50].rsplit("-", 1)[0]
    return s or "page"


class Slugger:
    def __init__(self) -> None:
        self.seen: dict[str, int] = {}

    def slug(self, text: str) -> str:
        base = github_slug(text)
        n = self.seen.get(base, 0)
        self.seen[base] = n + 1
        return base if n == 0 else f"{base}-{n}"


def norm(anchor: str) -> str:
    return re.sub(r"[^a-z0-9]", "", anchor.lower())


# ------------------------------------------------------------ parse lines ----
def classify(lines: list[str]) -> list[tuple[str, str]]:
    """Tag each line as 'code' or 'text' (fence lines are 'code')."""
    out = []
    fence = None
    for line in lines:
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(2)[0] * len(m.group(2))
                out.append(("code", line))
            else:
                out.append(("text", line))
        else:
            out.append(("code", line))
            if m and m.group(2).startswith(fence) and not m.group(3).strip():
                fence = None
    return out


# ----------------------------------------------------------- page model ------
class Page:
    def __init__(self, folder: str, slug: str, title: str, heading_shift: int | None):
        self.folder = folder  # "" for lld root
        self.slug = slug
        self.title = title
        self.shift = heading_shift  # None => auto (min level -> 2)
        self.lines: list[tuple[str, str]] = []
        self.headings: list[tuple[str, str]] = []  # (global slug, heading text)

    @property
    def url(self) -> str:
        parts = [BASE_URL] + ([self.folder] if self.folder else [])
        if self.slug != "index":
            parts.append(self.slug)
        return "/".join(parts)


def build_pages(tagged: list[tuple[str, str]]):
    pages: list[Page] = []
    chapters: list[dict] = []
    anchor_map: dict[str, str] = {}
    global_slugger = Slugger()

    root = Page("", "index", "LLD in TypeScript — from Basics to SDE-2", None)
    pages.append(root)
    cur = root
    chapter = None
    skip_title_line = False

    for kind, line in tagged:
        hm = HEADING_RE.match(line) if kind == "text" else None
        if not hm:
            cur.lines.append((kind, line))
            continue

        level, text = len(hm.group(1)), hm.group(2)
        gslug = global_slugger.slug(text)
        ptext = plain_heading(text)

        if level == 1 and cur is root and not root.lines:
            anchor_map[gslug] = root.url
            continue  # book title -> frontmatter

        cm = CHAPTER_RE.match(ptext)
        if level == 2 and cm:
            num = int(cm.group(1))
            title = ptext
            if num == 1:
                folder = ""
                cur = Page("", "how-to-use", title, None)
                chapter = {"num": 1, "folder": "", "title": title, "pages": [cur]}
            else:
                folder = f"{num:02d}-{page_slug(cm.group(2))}"
                cur = Page(folder, "index", title, None)
                chapter = {"num": num, "folder": folder, "title": title, "pages": [cur]}
            chapters.append(chapter)
            pages.append(cur)
            anchor_map[gslug] = cur.url
            continue

        if level == 2 and ptext.lower().startswith("table of contents"):
            cur = root
            cur.lines.append(("text", "## Full table of contents"))
            anchor_map[gslug] = root.url + "#full-table-of-contents"
            continue

        if chapter and chapter["num"] > 1:
            is_section = level == 3 and (SECTION_RE.match(ptext) or ptext.lower().startswith("domain primer"))
            if is_section:
                cur = Page(chapter["folder"], page_slug(SECTION_RE.sub(r"\3", ptext)), ptext, -1)
                chapter["pages"].append(cur)
                pages.append(cur)
                anchor_map[gslug] = cur.url
                continue
            # unnumbered heading after sections => recap page
            if len(chapter["pages"]) > 1 and not chapter.get("recap") and level <= 3:
                cur = Page(chapter["folder"], "recap-and-practice", "Chapter recap & practice", None)
                chapter["recap"] = cur
                chapter["pages"].append(cur)
                pages.append(cur)
            elif chapter.get("recap") and cur is not chapter["recap"] and level <= 3:
                cur = chapter["recap"]

        cur.lines.append(("heading", line))
        cur.headings.append((gslug, text))

    # compute local heading slugs per page (in order) for the anchor map
    for p in pages:
        s = Slugger()
        for gslug, text in p.headings:
            anchor_map[gslug] = f"{p.url}#{s.slug(text)}"

    return pages, chapters, anchor_map


# -------------------------------------------------------- text transforms ----
INLINE_CODE_RE = re.compile(r"(`+)(.+?)\1")


def escape_prose(segment: str) -> str:
    segment = segment.replace("{", "\\{").replace("}", "\\}")
    out = []
    i = 0
    tag_re = re.compile(rf"</?{ALLOWED_TAGS}(\s[^<>]*)?/?>", re.I)
    while i < len(segment):
        ch = segment[i]
        if ch == "<":
            auto = re.match(r"<(https?://[^>\s]+)>", segment[i:])
            if auto:
                out.append(f"[{auto.group(1)}]({auto.group(1)})")
                i += auto.end()
                continue
            tm = tag_re.match(segment, i)
            if tm:
                tag = tm.group(0)
                if re.fullmatch(r"<br\s*>", tag, re.I):
                    tag = "<br />"
                out.append(tag)
                i = tm.end()
                continue
            out.append("&lt;")
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def rewrite_links(segment: str, anchor_map: dict[str, str], norm_map: dict[str, str], where: str) -> str:
    def repl(m: re.Match) -> str:
        anchor = m.group(1)
        target = anchor_map.get(anchor) or norm_map.get(norm(anchor))
        if not target:
            warnings.append(f"unresolved link #{anchor} in {where}")
            return m.group(0)
        return f"]({target})"

    return re.sub(r"\]\(#([^)\s]+)\)", repl, segment)


def transform_text_line(line: str, anchor_map, norm_map, where: str) -> str:
    line = re.sub(r"<!--.*?-->", "", line)
    is_table_row = line.lstrip().startswith("|")
    parts = []
    last = 0
    for m in INLINE_CODE_RE.finditer(line):
        parts.append(escape_prose(line[last:m.start()]))
        code = m.group(0)
        if is_table_row:
            # GFM splits cells on `|` even inside code spans
            code = re.sub(r"(?<!\\)\|", r"\\|", code)
        parts.append(code)
        last = m.end()
    parts.append(escape_prose(line[last:]))
    out = "".join(parts)
    out = rewrite_links(out, anchor_map, norm_map, where)
    if re.match(r"^\s*(import|export)\s", out):
        out = out.replace("import", "&#105;mport", 1).replace("export", "&#101;xport", 1)
    return out


def split_details(line: str) -> list[str]:
    """Put <details>/<summary>/</details> on their own lines so MDX parses them as blocks."""
    if "<details" not in line and "</details>" not in line:
        return [line]
    s = re.sub(r"(<details[^>]*>)", r"\n\1\n", line)
    s = re.sub(r"(<summary>.*?</summary>)", r"\n\1\n", s)
    s = s.replace("</details>", "\n</details>\n")
    pieces = [p.strip() for p in s.split("\n")]
    out = []
    for p in pieces:
        if not p:
            continue
        out.append(p)
    # blank line after summary / before closing so the markdown inside is parsed
    res = []
    for p in out:
        if p == "</details>":
            res.append("")
        res.append(p)
        if p.startswith("<summary>") or p == "</details>":
            res.append("")
    return res


def render_page(p: Page, anchor_map, norm_map) -> str:
    # heading shift
    levels = [len(HEADING_RE.match(l).group(1)) for k, l in p.lines if k == "heading"]
    if p.shift is None:
        shift = (2 - min(levels)) if levels else 0
    else:
        shift = 2 - 4  # #### -> ##
        if levels and min(levels) + shift < 2:
            shift = 2 - min(levels)
    body: list[str] = []
    mermaid: list[str] | None = None
    for kind, line in p.lines:
        if kind == "code":
            fm = FENCE_RE.match(line)
            if mermaid is not None:
                if fm and not fm.group(3).strip():
                    if mermaid and mermaid[0].strip().startswith("sequenceDiagram"):
                        # `;` ends a statement in sequence diagrams; escape it inside message text
                        mermaid = [re.sub(r"^([^:]*:)(.*)$", lambda m: m.group(1) + m.group(2).replace(";", "#59;"), l)
                                   for l in mermaid]
                    chart = "\n".join(mermaid).replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
                    body.append("<Mermaid chart={`" + chart + "`} />")
                    mermaid = None
                else:
                    mermaid.append(line)
                continue
            if fm and fm.group(3).strip().startswith("mermaid"):
                mermaid = []
                continue
            body.append(line)
        elif kind == "heading":
            m = HEADING_RE.match(line)
            lvl = max(2, min(6, len(m.group(1)) + shift))
            body.append("#" * lvl + " " + transform_text_line(m.group(2), anchor_map, norm_map, p.url))
        else:
            for piece in split_details(line):
                body.append(transform_text_line(piece, anchor_map, norm_map, p.url))

    # trim leading/trailing blank lines and horizontal rules
    while body and body[0].strip() in ("", "---"):
        body.pop(0)
    while body and body[-1].strip() in ("", "---"):
        body.pop()
    text = "\n".join(body)
    text = re.sub(r"\n{3,}", "\n\n", text)
    fm = f"---\ntitle: {json.dumps(p.title, ensure_ascii=False)}\n---\n\n"
    return fm + text + "\n"


def main() -> None:
    raw = SRC.read_text(encoding="utf-8")
    fixed = fix_mojibake(raw)
    left = len(re.findall("â€|Ã", fixed))
    print(f"mojibake runs remaining: {left}")
    lines = fixed.splitlines()

    tagged = classify(lines)
    pages, chapters, anchor_map = build_pages(tagged)
    norm_map = {norm(k): v for k, v in anchor_map.items()}

    # delete generated files, then folders best-effort (Windows can lock open directories)
    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.rglob("*"):
        if f.is_file():
            f.unlink()
    for d in sorted((p for p in OUT.rglob("*") if p.is_dir()), reverse=True):
        shutil.rmtree(d, ignore_errors=True)

    for p in pages:
        d = OUT / p.folder if p.folder else OUT
        d.mkdir(parents=True, exist_ok=True)
        path = d / f"{p.slug}.mdx"
        if path.exists():
            warnings.append(f"duplicate page slug {path}")
        path.write_text(render_page(p, anchor_map, norm_map), encoding="utf-8")

    root_pages = ["index", "how-to-use"]
    for ch in chapters:
        if ch["num"] == 1:
            continue
        if ch["num"] in PART_BEFORE:
            root_pages.append(f"---{PART_BEFORE[ch['num']]}---")
        root_pages.append(ch["folder"])
        meta = {
            "title": ch["title"],
            "pages": [pg.slug for pg in ch["pages"] if pg.slug != "index"],
        }
        (OUT / ch["folder"] / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    root_meta = {
        "title": "LLD in TypeScript",
        "description": "Basics to SDE-2 design book",
        "root": True,
        "icon": "BookOpen",
        "pages": root_pages,
    }
    (OUT / "meta.json").write_text(json.dumps(root_meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"pages written: {len(pages)} in {len(chapters)} chapters")
    for w in warnings:
        print("WARN", w)


if __name__ == "__main__":
    main()
