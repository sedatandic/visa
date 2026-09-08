#!/usr/bin/env node
/* Build sonrasi her rota icin statik SEO HTML uretir: tekil title/description,
   canonical, JSON-LD ve gercek metin icerigi. Bot'lar JS calistirmasa da icerigi gorur.
   Hata durumunda build'i dusurmez (exit 0). */

const fs = require("fs");
const path = require("path");
const { buildStaticPages, BRAND } = require("./seo-pages");

/** CRA .env dosyalarini yukler (node scripti webpack env'ini gormez). */
function loadEnv() {
    [".env.production.local", ".env.local", ".env.production", ".env"].forEach((name) => {
        const file = path.join(__dirname, "..", name);
        if (!fs.existsSync(file)) return;
        fs.readFileSync(file, "utf8")
            .split("\n")
            .forEach((line) => {
                const match = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
                if (!match) return;
                const [, key, raw] = match;
                if (process.env[key]) return;
                process.env[key] = raw.replace(/^["']|["']$/g, "").trim();
            });
    });
}
loadEnv();

const BUILD = path.join(__dirname, "..", "build");
const SITE_URL = (process.env.REACT_APP_SITE_URL || "https://www.dubaivizehatti.com").replace(/\/+$/, "");
const API = (process.env.REACT_APP_BACKEND_URL || "").replace(/\/+$/, "");
const OG_IMAGE = `${SITE_URL}/brand/logo-horizontal-gold-palm.png`;
const TODAY = new Date().toISOString().slice(0, 10);

const esc = (value) =>
    String(value === null || value === undefined ? "" : value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");

/** Title 60 karakteri gecmesin: marka eki sigmiyorsa dusurulur, gerekirse kelime sinirinda kisaltilir. */
function withBrand(title) {
    const full = `${title} | ${BRAND}`;
    if (full.length <= 60) return full;
    if (title.length <= 60) return title;
    const cut = title.slice(0, 59);
    return `${cut.slice(0, cut.lastIndexOf(" ") > 30 ? cut.lastIndexOf(" ") : 59)}…`;
}

async function getJson(url) {
    if (!API) return null;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 15000);
    try {
        const res = await fetch(url, {
            signal: controller.signal,
            headers: { "User-Agent": "dvh-prerender/1.0", Accept: "application/json" },
        });
        if (!res.ok) return null;
        return await res.json();
    } catch (err) {
        console.warn(`[prerender] ${url} alinamadi: ${err.message}`);
        return null;
    } finally {
        clearTimeout(timer);
    }
}

const P = (text) => (text ? `<p>${esc(text)}</p>` : "");
const UL = (items) => {
    const list = (items || []).filter(Boolean);
    return list.length ? `<ul>${list.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>` : "";
};
const SECTION = (section) =>
    `<section><h2>${esc(section.h2)}</h2>${(section.paras || []).map(P).join("")}${UL(section.list)}</section>`;
const FAQ_BLOCK = (items) =>
    items && items.length
        ? `<section><h2>Sıkça sorulan sorular</h2>${items
              .map((f) => `<h3>${esc(f.q)}</h3><p>${esc(f.a)}</p>`)
              .join("")}</section>`
        : "";

const NAV_LINKS = [
    ["/", "Ana sayfa"],
    ["/vize-tipleri", "Dubai vize fiyatları"],
    ["/basvuru", "Vize başvuru formu"],
    ["/gerekli-belgeler", "Gerekli belgeler"],
    ["/hizmetler", "Hizmetlerimiz"],
    ["/sss", "Sıkça sorulan sorular"],
    ["/takip", "Başvuru takip"],
    ["/esim", "Dubai eSIM"],
    ["/seyahat-sigortasi", "Seyahat sigortası"],
    ["/dubai-turlari", "Dubai turları"],
    ["/gelismeler", "Dubai'den haberler"],
    ["/hakkimizda", "Hakkımızda"],
    ["/iletisim", "İletişim"],
];

function jsonLdBlocks(page, ctx) {
    const company = (ctx.site && ctx.site.company) || {};
    const url = `${SITE_URL}${page.path}`;
    const org = {
        "@context": "https://schema.org",
        "@type": "TravelAgency",
        "@id": `${SITE_URL}/#organization`,
        name: BRAND,
        legalName: company.legal_name || undefined,
        url: SITE_URL,
        logo: { "@type": "ImageObject", url: OG_IMAGE },
        image: OG_IMAGE,
        telephone: company.phone || undefined,
        email: company.email || undefined,
        address: company.address
            ? { "@type": "PostalAddress", streetAddress: company.address, addressCountry: "TR" }
            : undefined,
        areaServed: { "@type": "Country", name: "Türkiye" },
        sameAs: [company.instagram].filter(Boolean),
    };
    const blocks = [];
    (page.jsonld || []).forEach((kind) => {
        if (kind === "organization") blocks.push(org);
        if (kind === "website") {
            blocks.push({
                "@context": "https://schema.org",
                "@type": "WebSite",
                "@id": `${SITE_URL}/#website`,
                name: BRAND,
                url: SITE_URL,
                inLanguage: "tr-TR",
                publisher: { "@id": `${SITE_URL}/#organization` },
            });
        }
        if (kind === "faq" && (page.faq || []).length) {
            blocks.push({
                "@context": "https://schema.org",
                "@type": "FAQPage",
                mainEntity: page.faq.map((f) => ({
                    "@type": "Question",
                    name: f.q,
                    acceptedAnswer: { "@type": "Answer", text: f.a },
                })),
            });
        }
        if (kind === "breadcrumb" && page.path !== "/") {
            blocks.push({
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                itemListElement: [
                    { "@type": "ListItem", position: 1, name: "Ana sayfa", item: `${SITE_URL}/` },
                    ...(page.breadcrumb || []).map((b, i) => ({
                        "@type": "ListItem",
                        position: i + 2,
                        name: b.name,
                        item: `${SITE_URL}${b.path}`,
                    })),
                    { "@type": "ListItem", position: (page.breadcrumb || []).length + 2, name: page.h1, item: url },
                ],
            });
        }
    });
    return blocks.concat(page.extraJsonLd || []);
}

/** Onceki prerender cikitisini temizler (script tekrar kosulabilsin). */
function cleanTemplate(raw) {
    let html = raw
        .replace(/<title>[\s\S]*?<\/title>/gi, "")
        .replace(/<meta[^>]*name="description"[^>]*>/gi, "")
        .replace(/<meta[^>]*name="robots"[^>]*>/gi, "")
        .replace(/<meta[^>]*(?:property="og:|name="twitter:)[^>]*>/gi, "")
        .replace(/<link[^>]*rel="canonical"[^>]*>/gi, "")
        .replace(/<script type="application\/ld\+json">[\s\S]*?<\/script>/gi, "");
    const start = html.indexOf('<div id="root">');
    const end = html.lastIndexOf("</div>");
    if (start !== -1 && end > start) {
        html = `${html.slice(0, start)}<div id="root"></div>${html.slice(end + "</div>".length)}`;
    }
    return html;
}

function renderPage(template, page, ctx) {
    const url = `${SITE_URL}${page.path === "/" ? "/" : page.path}`;
    const head = [
        `<title>${esc(page.title)}</title>`,
        `<meta name="description" content="${esc(page.description)}"/>`,
        `<link rel="canonical" href="${esc(url)}"/>`,
        `<meta name="robots" content="index, follow"/>`,
        `<meta property="og:site_name" content="${esc(BRAND)}"/>`,
        `<meta property="og:type" content="${page.ogType || "website"}"/>`,
        `<meta property="og:locale" content="tr_TR"/>`,
        `<meta property="og:title" content="${esc(page.title)}"/>`,
        `<meta property="og:description" content="${esc(page.description)}"/>`,
        `<meta property="og:url" content="${esc(url)}"/>`,
        `<meta property="og:image" content="${esc(page.image || OG_IMAGE)}"/>`,
        `<meta name="twitter:card" content="summary_large_image"/>`,
        `<meta name="twitter:title" content="${esc(page.title)}"/>`,
        `<meta name="twitter:description" content="${esc(page.description)}"/>`,
        `<meta name="twitter:image" content="${esc(page.image || OG_IMAGE)}"/>`,
        ...jsonLdBlocks(page, ctx).map(
            (block) =>
                `<script type="application/ld+json">${JSON.stringify(block).replace(/</g, "\\u003c")}</script>`
        ),
    ].join("");

    const body =
        `<div id="seo-prerender">` +
        `<h1>${esc(page.h1)}</h1>` +
        (page.intro || []).map(P).join("") +
        (page.sections || []).map(SECTION).join("") +
        FAQ_BLOCK(page.faq) +
        `<nav aria-label="Site haritası"><ul>${NAV_LINKS.filter(([href]) => href !== page.path)
            .map(([href, label]) => `<li><a href="${href}">${esc(label)}</a></li>`)
            .join("")}</ul></nav>` +
        `</div>`;

    let html = template.replace("</head>", `${head}</head>`);
    html = html.replace('<div id="root"></div>', `<div id="root">${body}</div>`);
    return html;
}

function writePage(template, page, ctx) {
    const html = renderPage(template, page, ctx);
    const dir = page.path === "/" ? BUILD : path.join(BUILD, page.path.replace(/^\//, ""));
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, "index.html"), html, "utf8");
}

function guidePage(guide) {
    const visa = guide.visa || {};
    const price = Number(visa.price);
    return {
        path: `/dubai-vizesi/${guide.slug}`,
        priority: "0.8",
        changefreq: "monthly",
        title: guide.seo_title,
        description: guide.seo_description,
        h1: guide.h1,
        intro: guide.intro || [],
        breadcrumb: [{ name: "Dubai vize fiyatları", path: "/vize-tipleri" }],
        sections: [
            (guide.who_for || []).length && { h2: "Bu vize kimler için uygun?", list: guide.who_for },
            (guide.highlights || []).length && {
                h2: "Öne çıkan bilgiler",
                list: guide.highlights.map((h) => (typeof h === "string" ? h : `${h.title || ""}: ${h.detail || h.description || ""}`)),
            },
            visa.name && {
                h2: "Vize özeti",
                list: [
                    `Kalış süresi: ${visa.duration_days} gün`,
                    `Giriş tipi: ${visa.entry_label}`,
                    `Sonuçlanma: ${visa.processing_days}`,
                    price ? `Hizmet bedeli: ${Math.round(price).toLocaleString("tr-TR")} TL (${Math.round(visa.price_usd)} USD)` : null,
                ].filter(Boolean),
            },
            (guide.documents || []).length && {
                h2: "Gerekli belgeler",
                list: guide.documents.map((d) => `${d.title}${d.required ? " (zorunlu)" : " (zorunlu değil)"}: ${d.detail}`),
            },
            (guide.tips || []).length && { h2: "Danışman notları", list: guide.tips },
        ].filter(Boolean),
        faq: guide.faqs || [],
        jsonld: ["faq", "breadcrumb"],
        extraJsonLd: [
            {
                "@context": "https://schema.org",
                "@type": "Service",
                name: guide.h1,
                serviceType: "Vize danışmanlığı",
                description: guide.seo_description,
                inLanguage: "tr-TR",
                areaServed: { "@type": "Country", name: "Türkiye" },
                provider: { "@id": `${SITE_URL}/#organization` },
                url: `${SITE_URL}/dubai-vizesi/${guide.slug}`,
                ...(price
                    ? {
                          offers: {
                              "@type": "Offer",
                              price: price.toFixed(2),
                              priceCurrency: visa.currency || "TRY",
                              availability: "https://schema.org/InStock",
                              url: `${SITE_URL}/basvuru/${String(visa.id || "").replace(/_/g, "-")}`,
                          },
                      }
                    : {}),
            },
        ],
    };
}

function articlePage(article) {
    const body = Array.isArray(article.body) ? article.body : [article.body].filter(Boolean);
    const url = `${SITE_URL}/gelismeler/${article.slug}`;
    const image = article.image_url || article.image || OG_IMAGE;
    return {
        path: `/gelismeler/${article.slug}`,
        priority: "0.6",
        changefreq: "monthly",
        ogType: "article",
        image,
        title: withBrand(article.title),
        description: (article.excerpt || article.title).slice(0, 160),
        h1: article.title,
        intro: body,
        breadcrumb: [{ name: "Dubai'den haberler", path: "/gelismeler" }],
        sections: [
            (article.related || []).length && {
                h2: "İlgili yazılar",
                list: (article.related || []).map((r) => `${r.title}${r.excerpt ? `: ${r.excerpt}` : ""}`),
            },
            {
                h2: "Dubai vize başvurunuzu bizimle yapın",
                paras: [
                    "Dubai vizesi için yalnızca pasaportunuzun kimlik sayfası ve vesikalık fotoğrafınız yeterlidir; uçak bileti ve otel rezervasyonu zorunlu değildir. Başvurunuzu online tamamlayın, belgelerinizi biz kontrol edip yetkili mercilere iletelim.",
                    "Standart başvurularda sonuç ortalama 2 iş gününde çıkar; acil durumlarda ekspres hizmetle yaklaşık 8 mesai saatinde sonuç alınır. Onaylı vizeniz e-posta ve WhatsApp ile teslim edilir.",
                ],
            },
        ].filter(Boolean),
        faq: [],
        jsonld: ["breadcrumb"],
        extraJsonLd: [
            {
                "@context": "https://schema.org",
                "@type": "Article",
                headline: article.title.slice(0, 110),
                description: article.excerpt || "",
                image: [image],
                datePublished: article.date,
                dateModified: article.updated_at || article.date,
                inLanguage: "tr-TR",
                author: { "@type": "Organization", name: BRAND, url: SITE_URL },
                publisher: {
                    "@type": "Organization",
                    name: BRAND,
                    logo: { "@type": "ImageObject", url: OG_IMAGE },
                },
                mainEntityOfPage: { "@type": "WebPage", "@id": url },
                url,
            },
        ],
    };
}

function writeSitemap(pages) {
    const urls = pages
        .map(
            (p) =>
                `    <url>\n        <loc>${SITE_URL}${p.path === "/" ? "/" : p.path}</loc>\n` +
                `        <lastmod>${TODAY}</lastmod>\n` +
                `        <changefreq>${p.changefreq || "monthly"}</changefreq>\n` +
                `        <priority>${p.priority || "0.5"}</priority>\n    </url>`
        )
        .join("\n");
    fs.writeFileSync(
        path.join(BUILD, "sitemap.xml"),
        `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`,
        "utf8"
    );
}

async function main() {
    const templatePath = path.join(BUILD, "index.html");
    if (!fs.existsSync(templatePath)) {
        console.warn("[prerender] build/index.html yok, atlandi");
        return;
    }
    const template = cleanTemplate(fs.readFileSync(templatePath, "utf8"));
    if (!template.includes('<div id="root"></div>')) {
        console.warn("[prerender] root kabugu bulunamadi, atlandi");
        return;
    }

    const [site, visaTypes, guideIndex, articlesRaw, legal] = await Promise.all([
        getJson(`${API}/api/content/site`),
        getJson(`${API}/api/visa-types`),
        getJson(`${API}/api/visa-guides`),
        getJson(`${API}/api/articles`),
        getJson(`${API}/api/content/legal`),
    ]);

    const guides = [];
    for (const item of (guideIndex && guideIndex.items) || []) {
        const guide = await getJson(`${API}/api/visa-guides/${item.slug}`);
        if (guide && guide.h1 && guide.seo_title) guides.push(guide);
    }
    const articleList = Array.isArray(articlesRaw) ? articlesRaw : (articlesRaw && articlesRaw.items) || [];
    const articles = [];
    for (const item of articleList.filter((a) => a && a.slug)) {
        const detail = await getJson(`${API}/api/articles/${item.slug}`);
        articles.push({ ...item, ...((detail && detail.article) || {}), related: (detail && detail.related) || [] });
    }

    const ctx = { site, legal, visaTypes: visaTypes || [], guides, articles };
    const pages = [
        ...buildStaticPages(ctx),
        ...guides.map(guidePage),
        ...articles.filter((a) => a && a.slug).map(articlePage),
    ];

    pages.forEach((page) => writePage(template, page, ctx));
    writeSitemap(pages);
    console.log(`[prerender] ${pages.length} sayfa yazildi (${guides.length} rehber, ${articles.length} yazi)`);
}

main().catch((err) => {
    console.warn(`[prerender] atlandi: ${err.message}`);
    process.exit(0);
});
