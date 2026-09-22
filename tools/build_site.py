#!/usr/bin/env python3
"""Regenerate site/index.html (artifact format, no HTML skeleton) from index.html.

index.html is the source of truth. Run after every edit:
    python3 tools/build_site.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DROP = (
    "<!doctype html>",
    '<html lang="en">',
    "<head>",
    '<meta name="viewport"',
    '<meta name="description"',
    '<meta property="og:',
    '<link rel="icon"',
    '<meta name="twitter:',
    '<meta name="theme-color"',
    "</head>",
    "<body>",
    "</body>",
    "</html>",
)

lines = (ROOT / "index.html").read_text(encoding="utf-8").split("\n")
out = [l for l in lines if not l.strip().startswith(DROP)]
# collapse the blank lines left where the skeleton was
text = "\n".join(out).strip("\n") + "\n"
while "\n\n\n" in text:
    text = text.replace("\n\n\n", "\n\n")
(ROOT / "site" / "index.html").write_text(text, encoding="utf-8")
print("site/index.html rebuilt:", len(text), "bytes")
