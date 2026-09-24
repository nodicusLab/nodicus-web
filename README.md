# nódicus — web

Sitio web corporativo de **nódicus** (https://nodicus.com): soluciones de datos, IA y
automatización a medida.

Web estática (HTML / CSS / JS, sin framework ni paso de build).

## Estructura

Web estática generada con [Eleventy](https://www.11ty.dev/) (`src/` -> `_site/`). El diseño es
HTML/CSS/JS propio, sin framework.

- `src/_includes/base.njk` — plantilla común: `<head>` (metas, datos estructurados),
  cabecera, pie y scripts.
- `src/index.njk` — la home. Cada página nueva es otro `.njk` en `src/`.
- `src/_data/` — datos compartidos (`site.json`, `schemaOrg.js` con la organización y los socios).
- `styles.css` — sistema de diseño (tokens de marca, theming, layout editorial).
- `site.js` — interacciones: header, menú móvil, smooth-scroll, animaciones y el
  formulario de contacto (conectado a EmailJS).
- `illustrations/`, `images/`, `favicon/` — recursos estáticos (se copian tal cual).
- `logos/` — logos de clientes. **No se publican** (la sección está oculta a petición del cliente).
- `robots.txt`, `sitemap.xml` — SEO. El sitemap se genera con `tools/build_sitemap.py`.
- `55f406de27b942c699c397076e80feb9.txt` — clave de IndexNow (tiene que estar en la raíz).
- `tools/` — scripts de mantenimiento (no se publican).

## Desarrollo

```bash
npm install
npm run serve        # http://localhost:8080 con recarga automática
```

## SEO: flujo de trabajo

Al cambiar cualquier página:

```bash
npm run build                   # genera _site/
python tools/build_sitemap.py   # actualiza lastmod solo de las páginas cuyo HTML cambió
python tools/qa_check.py        # títulos, metas, canonical, JSON-LD, enlaces, sitemap
python tools/lint_copy.py       # rasgos de redacción que suenan a IA
```

En GitHub Actions:

- `QA` construye el sitio y corre esas comprobaciones, valida el HTML (html-validate) y revisa
  los enlaces externos (lychee) en cada push a `main` y cada pull request, y además cada lunes.
- `IndexNow` avisa a Bing y compañía de las URLs cambiadas cuando se publica un sitemap nuevo
  en `main` (espera a que Netlify haya desplegado).

La imagen para redes (`images/og-image.jpg`) se regenera con `python tools/make_og_image.py` a
partir de `tools/og/og-image.html`.

## Despliegue

Alojado en **Netlify**, con publicación automática desde la rama `main` (ver `netlify.toml`):
Netlify ejecuta `npm run build` y publica `_site/`.
