#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Avisa por IndexNow (Bing, Yandex, Seznam, Naver...) de las URLs que han
cambiado. Google no usa IndexNow; para Google basta con el sitemap.

Qué URLs envía: las del `sitemap.xml` actual cuyo `lastmod` es distinto al
del `sitemap.xml` de una revisión anterior de git (por defecto HEAD~1).
Como `lastmod` solo cambia cuando cambia el HTML (ver build_sitemap.py),
solo se avisa de páginas que de verdad han cambiado.

Uso:
    python tools/indexnow.py                       # compara con HEAD~1
    python tools/indexnow.py --since <commit>      # compara con otra revisión
    python tools/indexnow.py --all                 # envía todo el sitemap
    python tools/indexnow.py --wait-live           # antes, espera a que Netlify publique
    python tools/indexnow.py --dry-run             # solo muestra qué enviaría

La clave vive en `<clave>.txt` en la raíz del sitio, como pide el protocolo.
"""

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "nodicus.com"
KEY = "55f406de27b942c699c397076e80feb9"
ENDPOINT = "https://api.indexnow.org/indexnow"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def parse_sitemap(xml_text):
    if not xml_text.strip():
        return {}
    tree = ET.fromstring(xml_text)
    return {
        url.findtext("sm:loc", namespaces=NS): url.findtext("sm:lastmod", default="", namespaces=NS)
        for url in tree.findall("sm:url", NS)
    }


def sitemap_at(revision):
    try:
        return subprocess.run(
            ["git", "show", f"{revision}:sitemap.xml"],
            cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8",
        ).stdout
    except subprocess.CalledProcessError:
        return ""  # el sitemap no existía en esa revisión


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "nodicus-indexnow/1.0", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8")


def wait_until_live(local_sitemap, timeout=600):
    """Netlify tarda un poco en publicar tras el push: esperamos a que el
    sitemap servido sea el mismo que el del repo."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if parse_sitemap(fetch(f"https://{HOST}/sitemap.xml")) == parse_sitemap(local_sitemap):
                return True
        except (urllib.error.URLError, ET.ParseError):
            pass
        time.sleep(15)
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", default="HEAD~1")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--wait-live", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    local_sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    current = parse_sitemap(local_sitemap)
    if args.all:
        urls = list(current)
    else:
        previous = parse_sitemap(sitemap_at(args.since))
        urls = [url for url, lastmod in current.items() if previous.get(url) != lastmod]

    if not urls:
        print("No hay URLs nuevas ni modificadas. Nada que enviar.")
        return
    print("URLs a enviar:\n  " + "\n  ".join(urls))
    if args.dry_run:
        return

    if args.wait_live and not wait_until_live(local_sitemap):
        sys.exit("El sitemap publicado no coincide con el del repo tras 10 minutos. No se envía nada.")

    payload = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": urls,
    }).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT, data=payload, method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            print(f"IndexNow respondió {response.status}")
    except urllib.error.HTTPError as error:
        # 200/202 = aceptado; 403 = clave no válida; 422 = URLs de otro host; 429 = demasiadas peticiones
        sys.exit(f"IndexNow respondió {error.code}: {error.read().decode('utf-8', 'replace')}")


if __name__ == "__main__":
    main()
