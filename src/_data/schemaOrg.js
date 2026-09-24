// Datos estructurados (schema.org) comunes a todas las páginas: quién es
// nódicus y quiénes lo forman. Cada página puede añadir nodos propios con
// `schemaExtra` en su front matter (migas de pan, artículo, servicio...).
const SITE = "https://nodicus.com";

export default {
  base: [
    {
      "@type": "ProfessionalService",
      "@id": `${SITE}/#organization`,
      name: "nódicus",
      alternateName: "Nodicus",
      url: `${SITE}/`,
      logo: `${SITE}/images/logo.png`,
      image: `${SITE}/images/og-image.jpg`,
      description: "Soluciones de datos, IA y automatización a medida para empresas.",
      slogan: "IA para las empresas, empresas para las personas",
      email: "contacto@nodicus.com",
      address: {
        "@type": "PostalAddress",
        addressLocality: "Valencia",
        addressRegion: "Comunidad Valenciana",
        addressCountry: "ES",
      },
      areaServed: { "@type": "Country", name: "España" },
      knowsAbout: [
        "Integración de datos",
        "Cuadros de mando",
        "Inteligencia artificial",
        "Aprendizaje automático",
        "Visión por computador",
        "Automatización de procesos",
      ],
      founder: [
        { "@id": `${SITE}/#javier-martinez-llinares` },
        { "@id": `${SITE}/#pedro-de-luna-huerta` },
      ],
      sameAs: ["https://www.linkedin.com/company/nodicus"],
    },
    {
      "@type": "Person",
      "@id": `${SITE}/#javier-martinez-llinares`,
      name: "Javier Martínez Llinares",
      jobTitle: "Cofundador",
      worksFor: { "@id": `${SITE}/#organization` },
      sameAs: ["https://www.linkedin.com/in/javier-martinez-llinares"],
    },
    {
      "@type": "Person",
      "@id": `${SITE}/#pedro-de-luna-huerta`,
      name: "Pedro de Luna Huerta",
      jobTitle: "Cofundador",
      worksFor: { "@id": `${SITE}/#organization` },
      sameAs: ["https://www.linkedin.com/in/pedro-de-luna-huerta-1a161b333"],
    },
    {
      "@type": "WebSite",
      "@id": `${SITE}/#website`,
      url: `${SITE}/`,
      name: "nódicus",
      inLanguage: "es",
      publisher: { "@id": `${SITE}/#organization` },
    },
  ],
};
