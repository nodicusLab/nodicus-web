#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera `sitemap.xml` con un `lastmod` honesto.

Google solo usa `lastmod` si es "consistente y verificablemente correcto",
así que la fecha de cada URL cambia únicamente cuando cambia su HTML. Para
saberlo se guarda un hash por página en `tools/sitemap-state.json`:

  - si el hash coincide, se conserva el `lastmod` anterior;
  - si cambia (o la página es nueva), `lastmod` pasa a ser la fecha de hoy.

`changefreq` y `priority` no se incluyen: Google los ignora.

Uso:
    python tools/build_sitemap.py           # regenera sitemap.xml y el estado
    python tools/build_sitemap.py --check   # sale con error si están desfasados (CI)

Hay que ejecutarlo antes de hacer commit de cualquier cambio en una página.
"""

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://nodicus.com"
SITEMAP = ROOT / "sitemap.xml"
STATE = ROOT / "tools" / "sitemap-state.json"

# Carpetas que no se publican como páginas (plantillas, herramientas...)
EXCLUDED_DIRS = {"tools", "node_modules", ".git", ".github", "favicon", "_site"}
# Páginas que existen pero no deben indexarse
EXCLUDED_PAGES = {"404.html"}


def find_pages():
    pages = []
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        if rel.parts[0] in EXCLUDED_DIRS or rel.name in EXCLUDED_PAGES:
            continue
        pages.append(rel)
    return pages


def url_for(rel):
    """index.html -> /, casos/index.html -> /casos/, casos/x.html -> /casos/x"""
    parts = list(rel.parts)
    if parts[-1] == "index.html":
        parts = parts[:-1]
        return f"{SITE}/" + "".join(p + "/" for p in parts)
    parts[-1] = parts[-1][: -len(".html")]
    return f"{SITE}/" + "/".join(parts)


def page_hash(path):
    # Se normalizan los finales de línea para que Windows y Linux coincidan
    content = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()


def build(today):
    old_state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    new_state = {}
    for rel in find_pages():
        key = rel.as_posix()
        digest = page_hash(ROOT / rel)
        previous = old_state.get(key)
        if previous and previous["hash"] == digest:
            new_state[key] = previous
        else:
            new_state[key] = {"hash": digest, "lastmod": today}

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for key, entry in new_state.items():
        lines += [
            "  <url>",
            f"    <loc>{escape(url_for(Path(key)))}</loc>",
            f"    <lastmod>{entry['lastmod']}</lastmod>",
            "  </url>",
        ]
    lines.append("</urlset>")
    sitemap = "\n".join(lines) + "\n"
    state = json.dumps(new_state, indent=2, ensure_ascii=False) + "\n"
    return sitemap, state


def is_stale():
    """True si alguna página cambió (o apareció/desapareció) sin regenerar el
    sitemap. Solo se comparan hashes y URLs: el lastmod de una página
    cambiada sería "hoy", y eso no depende de cuándo se compruebe."""
    sitemap, state = build(dt.date.today().isoformat())
    current_sitemap = SITEMAP.read_text(encoding="utf-8") if SITEMAP.exists() else ""
    current_state = STATE.read_text(encoding="utf-8") if STATE.exists() else "{}"

    def hashes(text):
        return {k: v["hash"] for k, v in json.loads(text).items()}

    def locs(text):
        return [line.strip() for line in text.splitlines() if "<loc>" in line]

    return hashes(state) != hashes(current_state) or locs(sitemap) != locs(current_sitemap)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="no escribe; falla si hay cambios pendientes")
    args = parser.parse_args()

    if args.check:
        if is_stale():
            print("sitemap.xml está desfasado: ejecuta `python tools/build_sitemap.py` y haz commit.")
            sys.exit(1)
        print("sitemap.xml al día.")
        return

    sitemap, state = build(dt.date.today().isoformat())
    SITEMAP.write_text(sitemap, encoding="utf-8", newline="\n")
    STATE.write_text(state, encoding="utf-8", newline="\n")
    print(sitemap)


if __name__ == "__main__":
    main()
