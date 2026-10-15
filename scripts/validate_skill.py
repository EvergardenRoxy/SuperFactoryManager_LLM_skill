#!/usr/bin/env python3
"""Validate the SFM skill.

1. Parses every ```sfml / ```sfml-snippet code block in skills/**/*.md with a
   parser generated from the official SFML.g4 grammar (TeamDman/SuperFactoryManager).
   `sfml` blocks must be whole programs; `sfml-snippet` blocks are statements and
   are wrapped in `every 20 ticks do ... end` before parsing.
2. Checks SKILL.md structure: front matter, line budget, and that every
   `references/*.md` it mentions exists.

Requirements: Java 11+, Python 3.8+, network access on first run.
Downloads are cached in .cache/ (git-ignored).

Usage:
    python3 scripts/validate_skill.py [--ref <git ref of SuperFactoryManager>]
"""
import argparse
import pathlib
import re
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
SKILLS = ROOT / "skills"
ANTLR_VERSION = "4.13.2"
ANTLR_JAR_URL = f"https://repo1.maven.org/maven2/org/antlr/antlr4/{ANTLR_VERSION}/antlr4-{ANTLR_VERSION}-complete.jar"
GRAMMAR_URL = "https://raw.githubusercontent.com/TeamDman/SuperFactoryManager/{ref}/platform/minecraft/src/main/antlr/sfml/SFML.g4"
MAX_SKILL_LINES = 500

BLOCK_RE = re.compile(r"^```(sfml(?:-snippet)?)\n(.*?)^```", re.S | re.M)


def download(url, dest):
    if not dest.exists():
        print(f"downloading {url}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "sfm-skill-validator/1.0"})
        tmp = dest.with_suffix(dest.suffix + ".part")
        with urllib.request.urlopen(req) as resp:
            tmp.write_bytes(resp.read())
        tmp.replace(dest)


def build_parser(ref):
    gen = CACHE / f"gen-{ref}"
    if (gen / "SFMLParser.py").exists():
        return gen
    jar = CACHE / f"antlr-{ANTLR_VERSION}.jar"
    raw = CACHE / f"SFML-{ref}.g4"
    download(ANTLR_JAR_URL, jar)
    download(GRAMMAR_URL.format(ref=ref), raw)
    # Strip Java-only header/members and the predicate-guarded UNUSED rule.
    g = raw.read_text(encoding="utf-8")
    g = re.sub(r"@header \{.*?\n\}\n", "", g, flags=re.S)
    g = re.sub(r"@lexer::members \{.*?\n\}\n", "", g, flags=re.S)
    g = re.sub(r"UNUSED\s*:.*?;\n", "", g, flags=re.S)
    work = CACHE / f"grammar-{ref}"
    work.mkdir(parents=True, exist_ok=True)
    (work / "SFML.g4").write_text(g, encoding="utf-8")
    subprocess.run(
        ["java", "-jar", str(jar), "-Dlanguage=Python3", "-o", str(gen), "-Xexact-output-dir", "SFML.g4"],
        cwd=work, check=True,
    )
    return gen


def make_parse(gen):
    sys.path.insert(0, str(gen))
    from antlr4 import CommonTokenStream, InputStream
    from antlr4.error.ErrorListener import ErrorListener
    from SFMLLexer import SFMLLexer
    from SFMLParser import SFMLParser

    class Collect(ErrorListener):
        def __init__(self):
            self.errors = []

        def syntaxError(self, recognizer, symbol, line, col, msg, e):
            self.errors.append(f"{line}:{col} {msg}")

    def parse(src):
        listener = Collect()
        lexer = SFMLLexer(InputStream(src))
        lexer.removeErrorListeners()
        lexer.addErrorListener(listener)
        parser = SFMLParser(CommonTokenStream(lexer))
        parser.removeErrorListeners()
        parser.addErrorListener(listener)
        parser.program()
        return listener.errors

    return parse


def check_code_blocks(parse):
    failures, total = 0, 0
    for md in sorted(SKILLS.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        for m in BLOCK_RE.finditer(text):
            kind, body = m.group(1), m.group(2)
            if body.strip() == "...":  # placeholder inside the answer-format template
                continue
            total += 1
            src = body if kind == "sfml" else f"every 20 ticks do\n{body}\nend\n"
            errors = parse(src)
            if errors:
                failures += 1
                line = text[: m.start()].count("\n") + 1
                print(f"FAIL {md.relative_to(ROOT)}:{line} ({kind}): {errors[:3]}")
    print(f"code blocks: {total} checked, {failures} failed")
    return failures == 0


def check_structure():
    ok = True
    for skill_md in sorted(SKILLS.glob("*/SKILL.md")):
        rel = skill_md.relative_to(ROOT)
        text = skill_md.read_text(encoding="utf-8")
        fm = re.match(r"---\n(.*?)\n---\n", text, re.S)
        if not fm or not re.search(r"^name: \S", fm.group(1), re.M) or not re.search(r"^description: \S", fm.group(1), re.M):
            print(f"FAIL {rel}: front matter must contain name and description")
            ok = False
        elif re.search(r"^name: (.+)$", fm.group(1), re.M).group(1).strip() != skill_md.parent.name:
            print(f"FAIL {rel}: front matter name must equal folder name '{skill_md.parent.name}'")
            ok = False
        lines = text.count("\n")
        if lines > MAX_SKILL_LINES:
            print(f"FAIL {rel}: {lines} lines > {MAX_SKILL_LINES}; move details into references/")
            ok = False
        refs = set(re.findall(r"references/[\w.-]+\.md", text))
        refs |= {f"references/{n}" for n in re.findall(r"`([\w-]+\.md)`", text)}
        for ref in sorted(refs):
            if not (skill_md.parent / ref).exists():
                print(f"FAIL {rel}: mentions missing file {ref}")
                ok = False
        for f in sorted((skill_md.parent / "references").glob("*.md")):
            if f"references/{f.name}" not in refs:
                print(f"WARN {rel}: {f.relative_to(ROOT)} is never referenced, the model will not find it")
        print(f"structure: {rel} {lines} lines, {len(refs)} reference files")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="HEAD", help="git ref of TeamDman/SuperFactoryManager for SFML.g4")
    args = ap.parse_args()
    try:
        import antlr4  # noqa: F401
    except ImportError:
        sys.exit(f"missing dependency: pip install antlr4-python3-runtime=={ANTLR_VERSION}")
    parse = make_parse(build_parser(args.ref))
    ok = check_structure() & check_code_blocks(parse)
    print("OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
