"""Build content/docs/js-ts/typescript (TS guide §25–42) and content/docs/js-ts/interview-questions.

Sources live in notes-source/: tsfile.md (the revision guide) and interview/*.md (answered questions).
Usage: python scripts/convert-ts-guide.py
"""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "notes-source" / "tsfile.md"
ANSWERS = ROOT / "notes-source" / "interview"
DOCS = ROOT / "content" / "docs" / "js-ts"

_spec = importlib.util.spec_from_file_location("convert_book", ROOT / "scripts" / "convert-book.py")
cb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cb)

SECTION_RE = re.compile(r"^##\s+(\d+)\.\s+(.*)$")

# Basic -> advanced: (group, [(slug, title, description, [guide section numbers])])
TS_GROUPS = [
    ("Basics", [
        ("what-is-typescript", "What is TypeScript, Basic Types & Inference",
         "Why TS, primitives, arrays, tuples, any vs unknown, void, never, and when to annotate.", [25, 26, 27]),
        ("interfaces-vs-type-aliases", "Interfaces vs Type Aliases",
         "Extending, declaration merging, and when to pick which.", [28]),
        ("unions-intersections-literals", "Unions, Intersections & Literal Types",
         "Discriminated unions, intersections, literal and template literal types.", [29, 30]),
        ("enums", "Enums", "Numeric, string and const enums, and the as const alternative.", [31]),
        ("functions", "Functions in TypeScript", "Parameter and return types, optional/default params, overloads.", [32]),
    ]),
    ("Intermediate", [
        ("generics", "Generics", "Generic functions, constraints, generic interfaces/classes and defaults.", [33]),
        ("utility-types", "Utility Types", "Partial, Required, Pick, Omit, Record, ReturnType and friends.", [34]),
        ("narrowing-and-type-guards", "Type Narrowing & Type Guards",
         "typeof, instanceof, in, discriminants, custom guards and assertion functions.", [35]),
        ("classes", "Classes in TypeScript", "Access modifiers, parameter properties, abstract classes, implements.", [36]),
    ]),
    ("Tooling", [
        ("modules-and-declaration-files", "Modules, Namespaces & Declaration Files",
         "ES modules in TS, why namespaces are legacy, and writing .d.ts files.", [38, 39]),
        ("tsconfig", "tsconfig.json Deep Dive", "The compiler options that matter and what strict turns on.", [40]),
    ]),
    ("Advanced", [
        ("decorators", "Decorators", "Class, method, property and parameter decorators.", [37]),
        ("advanced-types", "Advanced Types", "Conditional types, infer, mapped types, key remapping and recursive types.", [41]),
        ("nestjs-patterns", "TypeScript with Node.js / NestJS", "DTOs, DI, typed configs and other NestJS patterns.", [42]),
    ]),
]

# (slug, title, description, source file)
QUESTION_PAGES = [
    ("js-fundamentals", "JavaScript — Fundamentals (Q1–Q20)",
     "var/let/const, TDZ, hoisting, coercion, equality, functions and currying.", "js-fundamentals.md"),
    ("js-core-concepts-1", "JavaScript — Core Concepts (Q21–Q40)",
     "Scope chain, closures, this, prototypes, classes and arrays.", "js-core.md"),
    ("js-core-concepts-2", "JavaScript — Core & Advanced (Q41–Q60)",
     "Async, event loop, modules, Map/Set, symbols, Proxy and memory.", "js-core-2.md"),
    ("ts-fundamentals", "TypeScript — Fundamentals (Q61–Q80)",
     "Types, interfaces, unions, generics, utility types, conditional and mapped types.", "ts-fundamentals.md"),
    ("ts-advanced", "TypeScript — Advanced (Q81–Q100)",
     "Decorators, strictness, guards, infer, satisfies, declaration merging and more.", "ts-advanced.md"),
]


def frontmatter(title: str, desc: str) -> str:
    return f"---\ntitle: {json.dumps(title, ensure_ascii=False)}\ndescription: {json.dumps(desc, ensure_ascii=False)}\n---\n\n"


def to_mdx(lines: list[str], where: str) -> str:
    out = []
    for kind, line in cb.classify(lines):
        if kind == "code":
            out.append(line)
            continue
        for piece in cb.split_details(line):
            out.append(cb.transform_text_line(piece, {}, {}, where))
    while out and out[-1].strip() in ("", "---"):
        out.pop()
    while out and out[0].strip() in ("", "---"):
        out.pop(0)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


def guide_sections() -> dict[int, tuple[str, list[str]]]:
    """Map section number -> (title, body lines) for the numbered `## N.` sections."""
    sections: dict[int, tuple[str, list[str]]] = {}
    current = None
    for kind, line in cb.classify(cb.fix_mojibake(SRC.read_text(encoding="utf-8")).splitlines()):
        m = SECTION_RE.match(line) if kind == "text" else None
        if m:
            current = int(m.group(1))
            sections[current] = (m.group(2).strip(), [])
            continue
        if kind == "text" and line.startswith("# "):
            current = None  # PART headings end the previous section
            continue
        if current is not None:
            sections[current][1].append(line)
    return sections


def build_typescript() -> None:
    sections = guide_sections()
    out = DOCS / "typescript"
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.mdx"):
        f.unlink()

    meta_pages = ["index"]
    cards = []
    for group, pages in TS_GROUPS:
        meta_pages.append(f"---{group}---")
        cards += [f"## {group}", "", "<Cards>"]
        for slug, title, desc, nums in pages:
            body: list[str] = []
            for n in nums:
                sec_title, lines = sections[n]
                if len(nums) > 1:
                    body += [f"## {sec_title}", ""]
                body += lines
            (out / f"{slug}.mdx").write_text(frontmatter(title, desc) + to_mdx(body, slug), encoding="utf-8")
            meta_pages.append(slug)
            cards.append(f'  <Card title={json.dumps(title)} href="/docs/js-ts/typescript/{slug}" description={json.dumps(desc)} />')
        cards += ["</Cards>", ""]

    meta_pages += ["---Apply it---", "[TypeScript for LLD (book §2)](/docs/lld/02-typescript-essentials-for-lld)"]
    index = frontmatter("TypeScript", "TypeScript from basic types to conditional types and NestJS patterns.") + "\n".join([
        "Read these after the JavaScript sections: TypeScript is JavaScript plus a type system, so every JS rule still applies.",
        "The pages go from basics to advanced; test yourself with the "
        "[TypeScript interview questions](/docs/js-ts/interview-questions/ts-fundamentals) afterwards.",
        "",
        *cards,
        "## Apply it",
        "",
        "<Cards>",
        '  <Card title="TypeScript Essentials for LLD" href="/docs/lld/02-typescript-essentials-for-lld" '
        'description="Branded types, private vs #private, discriminated unions for state machines, money modelling." />',
        "</Cards>",
        "",
    ])
    (out / "index.mdx").write_text(index, encoding="utf-8")
    meta = {"title": "TypeScript", "pages": meta_pages}
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"typescript: {sum(len(p) for _, p in TS_GROUPS)} pages")


def build_questions() -> None:
    out = DOCS / "interview-questions"
    missing = [src for *_, src in QUESTION_PAGES if not (ANSWERS / src).exists()]
    if missing:
        print(f"interview-questions: skipped, missing answers {missing}")
        return
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.mdx"):
        f.unlink()

    cards = []
    for slug, title, desc, src in QUESTION_PAGES:
        lines = (ANSWERS / src).read_text(encoding="utf-8").splitlines()
        intro = "Try answering out loud before expanding each answer.\n\n"
        (out / f"{slug}.mdx").write_text(frontmatter(title, desc) + intro + to_mdx(lines, slug), encoding="utf-8")
        cards.append(f'  <Card title={json.dumps(title)} href="/docs/js-ts/interview-questions/{slug}" description={json.dumps(desc)} />')

    index = frontmatter(
        "100 Interview Questions (JS & TS)",
        "Theory and coding questions from JavaScript fundamentals to advanced TypeScript, each with a hidden answer.",
    ) + "\n".join([
        "Go in order: JavaScript fundamentals first, TypeScript advanced last. Answer each question yourself, "
        "then expand the answer to compare.",
        "",
        "<Cards>",
        *cards,
        "</Cards>",
        "",
    ])
    (out / "index.mdx").write_text(index, encoding="utf-8")
    meta = {"title": "100 Interview Questions", "pages": [s for s, *_ in QUESTION_PAGES]}
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"interview-questions: {len(QUESTION_PAGES)} pages")


if __name__ == "__main__":
    build_typescript()
    build_questions()
    for w in cb.warnings:
        print("WARN", w)
