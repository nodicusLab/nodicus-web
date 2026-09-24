// Datos estructurados propios de cada página, calculados a partir de su front matter:
//   crumbs      -> BreadcrumbList (migas de pan)
//   serviceName -> Service ofrecido por nódicus
//   articleType -> Article (casos) con fechas de publicación y modificación
// base.njk los junta con los nodos comunes de schemaOrg.js.
const SITE = "https://nodicus.com";
const ORG = { "@id": `${SITE}/#organization` };

export default {
  schemaPage: (data) => {
    const nodes = [];
    const url = SITE + data.page.url;

    if (data.crumbs) {
      const items = [...data.crumbs, { name: data.crumbName || data.h1, url: data.page.url }];
      nodes.push({
        "@type": "BreadcrumbList",
        itemListElement: items.map((item, i) => ({
          "@type": "ListItem",
          position: i + 1,
          name: item.name,
          item: SITE + item.url,
        })),
      });
    }

    if (data.serviceName) {
      nodes.push({
        "@type": "Service",
        "@id": `${url}#service`,
        name: data.serviceName,
        description: data.description,
        provider: ORG,
        areaServed: { "@type": "Country", name: "España" },
        url,
      });
    }

    if (data.articleType) {
      nodes.push({
        "@type": data.articleType,
        "@id": `${url}#article`,
        headline: data.h1,
        description: data.description,
        inLanguage: "es",
        datePublished: data.published,
        dateModified: data.modified || data.published,
        author: ORG,
        publisher: ORG,
        mainEntityOfPage: url,
        image: `${SITE}/images/og-image.jpg`,
      });
    }

    return nodes;
  },
};
