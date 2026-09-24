#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprobaciones técnicas de SEO sobre el HTML generado (_site/). Se ejecuta en
CI en cada push y pull request, y también a mano:

    npm run build && python tools/qa_check.py

Por cada página publicada comprueba:
  - <title> y meta description: presentes, con longitud razonable y sin
    duplicados entre páginas.
  - Un único <h1>.
  - <link rel="canonical"> absoluto hacia https://nodicus.com.
  - og:image apunta a un archivo que existe en el repo.
  - Todos los bloques JSON-LD son JSON válido.
  - Ninguna imagen sin atributo alt.
  - Enlaces y recursos locales (href/src) que existen, y anclas #id que
    existen en la página.
  - Restos de plantillas o datos rotos en el texto: undefined, NaN,
    [object Object], {{ }}, lorem ipsum.
Y a nivel de sitio: robots.txt declara el sitemap y el sitemap está al día.

Errores -> código de salida 1. Avisos -> solo se muestran.
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from build_sitemap import SITE, SITE_DIR, find_pages, is_stale as sitemap_is_stale  # noqa: E402

BROKEN_TEXT = re.compile(r"\bundefined\b|\bNaN\b|\[object Object\]|\{\{|\}\}|lorem ipsum", re.IGNORECASE)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titles, self.h1, self.ids, self.links = [], 0, set(), []
        self.meta, self.canonical, self.jsonld, self.imgs_without_alt = {}, [], [], []
        self.text = []
        self._stack = []  # etiquetas cuyo contenido capturamos (title, script, style)
        self._buffer = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "h1":
            self.h1 += 1
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical.append(a.get("href", ""))
        elif tag == "img" and "alt" not in a:
            self.imgs_without_alt.append(a.get("src", "?"))
        for attr in ("href", "src"):
            if a.get(attr):
                self.links.append(a[attr])
        if tag in ("title", "script", "style"):
            self._stack.append((tag, a.get("type", "")))
            self._buffer = ""

    def handle_endtag(self, tag):
        if self._stack and self._stack[-1][0] == tag:
            name, kind = self._stack.pop()
            if name == "title":
                self.titles.append(self._buffer.strip())
            elif name == "script" and kind == "application/ld+json":
                self.jsonld.append(self._buffer)

    def handle_data(self, data):
        if self._stack:
            self._buffer += data
        else:
            self.text.append(data)


def check_page(rel, errors, warnings, seen):
    html = (SITE_DIR / rel).read_text(encoding="utf-8")
    page = PageParser()
    page.feed(html)
    where = rel.as_posix()

    def err(msg):
        errors.append(f"{where}: {msg}")

    def warn(msg):
        warnings.append(f"{where}: {msg}")

    # Título
    if len(page.titles) != 1 or not page.titles[0]:
        err(f"debe tener exactamente un <title> no vacío (tiene {len(page.titles)})")
    else:
        title = page.titles[0]
        if not 15 <= len(title) <= 65:
            warn(f"el título tiene {len(title)} caracteres (recomendado 15-65): {title!r}")
        seen.setdefault(("title", title), []).append(where)

    # Meta description
    description = page.meta.get("description", "").strip()
    if not description:
        err("falta meta description")
    else:
        if not 70 <= len(description) <= 160:
            warn(f"la meta description tiene {len(description)} caracteres (recomendado 70-160)")
        seen.setdefault(("description", description), []).append(where)

    # H1
    if page.h1 != 1:
        err(f"debe tener exactamente un <h1> (tiene {page.h1})")

    # Canonical
    if len(page.canonical) != 1:
        err(f"debe tener exactamente un canonical (tiene {len(page.canonical)})")
    elif not page.canonical[0].startswith(SITE + "/"):
        err(f"el canonical no es absoluto hacia {SITE}: {page.canonical[0]}")

    # og:image
    og_image = page.meta.get("og:image", "")
    if not og_image:
        warn("falta og:image")
    elif og_image.startswith(SITE):
        local = SITE_DIR / urlparse(og_image).path.lstrip("/")
        if not local.exists():
            err(f"og:image apunta a un archivo que no existe: {og_image}")

    # JSON-LD
    for block in page.jsonld:
        try:
            json.loads(block)
        except json.JSONDecodeError as error:
            err(f"JSON-LD inválido: {error}")

    # Imágenes sin alt
    for src in page.imgs_without_alt:
        err(f"imagen sin atributo alt: {src}")

    # Enlaces y recursos locales
    for link in page.links:
        parsed = urlparse(link)
        if parsed.scheme or link.startswith("//"):
            continue  # externos (http, mailto, tel...): los revisa lychee
        if link.startswith("#"):
            anchor = link[1:]
            if anchor and anchor not in page.ids:
                err(f"ancla rota: {link}")
            continue
        target = (SITE_DIR / rel).parent / parsed.path if not parsed.path.startswith("/") else SITE_DIR / parsed.path.lstrip("/")
        if parsed.path and not (target.exists() or target.with_suffix(".html").exists() or (target / "index.html").exists()):
            err(f"recurso o enlace local inexistente: {link}")

    # Restos de plantilla o datos rotos en el texto visible
    visible = " ".join(page.text)
    for match in sorted(set(BROKEN_TEXT.findall(visible))):
        err(f"texto sospechoso de dato roto o plantilla: {match!r}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    errors, warnings, seen = [], [], {}
    pages = find_pages()
    for rel in pages:
        check_page(rel, errors, warnings, seen)

    for (kind, value), where in seen.items():
        if len(where) > 1:
            errors.append(f"{kind} duplicado en {', '.join(where)}: {value!r}")

    robots = (SITE_DIR / "robots.txt").read_text(encoding="utf-8") if (SITE_DIR / "robots.txt").exists() else ""
    if f"Sitemap: {SITE}/sitemap.xml" not in robots:
        errors.append("robots.txt no declara el sitemap")

    if sitemap_is_stale():
        errors.append("sitemap.xml está desfasado: ejecuta `python tools/build_sitemap.py` y haz commit")

    print(f"Páginas revisadas: {len(pages)}")
    for warning in warnings:
        print(f"AVISO  {warning}")
    for error in errors:
        print(f"ERROR  {error}")
    if errors:
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
