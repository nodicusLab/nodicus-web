# nódicus — web

Sitio web corporativo de **nódicus** (https://nodicus.com): soluciones de datos, IA y
automatización a medida.

Web estática (HTML / CSS / JS, sin framework ni paso de build).

## Estructura

- `index.html` — página única (hero, filosofía, servicios, casos, nosotros, contacto).
- `styles.css` — sistema de diseño (tokens de marca, theming, layout editorial).
- `site.js` — interacciones: header, menú móvil, smooth-scroll, animaciones y el
  formulario de contacto (conectado a EmailJS).
- `logos/`, `illustrations/`, `images/`, `favicon/` — recursos estáticos.
- `robots.txt`, `sitemap.xml` — SEO. El sitemap se genera con `tools/build_sitemap.py`.
- `55f406de27b942c699c397076e80feb9.txt` — clave de IndexNow (tiene que estar en la raíz).
- `tools/` — scripts de mantenimiento (no se publican, ver `netlify.toml`).

## SEO: flujo de trabajo

Al cambiar cualquier página:

```bash
python tools/build_sitemap.py   # actualiza lastmod solo de las páginas cuyo HTML cambió
python tools/qa_check.py        # títulos, metas, canonical, JSON-LD, enlaces, sitemap
python tools/lint_copy.py       # rasgos de redacción que suenan a IA
```

En GitHub Actions:

- `QA` corre esas comprobaciones, valida el HTML (html-validate) y revisa los
  enlaces externos (lychee) en cada push, y además cada lunes.
- `IndexNow` avisa a Bing y compañía de las URLs cambiadas cuando se publica
  un sitemap nuevo en `main` (espera a que Netlify haya desplegado).

La imagen para redes (`images/og-image.jpg`) se regenera con
`python tools/make_og_image.py` a partir de `tools/og/og-image.html`.

## Despliegue

Alojado en **Netlify**, con publicación automática desde la rama `main`
(ver `netlify.toml`). Cada `git push` a `main` publica el sitio.
