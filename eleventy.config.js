// Configuración de Eleventy: las páginas viven en src/ (plantillas Nunjucks)
// y se generan como HTML estático en _site/, que es lo que publica Netlify.
// Los recursos estáticos se quedan en la raíz del repo y se copian tal cual.
export default function (eleventyConfig) {
  for (const path of [
    "styles.css",
    "site.js",
    "favicon",
    "images",
    "illustrations",
    "robots.txt",
    "sitemap.xml",
    "55f406de27b942c699c397076e80feb9.txt",
  ]) {
    eleventyConfig.addPassthroughCopy(path);
  }

  return {
    dir: { input: "src", output: "_site" },
    templateFormats: ["njk", "md"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
  };
}
