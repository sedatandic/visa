/* Statik sayfa SEO icerikleri (prerender.js tarafindan kullanilir).
   Metinler sitedeki mevcut kopyadan ve /api/content/site verisinden turetilir. */

const BRAND = "Dubai Vize Hattı";

const usd = (v) => (v ? `${Math.round(v)} USD` : "");
const tl = (v) => (v ? `${Math.round(v).toLocaleString("tr-TR")} TL` : "");

const priceLine = (v) =>
    `${v.name}: ${usd(v.price_usd)}${v.price ? ` (yaklaşık ${tl(v.price)})` : ""} · ` +
    `${v.duration_days} gün kalış · ${v.entry_label} · sonuç ${v.processing_days}`;

/** Ana sayfa + ic sayfalarin tamami. ctx: { site, visaTypes, guides, articles, legal } */
function buildStaticPages(ctx) {
    const site = ctx.site || {};
    const legal = ctx.legal || {};
    const legalSections = (key) =>
        ((legal[key] || {}).sections || []).map((s) => ({
            h2: s.title,
            paras: s.body ? [s.body] : [],
            list: s.items || [],
        }));
    const legalIntro = (key) => [(legal[key] || {}).intro, legal.affiliation].filter(Boolean);
    const company = site.company || {};
    const faq = Array.isArray(site.faq) ? site.faq : [];
    const docs = Array.isArray(site.required_documents) ? site.required_documents : [];
    const photoRules = Array.isArray(site.photo_rules) ? site.photo_rules : [];
    const steps = Array.isArray(site.process_steps) ? site.process_steps : [];
    const whyUs = Array.isArray(site.why_us) ? site.why_us : [];
    const services = Array.isArray(site.services) ? site.services : [];
    const visas = (ctx.visaTypes || []).filter((v) => v.active !== false);
    const articles = ctx.articles || [];
    const guides = ctx.guides || [];

    const adultVisas = visas.filter((v) => v.category !== "child");
    const cheapest = adultVisas.reduce((min, v) => (min && min.price_usd <= v.price_usd ? min : v), null);

    return [
        {
            path: "/",
            priority: "1.0",
            changefreq: "weekly",
            title: `Dubai Vizesi Online Başvuru | ${BRAND}`,
            description:
                "Dubai (BAE) vizenizi online alın: pasaport ve fotoğrafınızı yükleyin, ödemenizi yapın, onaylı vizeniz e-postanıza gelsin. Net fiyatlar, başvuru takibi.",
            h1: "Dubai vizesi online başvuru",
            intro: [
                "Dubai Vize Hattı, Birleşik Arap Emirlikleri vize başvurularınızı sizin adınıza hazırlayıp yetkili mercilere ileten TÜRSAB üyesi A Grubu seyahat acentesi güvencesiyle çalışan bir hizmettir. Başvurunuzun tamamı online yürütülür; konsolosluğa gitmeniz, randevu almanız veya pasaportunuzu kargoya vermeniz gerekmez.",
                "Başvuru için yalnızca iki belge yeterlidir: pasaportunuzun kimlik sayfası ve vesikalık fotoğrafınız. Vizeniz onaylanmadan uçak bileti almanız ya da otel rezervasyonu yapmanız gerekmez; bu belgeler zorunlu değildir.",
                "Standart başvurularda sonuç 36 saat içinde çıkar. Acil seyahatlerde ekspres hizmetle yaklaşık 8 mesai saatinde, anında ekspres seçeneğiyle aynı gün içinde sonuç alınır. Onaylanan vizeniz PDF olarak e-postanıza ve başvuru takip sayfanıza yüklenir.",
            ],
            sections: [
                steps.length && {
                    h2: "Dubai vize başvurusu nasıl yapılır?",
                    list: steps.map((s) => `${s.title || s.label || ""}: ${s.description || s.detail || ""}`.trim()),
                },
                visas.length && {
                    h2: "Dubai vize tipleri ve hizmet bedelleri",
                    paras: [
                        cheapest
                            ? `Hizmet bedelleri kişi başıdır, tek seferliktir ve resmî harcı içerir. Başlangıç bedeli ${usd(cheapest.price_usd)} olan 30 günlük vizeden 60 günlük çok girişli vizeye kadar tüm seçenekler aşağıdadır.`
                            : "Hizmet bedelleri kişi başıdır, tek seferliktir ve resmî harcı içerir.",
                    ],
                    list: visas.map(priceLine),
                },
                whyUs.length && {
                    h2: "Neden Dubai Vize Hattı?",
                    list: whyUs.map((w) => `${w.title || ""}: ${w.description || w.detail || ""}`.trim()),
                },
                {
                    h2: "Seyahat sigortası, eSIM ve Dubai turları",
                    paras: [
                        "Vize başvurunuza aynı formda seyahat sağlık sigortası, Dubai eSIM paketi ve çöl safarisi turu ekleyebilirsiniz. Sigorta poliçeniz ve eSIM QR kodunuz ödeme sonrası e-postanıza iletilir; birlikte alınan paketlerde indirim uygulanır.",
                    ],
                },
            ].filter(Boolean),
            faq: faq.slice(0, 8),
            jsonld: ["organization", "website"],
        },
        {
            path: "/vize-tipleri",
            priority: "0.9",
            changefreq: "weekly",
            title: `Dubai Vize Fiyatları 2026 | ${BRAND}`,
            description:
                "Dubai (BAE) vize hizmet bedelleri 2026: 30/60 gün tek ve çok girişli vize, çocuk vizesi, uzatma ve ekspres fiyatları. Bedele dahil olanlar ve ödeme koşulları.",
            h1: "Dubai vize hizmet bedelleri",
            intro: [
                "Kalış süreniz, giriş sayınız ve yolcuların yaşına göre hizmet bedeli değişir. Aşağıdaki tutarlar kişi başıdır, tek seferliktir ve resmî harcı da içerir. Türk lirası karşılığı, başvuru anındaki Merkez Bankası döviz satış kuru üzerinden hesaplanır ve başvurunuz oluştuğu anda sabitlenir.",
                "Bedele dahil olanlar: evrak kontrolü, resmî başvurunun yetkili mercilere iletilmesi, süreç takibi ve bilgilendirme, onaylı vizenin dijital teslimi ve uzman danışman desteği.",
            ],
            sections: [
                visas.length && { h2: "Vize tipleri ve bedelleri", list: visas.map(priceLine) },
                {
                    h2: "Ek hizmetler",
                    list: [
                        "Ekspres hizmet: yaklaşık 8 mesai saatinde sonuç (kişi başı ek ücret).",
                        "Anında ekspres vize: aynı gün içinde sonuç (kişi başı ek ücret).",
                        "Aile başvurusu: aynı formda birden fazla yolcu; yolcu sayısına göre indirim otomatik uygulanır.",
                        "18 yaş altı yolcular için indirimli çocuk vizesi bedeli geçerlidir.",
                    ],
                },
                {
                    h2: "Ödeme ve iade",
                    paras: [
                        "Kredi kartı ile 3D Secure ödeme veya banka havalesi/EFT ile ödeyebilirsiniz. Kart bilgileriniz sunucularımızda saklanmaz. Başvuru yetkili mercilere iletilmeden önce iptal ederseniz harç dışındaki kısım iade edilir; dosya resmî sisteme işlendikten sonra harç, sonuç ne olursa olsun geri alınamaz.",
                    ],
                },
            ].filter(Boolean),
            faq: faq.filter((f) => /fiyat|ücret|ödeme|iade|bedel|harç/i.test(f.q)).slice(0, 6),
            jsonld: ["faq", "breadcrumb"],
        },
        {
            path: "/basvuru",
            priority: "0.9",
            changefreq: "monthly",
            title: `Dubai Vize Başvuru Formu | ${BRAND}`,
            description:
                "Dubai vize başvurunuzu online tamamlayın: yolcuları ekleyin, vize tipini seçin, pasaport ve fotoğrafınızı yükleyin, ödemenizi yapın. Aile indirimi otomatik hesaplanır.",
            h1: "Dubai vize başvuru formu",
            intro: [
                "Başvuru sihirbazı dört adımdan oluşur: yolcu bilgileri, vize tipi ve ek hizmet seçimi, belge yükleme ve özet/ödeme. Aynı formda en fazla sekiz yolcu ekleyebilirsiniz; yolcu sayısına göre aile indirimi ve 18 yaş altı için indirimli çocuk vizesi otomatik hesaplanır.",
                "Yüklemeniz gereken belgeler pasaportunuzun kimlik sayfası ve vesikalık fotoğrafınızdır. Uçak bileti ve otel rezervasyonu zorunlu değildir. Pasaportunuzun dönüş tarihinizden itibaren en az 6 ay geçerli olması gerekir; form bu şartı başvuru sırasında kontrol eder.",
                "Yarım kalan başvurunuz taslak olarak saklanır ve size gönderilen bağlantıyla kaldığınız yerden devam edebilirsiniz. Ödemeden sonra takip kodunuz e-posta ve WhatsApp ile iletilir.",
            ],
            sections: [
                docs.length && {
                    h2: "Başvuruda istenen belgeler",
                    list: docs.map((d) => `${d.title}${d.required ? " (zorunlu)" : " (zorunlu değil)"}: ${d.detail}`),
                },
                {
                    h2: "Başvuruya eklenebilen ek hizmetler",
                    list: [
                        "Ekspres hizmet ve anında ekspres vize seçenekleri",
                        "Seyahat sağlık sigortası poliçesi",
                        "Dubai eSIM internet paketi",
                        "Dubai çöl safarisi turu (tarih ve saat seçimiyle)",
                    ],
                },
            ].filter(Boolean),
            faq: faq.filter((f) => /başvuru|belge|form|pasaport/i.test(f.q)).slice(0, 5),
            jsonld: ["breadcrumb"],
        },
        {
            path: "/gerekli-belgeler",
            priority: "0.8",
            changefreq: "monthly",
            title: `Dubai Vizesi Gerekli Belgeler | ${BRAND}`,
            description:
                "Dubai (BAE) vize başvurusu için gereken belgeler: pasaport kimlik sayfası, vesikalık fotoğraf kriterleri. Uçak bileti ve otel rezervasyonu zorunlu değildir.",
            h1: "Dubai vizesi için gereken belgeler",
            intro: [
                "Sadece pasaport ve fotoğrafınızla vizenizi alıyoruz. Dubai vizesi tamamen elektronik düzenlenir; pasaportunuzu kargoya vermenize, vizeniz çıkmadan uçak bileti veya otel rezervasyonu almanıza gerek yoktur.",
            ],
            sections: [
                docs.length && {
                    h2: "Belge listesi",
                    list: docs.map((d) => `${d.title}${d.required ? " (zorunlu)" : " (zorunlu değil)"}: ${d.detail}`),
                },
                photoRules.length && { h2: "Vesikalık fotoğraf kuralları", list: photoRules.map((r) => (typeof r === "string" ? r : `${r.title || ""}: ${r.detail || r.description || ""}`)) },
                {
                    h2: "Pasaport geçerlilik şartı",
                    paras: [
                        "Pasaportunuzun, Dubai'den dönüş tarihinizden itibaren en az 6 ay daha geçerli olması gerekir. Bu süreyi karşılamayan pasaportlarla yapılan başvurular yetkili merciler tarafından reddedilir; bu nedenle başvuru formu geçerlilik süresini önceden kontrol eder.",
                    ],
                },
            ].filter(Boolean),
            faq: faq.filter((f) => /belge|fotoğraf|pasaport|bilet|otel/i.test(f.q)).slice(0, 6),
            jsonld: ["breadcrumb"],
        },
        {
            path: "/hizmetler",
            priority: "0.7",
            changefreq: "monthly",
            title: `Vize Hizmetlerimiz | ${BRAND}`,
            description:
                "Dubai vize başvurusu, aile başvurusu, evrak kontrolü, ekspres vize, vize uzatma ve başvuru takibi hizmetleri tek çatı altında.",
            h1: "Odağımız vize; baştan sona yanınızdayız",
            intro: [
                "Başvuru hazırlığından evrak kontrolüne, ekspres işlemden vize uzatmaya kadar tüm süreç uzman danışmanlarımız tarafından yürütülür. Yetkili özel seyahat acentesiyiz; resmî bir devlet kurumu, konsolosluk ya da BAE göç idaresi değiliz.",
            ],
            sections: [
                services.length && {
                    h2: "Hizmet listesi",
                    list: services.map((s) => `${s.title || s.name || ""}: ${s.description || s.detail || ""}`.trim()),
                },
            ].filter(Boolean),
            faq: faq.filter((f) => /hizmet|ekspres|uzatma|takip/i.test(f.q)).slice(0, 5),
            jsonld: ["breadcrumb"],
        },
        {
            path: "/sss",
            priority: "0.8",
            changefreq: "monthly",
            title: `Dubai Vizesi Sıkça Sorulan Sorular | ${BRAND}`,
            description:
                "Dubai vizesi hakkında sıkça sorulan sorular: işlem süresi, pasaport geçerliliği, ödeme güvenliği, ret durumunda iade ve başvuru takibi.",
            h1: "Dubai vizesi hakkında sıkça sorulan sorular",
            intro: [
                "Başvuru öncesi aklınıza gelebilecek soruları tek sayfada topladık. Aradığınızı bulamazsanız WhatsApp, telefon veya e-posta ile danışmanlarımıza yazabilirsiniz.",
            ],
            sections: [],
            faq,
            jsonld: ["faq", "breadcrumb"],
        },
        {
            path: "/hakkimizda",
            priority: "0.6",
            changefreq: "yearly",
            title: `Hakkımızda | ${BRAND}`,
            description:
                "Dubai Vize Hattı, Birleşik Arap Emirlikleri vize başvurularında uzmanlaşmış, TÜRSAB üyesi A Grubu seyahat acentesi güvencesiyle çalışan bağımsız bir danışmanlık hizmetidir.",
            h1: "Dubai vizesi işini biz üstleniyoruz",
            intro: [
                "Dubai Vize Hattı, Birleşik Arap Emirlikleri vize başvurularına odaklanmış bağımsız bir danışmanlık hizmetidir. Resmî bir devlet kurumu değiliz; başvurunuzu sizin adınıza hazırlar, evraklarınızı tek tek kontrol eder ve yetkili mercilere iletiriz.",
                company.legal_name
                    ? `Hizmet, ${company.legal_name} bünyesinde yürütülür. TÜRSAB üyesi A Grubu seyahat acentesi güvencesiyle çalışıyoruz.`
                    : "TÜRSAB üyesi A Grubu seyahat acentesi güvencesiyle çalışıyoruz.",
            ],
            sections: [
                {
                    h2: "Çalışma şeklimiz",
                    list: [
                        "Belgelerinizi gönderim öncesi kontrol ederiz; eksik veya hatalı belge kaynaklı ret riski azalır.",
                        "Başvurunuzun her adımını takip kodu ile izleyebilirsiniz.",
                        "Onaylı vizeniz PDF olarak e-posta ve WhatsApp ile teslim edilir.",
                        "Vize sonrası seyahat sigortası, eSIM ve tur hizmetleriyle destek sağlarız.",
                    ],
                },
                {
                    h2: "Neden acente üzerinden başvurmak?",
                    paras: [
                        "Dubai vize başvurularında en sık karşılaşılan ret sebepleri; okunmayan pasaport taraması, kriterlere uymayan vesikalık fotoğraf, aktif başka bir vizenin bulunması ve isim yazımındaki tutarsızlıklardır. Başvurunuzu iletmeden önce bu noktaları tek tek kontrol ediyoruz.",
                        "Süreç boyunca tek bir danışman ekibiyle iletişimde kalırsınız. Başvurunuz sonuçlandığında vize belgeniz dijital olarak teslim edilir, dosya numaranızla resmî sistem üzerinden de doğrulayabilirsiniz.",
                    ],
                },
                {
                    h2: "Yasal statümüz",
                    paras: [
                        "Yetkili özel seyahat acentesiyiz; resmî bir devlet kurumu, konsolosluk ya da BAE göç idaresi değiliz. Başvurunuzu sizin adınıza hazırlayıp yetkili mercilere iletiriz. Vize onayı kararı tamamen yetkili mercilere aittir.",
                    ],
                },
            ],
            faq: [],
            jsonld: ["organization", "breadcrumb"],
        },
        {
            path: "/iletisim",
            priority: "0.6",
            changefreq: "yearly",
            title: `İletişim | ${BRAND}`,
            description:
                "Dubai vize başvurunuzla ilgili sorularınız için telefon, WhatsApp veya e-posta ile ulaşın. Ofis adresimiz ve çalışma saatlerimiz bu sayfada.",
            h1: "Hemen bizimle iletişime geçin",
            intro: [
                "Dubai vizeniz, ek hizmetleriniz ve mevcut başvurunuz için danışman ekibimiz yanınızda. İletişim formunu doldurabilir ya da aşağıdaki kanallardan yazabilirsiniz; ofis saatlerinde aynı gün dönüş yapıyoruz.",
            ],
            sections: [
                {
                    h2: "İletişim bilgileri",
                    list: [
                        company.phone && `Telefon: ${company.phone}`,
                        company.email && `E-posta: ${company.email}`,
                        company.address && `Adres: ${company.address}`,
                        company.working_hours && `Çalışma saatleri: ${company.working_hours}`,
                    ].filter(Boolean),
                },
                {
                    h2: "Hangi konularda yardımcı oluyoruz?",
                    list: [
                        "Vize tipi seçimi, kalış süresi ve giriş sayısı danışmanlığı",
                        "Belge kontrolü ve başvuru öncesi uygunluk değerlendirmesi",
                        "Mevcut başvurunuzun durumu ve sonuç takibi",
                        "Ekspres işlem, vize uzatma ve ret sonrası yeniden başvuru",
                        "Seyahat sigortası, eSIM ve Dubai turu talepleri",
                    ],
                },
                {
                    h2: "Dönüş süremiz",
                    paras: [
                        "İletişim formundan gelen talepler ofis saatleri içinde aynı gün yanıtlanır. Acil başvurularda WhatsApp üzerinden yazmanız daha hızlı sonuç verir. Yetkili özel seyahat acentesiyiz; resmî bir devlet kurumu, konsolosluk ya da BAE göç idaresi değiliz.",
                    ],
                },
            ],
            faq: [],
            jsonld: ["organization", "breadcrumb"],
        },
        {
            path: "/takip",
            priority: "0.7",
            changefreq: "monthly",
            title: `Başvuru Takip | ${BRAND}`,
            description:
                "Takip kodunuz ve soyadınızla Dubai vize başvurunuzun durumunu sorgulayın, onaylanan vizenizi PDF olarak indirin.",
            h1: "Başvurunuzun durumunu sorgulayın",
            intro: [
                "Takip kodunuz ve yolculardan birinin soyadı ile başvurunuzun güncel durumunu görüntüleyebilir, onaylanan vizenizi indirebilirsiniz. Takip kodu, ödeme sonrası e-posta ve WhatsApp ile iletilir.",
                "Başvuru durumları sırayla şu şekilde ilerler: başvuru alındı, belge bekleniyor, inceleniyor, onaylandı. Her durum değişikliğinde bilgilendirme mesajı gönderilir.",
            ],
            sections: [
                {
                    h2: "Durum açıklamaları",
                    list: [
                        "Başvuru alındı: kaydınız oluşturuldu, belgeleriniz danışmanlarımızda kontrol sırasında.",
                        "Belge bekleniyor: eksik veya okunamayan bir belge var; size iletilen bağlantıdan yeniden yükleyebilirsiniz.",
                        "İnceleniyor: başvurunuz yetkili mercilere iletildi ve sonuç bekleniyor.",
                        "Onaylandı: vizeniz düzenlendi; PDF olarak takip sayfanızdan indirebilir, e-postanızdan da ulaşabilirsiniz.",
                    ],
                },
                {
                    h2: "Takip kodunuzu bulamıyorsanız",
                    paras: [
                        "Takip kodu, ödeme onayı e-postasında ve WhatsApp bildiriminde yer alır. Kodunuza ulaşamıyorsanız başvuru sırasında kullandığınız e-posta ve soyadınızla \"Başvurularım\" ekranından giriş yapabilir ya da iletişim kanallarımızdan bize yazabilirsiniz.",
                    ],
                },
            ],
            faq: faq.filter((f) => /takip|durum|sonuç/i.test(f.q)).slice(0, 4),
            jsonld: ["breadcrumb"],
        },
        {
            path: "/esim",
            priority: "0.7",
            changefreq: "monthly",
            title: `Dubai eSIM Paketleri | ${BRAND}`,
            description:
                "Dubai ve BAE için eSIM paketleri: QR kod ile iki dakikada kurulum, Türkiye numaranız açık kalır, roaming faturası sürprizi yok.",
            h1: "Dubai'de ilk dakikadan itibaren internet",
            intro: [
                "Roaming faturası sürprizi yok. eSIM paketinizi vize başvurunuz sırasında seçtiğinizde QR kodunuz ödeme sonrası e-postanıza gelir; uçaktan indiğiniz anda internetiniz hazır olur.",
                "eSIM, telefonunuzdaki dijital SIM'dir; fiziksel kart takmanız gerekmez. Türkiye numaranız açık kalmaya devam eder, veri trafiği eSIM üzerinden akar.",
            ],
            sections: [
                {
                    h2: "Kurulum adımları",
                    list: [
                        "Ödeme sonrası e-postanıza gelen QR kodu açın.",
                        "Telefon ayarlarından mobil veri bölümüne girip eSIM ekleyin.",
                        "QR kodu okutun ve paketi yükleyin.",
                        "Dubai'ye indiğinizde eSIM hattını veri hattı olarak seçin.",
                        "Türkiye numaranızda veri dolaşımını kapalı tutun.",
                    ],
                },
                {
                    h2: "Hangi paketi seçmeliyim?",
                    paras: [
                        "Kısa şehir turlarında harita, mesajlaşma ve sosyal medya için küçük veri paketleri yeterlidir. Video izleme, canlı yayın veya telefonunuzu hotspot olarak kullanma ihtiyacınız varsa yüksek kapasiteli ya da sınırsız paketleri tercih edin.",
                        "Paket süresi, Dubai'ye girişinizden itibaren başlar ve satın aldığınız gün sayısı kadar devam eder. Aynı başvurudaki her yolcu için ayrı eSIM alabilirsiniz.",
                    ],
                },
                {
                    h2: "eSIM uyumluluğu",
                    paras: [
                        "eSIM, iPhone XR ve sonrası ile Samsung Galaxy S20 ve sonrası gibi eSIM destekli cihazlarda çalışır. Telefonunuzun operatör kilidi açık olmalıdır. Cihazınızın uyumlu olup olmadığından emin değilseniz satın almadan önce bize yazabilirsiniz.",
                    ],
                },
            ],
            faq: [],
            jsonld: ["breadcrumb"],
        },
        {
            path: "/seyahat-sigortasi",
            priority: "0.7",
            changefreq: "monthly",
            title: `Dubai Seyahat Sigortası | ${BRAND}`,
            description:
                "Dubai seyahat sağlık sigortası neyi kapsar, zorunlu mu, kaç gün geçerli? BAE genelinde geçerli poliçenin kapsamı ve başvuruya nasıl eklendiği.",
            h1: "Dubai seyahat sigortası hakkında bilmeniz gerekenler",
            intro: [
                "Seyahat sağlık sigortası Dubai vize başvurusu için zorunlu bir belge değildir; ancak Birleşik Arap Emirlikleri'nde sağlık masraflarının yüksekliği bu poliçeyi düşünmeye değer kılar.",
                "Poliçeler seyahat sürenize göre gün bazlı düzenlenir ve BAE'nin yedi emirliğinin tamamında geçerlidir. Vize başvurunuz sırasında seçtiğinizde poliçeniz ödeme sonrası düzenlenir ve PDF olarak e-postanıza gönderilir.",
            ],
            sections: [
                {
                    h2: "Poliçe kapsamı",
                    list: [
                        "Ani hastalık ve kaza sonucu acil tıbbi tedavi masrafları",
                        "Acil tıbbi nakil ve ülkeye geri dönüş masrafları",
                        "Geniş kapsamlı poliçelerde bagaj kaybı ve seyahat kesintisi teminatları",
                        "Aynı başvurudaki her yolcu için ayrı poliçe düzenlenmesi",
                    ],
                },
                {
                    h2: "Poliçe süresi nasıl seçilir?",
                    paras: [
                        "Poliçenin geçerlilik süresi seyahat tarihlerinizi kapsamalıdır. Başvuru formunda yalnızca seyahat süreniz ve vize sürenizle uyumlu poliçeler listelenir; kapsamı yetmeyen seçenekler otomatik olarak devre dışı kalır.",
                        "Poliçeniz ödemeniz tamamlandıktan sonra düzenlenir ve PDF olarak e-postanıza gönderilir. Sigorta, vize başvurusundan bağımsız olarak da satın alınabilir.",
                    ],
                },
            ],
            faq: [],
            jsonld: ["breadcrumb"],
        },
        {
            path: "/dubai-turlari",
            priority: "0.6",
            changefreq: "monthly",
            title: `Dubai Çöl Safarisi | ${BRAND}`,
            description:
                "Dubai çöl safarisi: 4×4 Land Cruiser ile kumul turu, kum sörfü, deve turu ve Bedevi kampında açık büfe akşam yemeği. Otelden alınış 15:00, dönüş 21:00 – 22:00.",
            h1: "Dubai Çöl Safarisi",
            intro: [
                "Dubai çöl safarisi turunu tarih seçerek sepete ekleyin; rezervasyonunuzu biz yapar, kupon ve buluşma bilgilerini e-postanıza göndeririz.",
                "Tur programı kumul safarisi, deve gezisi, kum sörfü ve Arap kampında akşam yemeğini kapsar. Otelinizden alınıp tur sonunda geri bırakılırsınız.",
                "Turu vize başvurunuza ekleyebilir ya da tek başına satın alabilirsiniz. Ödemeniz tamamlandığında rezervasyonunuz oluşturulur; buluşma saati ve rehber iletişim bilgisi seyahatinizden önce paylaşılır.",
            ],
            sections: [
                {
                    h2: "Tur programında neler var?",
                    list: [
                        "15:00'te otelinizden alınış, çöl bölgesine yaklaşık 40 dakika yolculuk",
                        "30 dakika 4×4 Land Cruiser ile kumul safarisi (dune bashing)",
                        "İsteğe bağlı 30 dakika ATV safari (+40 USD)",
                        "Kum sörfü (sandboarding) ve çölün en iyi fotoğraf noktalarında mola",
                        "Gün batımından sonra Bedevi kampında kısa deve turu",
                        "Açık büfe akşam yemeği, ateş ve dans gösterileri, kadın misafirlere kına",
                        "21:00 – 22:00 arasında otelinize dönüş",
                    ],
                },
                {
                    h2: "Rezervasyon nasıl yapılır?",
                    paras: [
                        "Turu seçtikten sonra tarih ve saat dilimi belirlemeniz gerekir; tarih, seyahat tarihleriniz arasında olmalıdır. Kişi sayısını arttırıp azaltabilir, aynı siparişte vize, seyahat sigortası ve eSIM ile birleştirebilirsiniz.",
                        "Tur ücreti kişi başıdır. Rezervasyon onayınız ve kupon bilgileriniz ödeme sonrası e-posta ile iletilir; iptal ve değişiklik talepleri için iade koşulları sayfamızdaki kurallar geçerlidir.",
                    ],
                },
            ],
            faq: [],
            jsonld: ["breadcrumb"],
        },
        {
            path: "/gelismeler",
            priority: "0.7",
            changefreq: "weekly",
            title: `Dubai'den Haberler ve Vize Rehberi | ${BRAND}`,
            description:
                "Dubai vize kuralları, pasaport süresi, vize uzatma, seyahat sigortası ve ret sebepleri hakkında güncel rehber yazıları.",
            h1: "Dubai vize ve seyahat rehberi",
            intro: [
                "Dubai'den haberler, vize kuralları, aktiviteler ve güncel duyurular. Yazılarımız vize ekibimizin başvurularda sık karşılaştığı sorulardan yola çıkılarak hazırlanır.",
            ],
            sections: [
                articles.length && {
                    h2: "Yazılar",
                    list: articles.map((a) => `${a.title}: ${a.excerpt || ""}`.trim()),
                },
            ].filter(Boolean),
            faq: [],
            jsonld: ["breadcrumb"],
        },
        {
            path: "/guvenlik",
            priority: "0.5",
            changefreq: "yearly",
            title: `Güvenlik ve Veri Koruma | ${BRAND}`,
            description:
                "256-bit SSL, 3D Secure ve PCI-DSS ödeme altyapısı, imzalı belge bağlantıları, 90 gün sonra imha ve KVKK uyumu: bilgilerinizin nasıl korunduğu.",
            h1: "Güvenlik ve veri koruma",
            intro: [
                "Pasaport bilgilerinizi ve ödemenizi bize emanet ediyorsunuz. Karşılığında uyguladığımız teknik önlemlerin tamamı bu sayfada açık dille yazılı: şifreli bağlantı, kart bilgisi saklamayan ödeme akışı, süreli belge bağlantıları, 90 günlük saklama süresi ve şifresiz tek kullanımlık kodla giriş.",
            ],
            sections: [
                {
                    h2: "Bağlantı ve site güvenliği",
                    paras: [
                        "Sitenin tamamı ve başvuru formu 256-bit SSL/TLS ile şifrelenir; HSTS başlığı sayesinde tarayıcınız şifresiz bağlantı kurmaz. Sunucu yanıtlarında içerik türü zorlaması, çerçeveleme (clickjacking) koruması, referans politikası ve kamera/mikrofon/konum izinlerini kapatan başlıklar tanımlıdır.",
                        "Yönetim arayüzünün API şeması dışarıya kapalıdır; başvuru, iletişim ve kod gönderimi uçlarında IP ve e-posta bazlı hız sınırları uygulanır.",
                    ],
                },
                {
                    h2: "Ödeme güvenliği",
                    paras: [
                        "Kart ödemeleri PCI-DSS sertifikalı ödeme kuruluşunun güvenli sayfasında alınır; kart numarası, son kullanma tarihi ve CVV sunucularımıza hiç ulaşmaz. Son onay bankanızın 3D Secure ekranında verilir.",
                        "Havale/EFT tercih edenler için hesap bilgileri yalnızca kendi sitemizde gösterilir. IBAN değişikliği bildiren mesajlara güvenmeyin, ödeme öncesi bize doğrulatın.",
                    ],
                },
                {
                    h2: "Belgelerinizin güvenliği",
                    paras: [
                        "Pasaport taramanız ve fotoğrafınız erişimi kısıtlı depolamada tutulur; dosyalar yalnızca imzalı ve süresi dolan bağlantılarla açılabilir, herkese açık bir adres yoktur.",
                        "Saklama süresi 90 gündür; süre dolduğunda belgelerin içeriği geri getirilemeyecek şekilde otomatik silinir.",
                    ],
                },
                {
                    h2: "Hesap ve oturum güvenliği",
                    paras: [
                        "Müşteri hesabı ve yönetim panelinde şifre kullanılmaz; giriş e-postaya gelen 6 haneli tek kullanımlık kodla yapılır. Kodlar kısa süre geçerlidir, tek kullanımlıktır, düz metin saklanmaz ve hatalı denemelerde kilitlenir.",
                    ],
                },
                {
                    h2: "Yetki, mevzuat ve şeffaflık",
                    paras: [
                        "Hizmet TÜRSAB üyesi A Grubu seyahat acentesi olarak sunulur; vize kararı Dubai göçmenlik makamlarına (GDRFA) aittir. Kişisel verileriniz KVKK kapsamında işlenir, reklam amacıyla üçüncü taraflara satılmaz.",
                    ],
                },
                {
                    h2: "Dolandırıcılığa karşı 4 kontrol",
                    paras: [
                        "Ödeme yalnızca dubaivizehatti.com üzerinden veya bize ait banka hesabına yapılır; adres çubuğundaki kilit simgesini ve alan adının doğru yazıldığını kontrol edin; sizden şifre, kart CVV'si veya SMS kodu istemeyiz; şüpheli mesajlarda işlem yapmadan önce iletişim sayfamızdaki numaradan doğrulatın.",
                    ],
                },
            ],
            faq: [],
            jsonld: ["breadcrumb"],
        },
        {
            path: "/kvkk",
            priority: "0.3",
            changefreq: "yearly",
            title: `KVKK Aydınlatma Metni | ${BRAND}`,
            description:
                "Kişisel verilerinizin hangi amaçlarla işlendiği, kimlerle paylaşıldığı, saklama süreleri ve KVKK kapsamındaki haklarınız.",
            h1: "KVKK aydınlatma metni ve gizlilik politikası",
            intro: [
                "Vize başvurusu sürecinde paylaştığınız kimlik, pasaport, iletişim ve ödeme bilgileri yalnızca başvurunuzun hazırlanması, yetkili mercilere iletilmesi ve size bilgilendirme yapılması amacıyla işlenir.",
                legal.affiliation || "",
            ].filter(Boolean),
            sections: [
                {
                    h2: "1. Hangi verileri topluyoruz?",
                    paras: [
                        "Adınız, soyadınız, doğum tarihiniz, pasaport bilgileriniz, iletişim bilgileriniz, seyahat tarihleri ve yüklediğiniz belgeler (pasaport taraması ve biyometrik fotoğraf). Bu veriler yalnızca vize başvurunuzun hazırlanması ve takibi için kullanılır.",
                    ],
                },
                {
                    h2: "2. Verilerinizi kimlerle paylaşıyoruz?",
                    paras: [
                        "Başvurunuzun işleme alınabilmesi için yetkili merciler ve başvuru aracılık platformlarıyla paylaşılır. Reklam veya pazarlama amacıyla üçüncü taraflara veri satmayız.",
                    ],
                },
                {
                    h2: "3. Ödeme bilgileri",
                    paras: [
                        "Kart bilgileriniz sunucularımıza hiçbir şekilde kaydedilmez. Ödeme işlemi uluslararası ödeme kuruluşunun güvenli sayfasında gerçekleşir; tarafımıza yalnızca işlem sonucunu gösteren referans bilgisi iletilir.",
                    ],
                },
                {
                    h2: "4. Saklama süresi",
                    paras: [
                        "Başvuru kayıtları yasal yükümlülüklerimiz süresince saklanır, ardından silinir veya anonim hâle getirilir.",
                    ],
                },
                {
                    h2: "5. Haklarınız",
                    paras: [
                        "KVKK kapsamında verilerinize erişme, düzeltme, silme ve işlenmesine itiraz etme hakkına sahipsiniz. Taleplerinizi iletişim sayfamızdaki e-posta adresine iletebilirsiniz.",
                    ],
                },
                {
                    h2: "6. İade koşulları",
                    paras: [
                        "Başvurunuz yetkili merciler tarafından reddedilirse, resmî harcın dışında kalan hizmet bedelimiz iade edilir. Başvuru gönderilmeden önce yapılan iptal taleplerinde ödeme tamamen iade edilir.",
                    ],
                },
            ],
            faq: [],
            jsonld: ["breadcrumb"],
        },
        {
            path: "/gizlilik-politikasi",
            priority: "0.3",
            changefreq: "yearly",
            title: `Gizlilik Politikası | ${BRAND}`,
            description:
                "Dubai Vize Hattı gizlilik politikası: işlenen veri kategorileri, hukuki sebepler, yurt içi ve yurt dışı aktarım, saklama süreleri ve haklarınız.",
            h1: "Gizlilik politikası",
            intro: legalIntro("privacy_policy").length
                ? legalIntro("privacy_policy")
                : [
                      "Bu politika, hangi verileri hangi hukuki sebeple işlediğimizi, kimlerle paylaştığımızı, ne kadar süre sakladığımızı ve haklarınızı nasıl kullanabileceğinizi açıklar.",
                  ],
            sections: legalSections("privacy_policy"),
            faq: [],
            jsonld: ["breadcrumb"],
        },
        {
            path: "/iade-kosullari",
            priority: "0.3",
            changefreq: "yearly",
            title: `İade ve İptal Koşulları | ${BRAND}`,
            description:
                "Dubai vize başvuruları, tur ve aktivite rezervasyonlarında iptal, iade, ret, no-show ve mücbir sebep koşulları.",
            h1: "İade ve iptal koşulları",
            intro: legalIntro("refund_terms").length
                ? legalIntro("refund_terms")
                : [
                      "Vize danışmanlığı, tur/aktivite ve transfer hizmetlerinde iptal, iade ve ret durumlarında uygulanan kuralların tamamı bu sayfada yer alır.",
                  ],
            sections: legalSections("refund_terms"),
            faq: [],
            jsonld: ["breadcrumb"],
        },
        {
            path: "/hizmet-sozlesmesi",
            priority: "0.3",
            changefreq: "yearly",
            title: `Mesafeli Hizmet Sözleşmesi | ${BRAND}`,
            description:
                "Dubai Vize Hattı hizmet sözleşmesi: kapsam, yükümlülükler, ödeme, aracılık statüsü, cayma hakkı ve uyuşmazlık çözümü.",
            h1: "Şartlar ve mesafeli hizmet sözleşmesi",
            intro: legalIntro("service_terms").length
                ? legalIntro("service_terms")
                : [
                      "Online başvuru sırasında kurulan sözleşmenin tarafları, kapsamı, aracılık statüsü ve karşılıklı yükümlülükler bu metinde tanımlanır.",
                  ],
            sections: legalSections("service_terms"),
            faq: [],
            jsonld: ["breadcrumb"],
        },
        {
            path: "/ticari-ileti-onami",
            priority: "0.3",
            changefreq: "yearly",
            title: `Ticari Elektronik İleti Onamı | ${BRAND}`,
            description:
                "Kampanya, indirim ve fırsat bildirimleri için ticari elektronik ileti onayının kapsamı ve izni geri alma adımları.",
            h1: "Ticari elektronik ileti onam formu",
            intro: legalIntro("marketing_consent").length
                ? legalIntro("marketing_consent")
                : [
                      "Kampanya ve fırsat bildirimleri için verdiğiniz onayın kapsamı, işlenen bilgiler ve onayı geri alma yolları bu sayfada açıklanır.",
                  ],
            sections: legalSections("marketing_consent"),
            faq: [],
            jsonld: ["breadcrumb"],
        },
    ];
}

module.exports = { buildStaticPages, BRAND };
