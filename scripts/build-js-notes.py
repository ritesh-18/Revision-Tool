"""Build the "JS & TS" notes section (content/docs/js-ts) from transcribed notebook Markdown.

PAGES maps each topic page to slices of transcript files (file, first line, last line).
SECTIONS orders those pages from basic to advanced; it drives both the sidebar (meta.json)
and the section index page. Usage: python scripts/build-js-notes.py <transcripts-dir>
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = Path(sys.argv[1])
OUT = ROOT / "content" / "docs" / "js-ts"

_spec = importlib.util.spec_from_file_location("convert_book", ROOT / "scripts" / "convert-book.py")
cb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cb)

P1, P2, P3, P4 = "js-notes-part1.md", "js-notes-part2.md", "js-notes-part3.md", "js-notes-part4.md"
END = 99999

# slug -> (title, description, [(file, start_line, end_line)])
PAGES = {
    "introduction-and-variables": ("Introduction & Variables",
        "What JS is, runtimes, let/var/const and naming rules.", [(P1, 3, 57)]),
    "datatypes-and-operators": ("Datatypes & Operators",
        "Primitive types, arithmetic/assignment/logical operators, short circuiting, truthy & falsy.", [(P1, 58, 219)]),
    "comparison-and-decisions": ("Comparison, Comments & Decisions",
        "== vs ===, comments, if / else and nesting.", [(P1, 220, 339)]),
    "loops": ("Loops, Unary Operators, break & continue",
        "while, for, do-while, ++/--, break and continue.", [(P1, 443, 546)]),
    "console-date-strings-arrays": ("Console, Date, Strings & Arrays",
        "Built-in objects and their everyday methods.", [(P1, 704, 830)]),
    "bitwise-operators": ("Bitwise Operators",
        "AND, OR, XOR, NOT and shifts, worked in binary.", [(P1, 340, 442)]),
    "functions": ("Functions & the Call Stack",
        "Parameters vs arguments, call stack, defaults, rest parameters, Math helpers.", [(P1, 547, 703)]),
    "scopes": ("Scopes & the Two Phases of Execution",
        "Compiled vs interpreted, scope resolution, var and auto globals.", [(P1, 831, END), (P2, 1, 72)]),
    "let-const-hoisting": ("let / const, TDZ & Hoisting",
        "Block scope, the temporal dead zone and hoisting.", [(P2, 73, 138)]),
    "function-expressions": ("Function Expressions, Arrow Functions & IIFE",
        "Named vs anonymous expressions, arrow-function rules and IIFEs.", [(P2, 139, 252)]),
    "type-coercion": ("Type Coercion & Equality",
        "Implicit vs explicit conversion, abstract operations, the + operator, == vs ===.", [(P2, 938, END), (P3, 1, 105)]),
    "explicit-conversion-and-autoboxing": ("Explicit Conversion & Autoboxing",
        "Number()/String(), isNaN vs Number.isNaN, detecting -0, autoboxing.", [(P3, 260, 335)]),
    "to-primitive": ("ToPrimitive, Objects in Operators & Comparisons",
        "OrdinaryToPrimitive, valueOf/toString, weird operator results, template literals, unary + and !!.", [(P3, 106, 259)]),
    "destructuring-and-rest": ("Destructuring, Rest & Spread",
        "Object destructuring, aliases, defaults, rest and spread.", [(P2, 604, 693)]),
    "objects-and-immutability": ("Object Methods & Immutability",
        "Object.keys/values/entries, const objects, seal, freeze, preventExtensions, defineProperty.", [(P4, 505, END)]),
    "classes-and-this": ("Classes, Constructors & this",
        "Classes, how new works, the this keyword and encapsulation.", [(P2, 253, 497)]),
    "function-constructors-static-builder": ("Function Constructors, Static & Builder",
        "Class as a wrapper on functions, static members and the Builder pattern.", [(P2, 498, 603)]),
    "prototypes-and-inheritance": ("Prototypes, Inheritance & call/apply/bind",
        "Prototype chain, extends, call/apply/bind and inheritance without classes.", [(P2, 694, 937)]),
    "callbacks-and-async": ("Callbacks, Async JS & Closures",
        "Callback hell, inversion of control, single-threaded JS, the event loop and closures.", [(P3, 336, 504)]),
    "promises": ("Promises & the Event Loop",
        "Creating and consuming promises, states, microtask vs macrotask queues, Promise.resolve/reject.",
        [(P3, 505, END), (P4, 1, 34)]),
    "async-await": ("async / await",
        "How await suspends and resumes, chaining, Promise.all / any / allSettled.", [(P4, 35, 203)]),
    "error-handling": ("Error Handling",
        "throw, try/catch, errors with promises, finally and error-first callbacks.", [(P4, 204, 282)]),
    "generators-and-iterators": ("Generators & Iterators",
        "Iterator protocol, Symbol.iterator, function*, yield, and generators driving promises.", [(P4, 283, 504)]),
}

# Basic -> advanced. Each entry: (group title, level blurb, [page slugs])
SECTIONS = [
    ("1. Basics", "Start here: syntax, types, operators and control flow.",
     ["introduction-and-variables", "datatypes-and-operators", "comparison-and-decisions", "loops",
      "console-date-strings-arrays", "bitwise-operators"]),
    ("2. Functions & Scope", "How functions run, where variables live, and hoisting.",
     ["functions", "scopes", "let-const-hoisting", "function-expressions"]),
    ("3. Types & Coercion", "What JS does when types don't match — the source of most output questions.",
     ["type-coercion", "explicit-conversion-and-autoboxing", "to-primitive"]),
    ("4. Objects & OOP", "Objects first, then classes, this, and the prototype machinery underneath.",
     ["destructuring-and-rest", "objects-and-immutability", "classes-and-this",
      "function-constructors-static-builder", "prototypes-and-inheritance"]),
    ("5. Async JavaScript", "Callbacks to promises to async/await, then generators.",
     ["callbacks-and-async", "promises", "async-await", "error-handling", "generators-and-iterators"]),
]

PAGE_COMMENT_RE = re.compile(r"^<!--\s*page\s+(\d+)\s*-->\s*$")


def slice_lines(file: str, start: int, end: int) -> list[str]:
    lines = (SRC_DIR / file).read_text(encoding="utf-8").splitlines()
    return lines[start - 1:end]


def render(title: str, desc: str, chunks: list[tuple[str, int, int]]) -> str:
    raw: list[str] = []
    for file, start, end in chunks:
        notebook = "notebook 1" if file in (P1, P2) else "notebook 2"
        for line in slice_lines(file, start, end):
            m = PAGE_COMMENT_RE.match(line)
            if m:
                raw.append(f"{{/* {notebook}, page {m.group(1)} */}}")
                continue
            if line.startswith("# "):
                continue  # notebook title
            raw.append(line)

    out: list[str] = []
    seen_headings: set[str] = set()
    for kind, line in cb.classify(raw):
        if kind == "code" or line.startswith("{/*"):
            out.append(line)
            continue
        hm = cb.HEADING_RE.match(line)
        if hm:
            text = re.sub(r"^\(continued\)\s*|\s*\(continued\)$", "", hm.group(2))
            if text != hm.group(2) and text in seen_headings:
                continue  # "(continued) X" when X already started on this page
            seen_headings.add(text)
            line = f"{hm.group(1)} {text}"
        for piece in cb.split_details(line):
            out.append(cb.transform_text_line(piece, {}, {}, title))

    body = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()
    fm = f"---\ntitle: {json.dumps(title, ensure_ascii=False)}\ndescription: {json.dumps(desc, ensure_ascii=False)}\n---\n\n"
    return fm + body + "\n"


def render_index() -> str:
    parts = [
        "---",
        "title: JS & TS Notes",
        "description: JavaScript topics from my notebooks, ordered from basics to advanced, plus a practice bank.",
        "---",
        "",
        "Work through the sections in order: each one builds on the previous. Code was rewritten as valid "
        "JavaScript where the handwriting was shorthand; unclear spots are marked *[illegible]* or with a short note.",
        "",
    ]
    for group, blurb, slugs in SECTIONS:
        parts += [f"## {group}", "", blurb, "", "<Cards>"]
        for slug in slugs:
            title, desc, _ = PAGES[slug]
            parts.append(f'  <Card title={json.dumps(title)} href="/docs/js-ts/{slug}" description={json.dumps(desc)} />')
        parts += ["</Cards>", ""]
    parts += [
        "## 6. TypeScript",
        "",
        "JavaScript plus a type system: basic types up to conditional types, decorators and NestJS patterns.",
        "",
        "<Cards>",
        '  <Card title="TypeScript" href="/docs/js-ts/typescript" '
        'description="14 pages: basics → generics, utility types, narrowing, classes → tsconfig → advanced types and NestJS." />',
        '  <Card title="TypeScript Essentials for LLD" href="/docs/lld/02-typescript-essentials-for-lld" '
        'description="How TypeScript is used in design rounds: branded types, discriminated unions, money modelling." />',
        "</Cards>",
        "",
        "## 7. Practice",
        "",
        "Test yourself once the topics above are done.",
        "",
        "<Cards>",
        '  <Card title="100 Interview Questions (JS & TS)" href="/docs/js-ts/interview-questions" '
        'description="Theory and coding questions from JS fundamentals to advanced TypeScript, each with a hidden answer." />',
        '  <Card title="Practice: Output Questions" href="/docs/js-ts/practice" '
        'description="350 questions, from hoisting and closures up to event-loop puzzles and LeetCode 30 Days of JS. Answers stay hidden until expanded." />',
        "</Cards>",
        "",
    ]
    return "\n".join(parts)


def main() -> None:
    listed = [s for _, _, slugs in SECTIONS for s in slugs]
    assert sorted(listed) == sorted(PAGES), "every page must appear exactly once in SECTIONS"

    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob("*.mdx"):
        f.unlink()

    meta_pages = ["index"]
    for group, _, slugs in SECTIONS:
        meta_pages.append(f"---{group}---")
        for slug in slugs:
            title, desc, chunks = PAGES[slug]
            (OUT / f"{slug}.mdx").write_text(render(title, desc, chunks), encoding="utf-8")
            meta_pages.append(slug)
    meta_pages += [
        "---6. TypeScript---",
        "typescript",  # generated by convert-ts-guide.py
        "---7. Practice---",
        "interview-questions",  # generated by convert-ts-guide.py
        "practice",  # generated by convert-practice.py
    ]
    (OUT / "index.mdx").write_text(render_index(), encoding="utf-8")

    meta = {
        "title": "JS & TS",
        "description": "Basics to advanced JavaScript notes",
        "root": True,
        "icon": "FileCode",
        "pages": meta_pages,
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(PAGES)} pages")
    for w in cb.warnings:
        print("WARN", w)


if __name__ == "__main__":
    main()
