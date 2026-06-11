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
- `robots.txt`, `sitemap.xml` — SEO.

## Despliegue

Alojado en **Netlify**, con publicación automática desde la rama `main`
(ver `netlify.toml`). Cada `git push` a `main` publica el sitio.
