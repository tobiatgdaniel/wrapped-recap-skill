#!/usr/bin/env python3
"""Fill the Wrapped template with slide data and check it against the copy rules.

Usage:
    python scripts/build.py data.json out.html

Prints warnings for style issues and exits with code 1 on errors that would
break the page (unknown slide types, neighbouring slides with the same
background, missing intro or outro). The output file is still written when
there are only warnings.
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "template.html"

TYPES = {"intro", "month", "gap", "stats", "ranking", "personality", "note", "outro"}
PALETTE = {"plum", "cobalt", "violet", "pink", "sun", "tang", "mint", "lilac"}
TESTED = {
    "plum/cobalt", "cobalt/plum", "lilac/sun", "sun/tang", "pink/sun", "mint/lilac",
    "tang/sun", "plum/violet", "sun/pink", "mint/sun", "pink/lilac", "lilac/pink",
}
BEGIN = "// ===== BEGIN WRAPPED DATA ====="
END = "// ===== END WRAPPED DATA ====="
MAX_ITEM_WORDS = 20
STRAIGHT_QUOTE = re.compile(r"['\"]")


def words(s):
    return len(s.split())


def check(data):
    errors, warnings = [], []
    slides = data.get("slides") or []
    if not slides:
        errors.append("no slides")
        return errors, warnings
    if slides[0].get("type") != "intro":
        errors.append("first slide must be type 'intro'")
    if slides[-1].get("type") != "outro":
        errors.append("last slide must be type 'outro'")

    prev_bg = None
    for i, s in enumerate(slides, 1):
        t = s.get("type")
        where = f"slide {i} ({t})"
        if t not in TYPES:
            errors.append(f"{where}: unknown type")
            continue
        if not s.get("headline"):
            errors.append(f"{where}: missing headline")

        combo = s.get("combo")
        if combo:
            parts = combo.split("/")
            if len(parts) != 2 or not set(parts) <= PALETTE or parts[0] == parts[1]:
                errors.append(f"{where}: invalid combo '{combo}'")
            else:
                if combo not in TESTED:
                    warnings.append(f"{where}: combo '{combo}' isn't in the tested list; check contrast")
                if parts[0] == prev_bg:
                    errors.append(f"{where}: same background as the slide before ('{parts[0]}')")
                prev_bg = parts[0]
        else:
            prev_bg = None  # the page will pick a non-repeating one

        giant = str(s.get("giant", ""))
        if not giant:
            warnings.append(f"{where}: no giant word")
        elif len(giant) > 5:
            warnings.append(f"{where}: giant word '{giant}' is over 5 characters and will crop hard")

        items = s.get("items") or []
        if t == "month":
            if not 2 <= len(items) <= 5:
                warnings.append(f"{where}: {len(items)} items (aim for 2 to 5)")
            for it in items:
                if words(it) > MAX_ITEM_WORDS:
                    warnings.append(f"{where}: item over {MAX_ITEM_WORDS} words: “{it[:40]}…”")
        if t == "ranking" and len(items) != 5:
            warnings.append(f"{where}: ranking has {len(items)} items (expected 5)")
        if t == "stats":
            n = len(s.get("stats") or [])
            if not 2 <= n <= 4:
                warnings.append(f"{where}: {n} stats (aim for 3 or 4)")
            for st in s.get("stats") or []:
                if len(str(st.get("value", ""))) > 4:
                    warnings.append(f"{where}: stat value '{st.get('value')}' is long and may shrink the slide")
        if words(s.get("headline", "")) > 10:
            warnings.append(f"{where}: headline is long ({words(s['headline'])} words)")

        texts = [s.get("headline", ""), s.get("lead", ""), s.get("hint", ""), s.get("replay", "")]
        texts += items + list(s.get("body") or [])
        texts += [st.get("label", "") for st in s.get("stats") or []]
        for tx in texts:
            if STRAIGHT_QUOTE.search(tx or ""):
                warnings.append(f"{where}: straight quote or apostrophe in “{tx[:40]}”; use ’ “ ”")
            if "[" in (tx or "") and "]" in (tx or ""):
                errors.append(f"{where}: placeholder text left in “{tx[:40]}”")

    for key in ("title", "label"):
        if STRAIGHT_QUOTE.search(data.get(key, "")):
            warnings.append(f"{key}: straight quote or apostrophe; use ’")
    return errors, warnings


def build(data, template_text):
    start = template_text.index(BEGIN)
    end = template_text.index(END)
    blob = json.dumps(data, ensure_ascii=False, indent=2)
    # Keep the JSON safe inside a <script> block
    blob = blob.replace("</", "<\\/").replace("<!--", "<\\!--")
    out = template_text[:start] + BEGIN + "\nconst WRAPPED = " + blob + ";\n" + template_text[end:]
    if data.get("title"):
        out = re.sub(r"<title>.*?</title>", "<title>" + html.escape(data["title"], quote=False) + "</title>",
                     out, count=1, flags=re.S)
    if data.get("lang"):
        out = re.sub(r'<html lang="[^"]*">', f'<html lang="{html.escape(data["lang"])}">', out, count=1)
    if data.get("label"):
        out = out.replace('aria-label="Your year on Claude, a recap you tap through"',
                          f'aria-label="{html.escape(data["label"])}"', 1)
    return out


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    errors, warnings = check(data)
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("error:", e)
    Path(sys.argv[2]).write_text(build(data, TEMPLATE.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"wrote {sys.argv[2]} ({len(data.get('slides', []))} slides)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
