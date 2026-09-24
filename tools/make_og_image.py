#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera la imagen para redes sociales (og:image) de nódicus.

Renderiza la plantilla `tools/og/og-image.html` con Chrome/Edge en modo
headless a 1200x630 (el tamaño recomendado por LinkedIn, Facebook y X) y la
guarda como JPG en `images/og-image.jpg`, que es la ruta a la que apuntan
las etiquetas `og:image` y `twitter:image` de index.html.

Si cambia el lema o el estilo, se edita la plantilla y se re-ejecuta:

    python tools/make_og_image.py

Requisitos: Pillow y Chrome o Edge instalados (con conexión, para cargar
las fuentes de Google Fonts).
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "tools" / "og" / "og-image.html"
OUTPUT = ROOT / "images" / "og-image.jpg"
WIDTH, HEIGHT = 1200, 630

BROWSER_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "google-chrome",
    "chromium",
    "chromium-browser",
]


def find_browser():
    for candidate in BROWSER_CANDIDATES:
        path = shutil.which(candidate) or (candidate if Path(candidate).exists() else None)
        if path:
            return path
    sys.exit("No se ha encontrado Chrome ni Edge.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "og.png"
        subprocess.run(
            [
                find_browser(),
                "--headless=new",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                f"--window-size={WIDTH},{HEIGHT}",
                "--virtual-time-budget=5000",  # da tiempo a cargar las fuentes
                f"--screenshot={png}",
                TEMPLATE.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
        image = Image.open(png).convert("RGB")
        if image.size != (WIDTH, HEIGHT):
            image = image.crop((0, 0, WIDTH, HEIGHT))
        args.out.parent.mkdir(parents=True, exist_ok=True)
        image.save(args.out, "JPEG", quality=90, optimize=True, progressive=True)

    print(f"OK -> {args.out.relative_to(ROOT)} ({args.out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
