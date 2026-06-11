#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline de generación de favicons de nódicus.

Genera TODO el conjunto de iconos del sitio a partir de una sola imagen de
origen (el logotipo "nód" en PNG con fondo transparente, p. ej.
`favicon_br.png`). Reproduce exactamente el mismo resultado que el conjunto
actual, de modo que si el logo vuelve a cambiar basta con re-ejecutar este
script sobre la nueva imagen, sin margen de error.

--------------------------------------------------------------------------
Qué genera (en la carpeta `favicon/`)
--------------------------------------------------------------------------
Iconos de pestaña/navegador  ->  FONDO TRANSPARENTE, lema a TODO EL ANCHO,
                                  centrado verticalmente:
    - favicon.svg            (PNG del lema incrustado, a tamaño nativo)
    - favicon.ico            (frames 16x16, 32x32, 48x48)
    - favicon-96x96.png

Iconos de app/escritorio     ->  FONDO BLANCO opaco, lema al ~70 % del ancho,
                                  centrado en ambos ejes:
    - apple-touch-icon.png         (180x180)
    - web-app-manifest-192x192.png (192x192, maskable)
    - web-app-manifest-512x512.png (512x512, maskable)

El `site.webmanifest` NO se toca: es configuración (nombre, colores, rutas),
no se deriva de la imagen.

--------------------------------------------------------------------------
Por qué esos valores
--------------------------------------------------------------------------
Las constantes de maquetación se midieron sobre el conjunto original:
  - Iconos blancos: el lema ocupaba 360 px de ancho en un lienzo de 512
    (= 0,703 del ancho), centrado -> WHITE_WIDTH_RATIO.
  - Iconos transparentes: el lema iba a sangre (todo el ancho del lienzo),
    centrado en vertical.
La convención es la estándar: los iconos de pestaña transparentes se adaptan
a barras claras/oscuras; los de app van sobre blanco con aire alrededor.

--------------------------------------------------------------------------
Requisitos
--------------------------------------------------------------------------
    pip install Pillow

--------------------------------------------------------------------------
Uso
--------------------------------------------------------------------------
    # La imagen de origen es obligatoria (se pasa como argumento):
    python tools/generate_favicons.py ruta/al/logo.png

    # Con carpeta de salida personalizada:
    python tools/generate_favicons.py ruta/al/logo.png --out otra/carpeta

La imagen de origen debe ser el lema sobre fondo TRANSPARENTE (PNG/RGBA).
Si no tuviera canal alfa, se detecta el contenido recortando el blanco.
"""

import argparse
import base64
import io
from pathlib import Path

from PIL import Image

# --- Resampling compatible entre versiones de Pillow ---
try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:  # Pillow < 9.1
    RESAMPLE = Image.LANCZOS

# --- Carpeta de salida por defecto (relativa a este script: tools/ -> repo/ -> favicon/) ---
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "favicon"

# --- Constantes de maquetación (medidas del conjunto original) ---
WHITE_BG = (255, 255, 255, 255)
TRANSPARENT_BG = (0, 0, 0, 0)
WHITE_WIDTH_RATIO = 360 / 512  # lema = 70,3 % del ancho en los iconos blancos
ICO_SIZES = [(16, 16), (32, 32), (48, 48)]
ICO_MASTER = 256  # los frames del .ico se reducen desde este maestro

# Iconos de app: fondo blanco, lema centrado al WHITE_WIDTH_RATIO del ancho.
WHITE_ICONS = {
    "apple-touch-icon.png": 180,
    "web-app-manifest-192x192.png": 192,
    "web-app-manifest-512x512.png": 512,
}
# Icono PNG de pestaña: fondo transparente, lema a todo el ancho.
TRANSPARENT_PNG = {
    "favicon-96x96.png": 96,
}


def load_wordmark(source: Path) -> Image.Image:
    """Abre la imagen de origen y la recorta ajustada al lema (sin márgenes)."""
    img = Image.open(source).convert("RGBA")
    alpha = img.split()[-1]
    bbox = alpha.getbbox()  # recorte por transparencia
    if bbox is None:
        # Sin alfa útil: recortar tratando el blanco como fondo.
        from PIL import ImageChops

        rgb = img.convert("RGB")
        bg = Image.new("RGB", rgb.size, (255, 255, 255))
        bbox = ImageChops.difference(rgb, bg).getbbox()
    if bbox is None:
        raise ValueError("No se detecta contenido en la imagen de origen.")
    return img.crop(bbox)


def square_padded(word: Image.Image, size: int, bg) -> Image.Image:
    """Lema escalado a WHITE_WIDTH_RATIO del ancho, centrado, sobre `bg`."""
    ww, wh = word.size
    canvas = Image.new("RGBA", (size, size), bg)
    tw = round(size * WHITE_WIDTH_RATIO)
    th = round(tw * wh / ww)
    resized = word.resize((tw, th), RESAMPLE)
    canvas.paste(resized, ((size - tw) // 2, (size - th) // 2), resized)
    return canvas


def square_full_bleed(word: Image.Image, size: int, bg) -> Image.Image:
    """Lema a todo el ancho del lienzo, centrado en vertical, sobre `bg`."""
    ww, wh = word.size
    canvas = Image.new("RGBA", (size, size), bg)
    tw = size
    th = round(tw * wh / ww)
    resized = word.resize((tw, th), RESAMPLE)
    canvas.paste(resized, (0, (size - th) // 2), resized)
    return canvas


def build_svg(word: Image.Image) -> str:
    """SVG que incrusta el lema recortado (RGBA, transparente) a tamaño nativo."""
    ww, wh = word.size
    buf = io.BytesIO()
    word.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{ww}" height="{wh}" viewBox="0 0 {ww} {wh}">'
        f'<image width="{ww}" height="{wh}" '
        f'xlink:href="data:image/png;base64,{b64}"/></svg>'
    )


def generate(source: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    word = load_wordmark(source)
    print(f"Origen : {source}")
    print(f"Salida : {out}")
    print(f"Lema recortado: {word.size[0]}x{word.size[1]} px\n")

    # 1) Iconos de app: fondo blanco, RGB.
    for name, size in WHITE_ICONS.items():
        square_padded(word, size, WHITE_BG).convert("RGB").save(out / name)
        print(f"  [blanco]       {name:<32} {size}x{size}")

    # 2) Icono PNG de pestaña: fondo transparente, RGBA.
    for name, size in TRANSPARENT_PNG.items():
        square_full_bleed(word, size, TRANSPARENT_BG).save(out / name)
        print(f"  [transparente] {name:<32} {size}x{size}")

    # 3) favicon.ico (multi-tamaño) desde un maestro transparente a sangre.
    master = square_full_bleed(word, ICO_MASTER, TRANSPARENT_BG)
    master.save(out / "favicon.ico", sizes=ICO_SIZES)
    sizes_txt = ", ".join(f"{w}x{h}" for w, h in ICO_SIZES)
    print(f"  [transparente] {'favicon.ico':<32} {sizes_txt}")

    # 4) favicon.svg con el lema incrustado.
    (out / "favicon.svg").write_text(build_svg(word), encoding="utf-8")
    print(f"  [transparente] {'favicon.svg':<32} {word.size[0]}x{word.size[1]}")

    print("\nListo. Recuerda: site.webmanifest es configuración y no se regenera.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera el conjunto de favicons de nódicus desde una imagen.",
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Imagen de origen (lema del logo, fondo transparente). Obligatoria.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Carpeta de salida. Por defecto: {DEFAULT_OUT}",
    )
    args = parser.parse_args()

    if not args.source.exists():
        parser.error(f"No existe la imagen de origen: {args.source}")
    generate(args.source, args.out)


if __name__ == "__main__":
    main()
