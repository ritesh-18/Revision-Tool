"""Split JS_Promises_Async_Closures_Output_Questions.md into content/docs/js-ts/practice.

One page per `## N. Section`; everything before the first section becomes the overview page.
Usage: python scripts/convert-practice.py [path-to-questions.md]
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("C:/claude-code-session-custom/JS_Promises_Async_Closures_Output_Questions.md")
FOLDER = "practice"
OUT = ROOT / "content" / "docs" / "js-ts" / FOLDER

_spec = importlib.util.spec_from_file_location("convert_book", ROOT / "scripts" / "convert-book.py")
cb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cb)
cb.BASE_URL = "/docs/js-ts"

SECTION_RE = re.compile(r"^(\d+)\.\s+(.*)$")


def main() -> None:
    text = cb.fix_mojibake(SRC.read_text(encoding="utf-8"))
    tagged = cb.classify(text.splitlines())

    overview = cb.Page(FOLDER, "index", "Practice: Promises, Async, Closures & Output Questions", None)
    pages = [overview]
    cur = overview
    anchors: dict[str, str] = {}
    slugger = cb.Slugger()

    for kind, line in tagged:
        hm = cb.HEADING_RE.match(line) if kind == "text" else None
        if not hm:
            cur.lines.append((kind, line))
            continue
        level, heading = len(hm.group(1)), hm.group(2)
        gslug = slugger.slug(heading)
        if level == 1:
            anchors[gslug] = overview.url
            continue
        sm = SECTION_RE.match(cb.plain_heading(heading)) if level == 2 else None
        if sm:
            cur = cb.Page(FOLDER, cb.page_slug(sm.group(2)), sm.group(2), None)
            pages.append(cur)
            anchors[gslug] = cur.url
            continue
        cur.lines.append(("heading", line))
        cur.headings.append((gslug, heading))

    for p in pages:
        local = cb.Slugger()
        for gslug, heading in p.headings:
            anchors[gslug] = f"{p.url}#{local.slug(heading)}"
    norm_map = {cb.norm(k): v for k, v in anchors.items()}

    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob("*"):
        if f.is_file():
            f.unlink()
    for p in pages:
        (OUT / f"{p.slug}.mdx").write_text(cb.render_page(p, anchors, norm_map), encoding="utf-8")

    # basic -> advanced, independent of the order in the source file
    order = [
        "var-let-const-hoisting-scope",
        "closures",
        "output-based-questions-general-javascript",
        "promises",
        "async-await",
        "mixed-sync-async-output-event-loop",
        "leetcode-30-days-of-javascript-all-30",
        "your-questions-reviewed-corrected",
    ]
    generated = [p.slug for p in pages[1:]]
    assert sorted(order) == sorted(generated), f"practice order out of sync: {generated}"
    meta = {"title": "Practice: Output Questions", "pages": order}

    titles = {p.slug: p.title for p in pages}
    steps = "\n".join(f"{i}. [{titles[s]}]({cb.BASE_URL}/{FOLDER}/{s})" for i, s in enumerate(order, 1))
    index = OUT / "index.mdx"
    index.write_text(
        index.read_text(encoding="utf-8").rstrip()
        + "\n\n## Suggested order (basic → advanced)\n\n"
        + "Do the sections in this order; the sidebar follows it too.\n\n"
        + steps + "\n",
        encoding="utf-8",
    )
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"wrote {len(pages)} pages: {', '.join(p.slug for p in pages)}")
    for w in cb.warnings:
        print("WARN", w)


if __name__ == "__main__":
    main()
