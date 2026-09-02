{
  "meta": {
    "project": "VizeAtlas Dubai",
    "goal": "Üretimde çalışan vize başvuru platformunun (public site + başvuru sihirbazı + müşteri hesabı + admin) görsel/etkileşim katmanını Google Stitch benzeri AI-native, modern ve güven veren bir estetikle yenilemek. API/state/form alanları ve mevcut data-testid’ler ASLA değişmeyecek.",
    "mode": "light-only",
    "language": "tr-TR",
    "non_negotiables": [
      "Frontend/backend sözleşmesi değişmeyecek (API çağrıları, state akışları, form field isimleri).",
      "Mevcut data-testid attribute’ları korunacak; yeni eklenen tüm interaktif/ana bilgi öğelerine data-testid eklenecek.",
      "Token mimarisi korunacak: index.css içindeki CSS değişken isimleri aynı kalacak; sadece değer/ölçek rafine edilebilir.",
      "Gradient kısıtları: viewport’un %20’sini aşmayacak; mavi-mor / mor-pembe gibi doygun koyu gradientler YASAK.",
      "transition: all YASAK; sadece opacity/transform ve hedefli property transition.",
      "Mobile-first; dokunma hedefi min 44x44px; WCAG AA kontrast."
    ]
  },

  "brand_personality": {
    "attributes": [
      "Güven veren (şeffaf ücret, resmi süreç hissi)",
      "Hızlı ve rehberlik eden (adım adım, hata önleyici)",
      "Premium ama sade (Dubai hissi: temiz, ferah, yüksek kalite)",
      "AI-native (OCR/otomatik doldurma gibi akıllı özellikler görünür ama abartısız)"
    ],
    "visual_metaphors": [
      "‘Resmi evrak’ netliği: ince çizgiler, düzenli grid, güçlü tipografik hiyerarşi",
      "‘Dubai modernliği’: geniş boşluk, cam/ışık hissi veren çok hafif yüzey parıltıları",
      "‘BAE bayrağı’ vurguları: yeşil ana aksiyon, kırmızı kritik uyarı/aksiyon"
    ]
  },

  "design_tokens": {
    "note": "Token isimleri korunur. Aşağıdaki değerler rafine öneridir; uygulama index.css :root altında yapılır.",
    "css_variables": {
      "--background": "40 18% 98%",
      "--foreground": "210 22% 7%",
      "--card": "0 0% 100%",
      "--card-foreground": "210 22% 7%",
      "--popover": "0 0% 100%",
      "--popover-foreground": "210 22% 7%",

      "--primary": "152 78% 22%",
      "--primary-foreground": "0 0% 100%",

      "--secondary": "150 18% 95%",
      "--secondary-foreground": "210 22% 10%",
      "--muted": "210 16% 95%",
      "--muted-foreground": "214 14% 30%",

      "--accent": "352 78% 38%",
      "--accent-foreground": "0 0% 100%",
      "--destructive": "352 78% 38%",
      "--destructive-foreground": "0 0% 100%",

      "--border": "214 18% 86%",
      "--input": "214 18% 86%",
      "--ring": "152 78% 22%",

      "--radius": "0.9rem",

      "--navy": "210 24% 8%",
      "--sand-surface": "150 22% 95%",
      "--cloud": "210 16% 96%",
      "--gold": "352 78% 40%",
      "--teal-hover": "152 82% 18%",
      "--success": "152 82% 26%",

      "--brand-green": "152 78% 22%",
      "--brand-red": "352 78% 38%",
      "--brand-black": "210 24% 8%",
      "--brand-white": "0 0% 100%",

      "--status-success": "152 82% 26%",
      "--status-warning": "34 72% 38%",
      "--status-info": "206 72% 27%",
      "--status-danger": "352 78% 38%",

      "--shadow-soft": "0 14px 34px rgba(11, 15, 20, 0.10)",
      "--shadow-card": "0 10px 24px rgba(11, 15, 20, 0.08)",
      "--shadow-float": "0 22px 60px rgba(11, 15, 20, 0.14)",
      "--focus-ring": "0 0 0 4px rgba(11, 107, 58, 0.22)"
    },
    "gradients": {
      "allowed_usage": [
        "Sadece hero/section background dekoru (max %20 viewport)",
        "Dekoratif overlay (noise ile)"
      ],
      "recipes": {
        "hero_glow": "radial-gradient(1000px circle at 12% 0%, hsl(var(--brand-green) / 0.12), transparent 58%), radial-gradient(760px circle at 88% 4%, hsl(var(--brand-red) / 0.07), transparent 62%), linear-gradient(180deg, hsl(var(--sand-surface) / 0.9) 0%, transparent 70%)",
        "section_tint": "linear-gradient(180deg, hsl(var(--cloud)) 0%, hsl(var(--background)) 70%)"
      },
      "prohibited": [
        "blue-500 to purple-600",
        "purple-500 to pink-500",
        "green-500 to blue-500",
        "red to pink",
        "Herhangi bir koyu/doygun gradientin küçük UI öğelerinde kullanımı"
      ]
    },
    "spacing_scale": {
      "base": "4px",
      "tokens": {
        "space-1": "4px",
        "space-2": "8px",
        "space-3": "12px",
        "space-4": "16px",
        "space-5": "20px",
        "space-6": "24px",
        "space-8": "32px",
        "space-10": "40px",
        "space-12": "48px",
        "space-14": "56px",
        "space-16": "64px"
      },
      "rule": "Mevcut .section padding’leri korunur; içerik blokları arası boşluklar 24–40px bandında tutulur (mobilde 16–24px)."
    },
    "radius_scale": {
      "rule": "Genel radius --radius (0.9rem) korunur. İç bileşenlerde: input/button 12px, kart 16px, modal/sheet 18px."
    }
  },

  "typography": {
    "fonts": {
      "heading": {
        "css_var": "--font-heading",
        "recommended": "Montserrat (mevcut) veya Space Grotesk (alternatif)",
        "note": "Türkçe karakter desteği zorunlu. Eğer Montserrat kalacaksa ağırlık dağılımını rafine edin: 700/800 başlık, 600 alt başlık."
      },
      "body": {
        "css_var": "--font-body",
        "recommended": "Figtree (mevcut) veya IBM Plex Sans (alternatif)",
        "note": "Body’de 400/500; form label 600."
      },
      "mono": {
        "css_var": "--font-mono",
        "recommended": "IBM Plex Mono (mevcut)",
        "usage": "Referans kodu/sipariş numarası, kur notu, küçük teknik metinler"
      }
    },
    "type_scale_tailwind": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl",
      "h2": "text-base md:text-lg",
      "body": "text-sm sm:text-base",
      "small": "text-xs sm:text-sm"
    },
    "line_height": {
      "headings": "leading-[1.05]",
      "body": "leading-6",
      "dense_tables": "leading-5"
    }
  },

  "layout_and_grid": {
    "container": {
      "class": ".container-page",
      "current": "max-w-6xl px-4 sm:px-6",
      "guidance": "Public sayfalarda 12 kolon hissi: desktop’ta 2/3 + 1/3 split (içerik + sticky özet). Mobilde tek kolon."
    },
    "page_patterns": {
      "public_marketing": {
        "hero": "Z-pattern: sol metin + sağ görsel/örnek vize kartı; mobilde önce metin sonra kart.",
        "sections": "Bento grid (2x2 veya 3x2) ile güven unsurları + hizmetler.",
        "cta": "Sayfa içinde 2 ana CTA: ‘Hemen Başvur’ ve ‘Ücretsiz Ön Değerlendirme’."
      },
      "wizard_apply": {
        "desktop": "Sol: stepper + form (8/12). Sağ: sticky fiyat özeti + güven rozetleri (4/12).",
        "mobile": "Üstte kompakt stepper; altta form; fiyat özeti ‘drawer’ veya sayfa içi yapışkan alt bar (min 56px)."
      },
      "admin": {
        "desktop": "Sol sidebar (sheet/collapsible), üstte sticky toolbar (filtre + arama + aksiyon).",
        "density": "Tablo satır yüksekliği 44–52px; kritik aksiyonlar sağda sabit."
      }
    }
  },

  "components": {
    "component_path": {
      "shadcn_primary": [
        "/app/frontend/src/components/ui/button.jsx",
        "/app/frontend/src/components/ui/card.jsx",
        "/app/frontend/src/components/ui/tabs.jsx",
        "/app/frontend/src/components/ui/badge.jsx",
        "/app/frontend/src/components/ui/input.jsx",
        "/app/frontend/src/components/ui/textarea.jsx",
        "/app/frontend/src/components/ui/select.jsx",
        "/app/frontend/src/components/ui/dialog.jsx",
        "/app/frontend/src/components/ui/sheet.jsx",
        "/app/frontend/src/components/ui/drawer.jsx",
        "/app/frontend/src/components/ui/progress.jsx",
        "/app/frontend/src/components/ui/table.jsx",
        "/app/frontend/src/components/ui/skeleton.jsx",
        "/app/frontend/src/components/ui/tooltip.jsx",
        "/app/frontend/src/components/ui/accordion.jsx",
        "/app/frontend/src/components/ui/calendar.jsx",
        "/app/frontend/src/components/ui/sonner.jsx"
      ],
      "existing_shared_components_to_style": [
        "Navbar",
        "Footer",
        "SiteLayout",
        "AdminLayout",
        "PricingTabs",
        "IconCards",
        "Testimonials",
        "SampleVisa",
        "AuthorityStrip",
        "GdrfaBadge",
        "TursabBadge",
        "FileDropzone",
        "StatusBadge",
        "StoreCheckout",
        "FxNote",
        "VisaGuideLinks",
        "BrandMark",
        "WhatsAppButton",
        "PreEvaluation"
      ]
    },

    "button_system": {
      "variants": {
        "primary": {
          "use": "Ana CTA (Hemen Başvur, Ödemeye Geç)",
          "tailwind": "bg-primary text-primary-foreground hover:bg-[hsl(var(--teal-hover))] shadow-[var(--shadow-card)]",
          "motion": "hover: translateY(-1px) + shadow-soft; active: scale(0.98)",
          "a11y": "focus-visible: box-shadow var(--focus-ring)",
          "data_testid": "Örn: data-testid=\"primary-cta-button\""
        },
        "secondary": {
          "use": "İkincil CTA (Ücretsiz Ön Değerlendirme)",
          "tailwind": "bg-secondary text-secondary-foreground hover:bg-secondary/70 border border-border",
          "motion": "hover: border-primary/40"
        },
        "ghost": {
          "use": "Navbar link/ikon aksiyonları",
          "tailwind": "bg-transparent hover:bg-muted text-foreground"
        },
        "destructive": {
          "use": "Sil/iptal",
          "tailwind": "bg-destructive text-destructive-foreground hover:bg-destructive/90"
        }
      },
      "sizes": {
        "sm": "h-9 px-3 text-sm",
        "md": "h-11 px-4 text-sm",
        "lg": "h-12 px-5 text-base"
      },
      "rule": "Butonlarda transition sadece background-color, box-shadow, border-color, opacity için verilecek; transform transition ayrı (duration-150/200)."
    },

    "card_system": {
      "base": "card-surface",
      "hoverable": "card-hoverable",
      "patterns": {
        "pricing_card": {
          "layout": "Başlık + fiyat + dahil olanlar + teslim süresi + CTA + şeffaf ücret notu",
          "details": "‘Devlet harcı’ ve ‘Hizmet bedeli’ ayrı satır; toplam en altta.",
          "micro": "hover’da border-primary/40 + shadow-soft; seçili kartta ring-2 ring-primary/30",
          "data_testid": "pricing-option-card"
        },
        "trust_card": {
          "layout": "Rozet/ikon + kısa başlık + 1 cümle açıklama",
          "style": "Muted yüzey (bg-secondary/60) + ince border"
        }
      }
    },

    "forms_and_inputs": {
      "rules": [
        "Label her zaman görünür (placeholder label yerine geçmez).",
        "Hata mesajı: text-sm, status-danger rengi, input border status-danger/40 + focus ring kırmızı değil (ring primary kalsın, hata border ile).",
        "Yükleme: input disabled + skeleton satırı; form submit butonu loading state (spinner)"
      ],
      "input_tailwind": "h-11 rounded-[12px] bg-card border-input focus-visible:ring-0 focus-visible:shadow-[var(--focus-ring)]",
      "textarea_tailwind": "min-h-[96px] rounded-[12px]",
      "select": "shadcn Select kullan; native select yok",
      "calendar": "Tarih seçimi gereken yerlerde shadcn Calendar + Popover"
    },

    "stepper_apply_wizard": {
      "structure": "5–7 adım: Yolcular → Belgeler → Detaylar → Ek Hizmetler → Ödeme → Takip",
      "desktop": "Sol üstte yatay stepper + altında form; sağda sticky özet",
      "mobile": "Üstte yatay scroll stepper (ScrollArea) + altta form",
      "visual": {
        "completed": "Badge/ikon + muted connector",
        "current": "primary ring + daha büyük nokta",
        "upcoming": "border + muted"
      },
      "shadcn": ["progress.jsx", "badge.jsx", "scroll-area.jsx", "separator.jsx"],
      "data_testid": "apply-stepper"
    },

    "timeline_order_status": {
      "use": "/siparis/:reference ve /takip",
      "pattern": "Dikey timeline: 5 adım (Alındı, İncelemede, Evrak Bekleniyor, Onaylandı, PDF Hazır) + her adımda tarih/saat + kısa açıklama",
      "components": ["badge.jsx", "card.jsx", "separator.jsx", "tooltip.jsx"],
      "micro": "Yeni güncelleme geldiğinde ilgili adım kısa ‘pulse’ (opacity) animasyonu (prefers-reduced-motion’a saygı)",
      "data_testid": "order-status-timeline"
    },

    "pre_evaluation_wizard": {
      "home_widget": "Ana sayfada 3 soruluk mini wizard: 1 ekran = 1 soru (radio/select), en sonda skor + lead form",
      "score_ui": "Progress + renk kodu: düşük=warning, orta=info, yüksek=success; metinle destekle (renge bağımlı olma)",
      "components": ["card.jsx", "radio-group.jsx", "select.jsx", "progress.jsx", "dialog.jsx"],
      "data_testid": "pre-evaluation-wizard"
    },

    "file_upload_dropzone": {
      "use": "Pasaport/fotoğraf yükleme + admin PDF yükleme",
      "pattern": "Büyük dropzone (min-h 140px) + dosya listesi + durum (yükleniyor/başarılı/hata)",
      "style": "bg-secondary/50 + dashed border-border; hover’da border-primary/40",
      "micro": "drag enter’da hafif scale(1.01) + border vurgusu",
      "data_testid": "file-dropzone"
    },

    "cross_sell_esim_insurance": {
      "pattern": "Apply akışında ‘Ek Hizmetler’ adımında 2 kart: eSIM ve Sigorta; tarih seçimine göre uygunluk + paket indirimi etiketi",
      "components": ["card.jsx", "switch.jsx", "badge.jsx", "calendar.jsx", "tabs.jsx"],
      "pricing": "%10 paket indirimi badge (accent değil; success/primary tonlarıyla) — kırmızı sadece kritik uyarı/iptal için",
      "data_testid": "cross-sell-section"
    },

    "admin_table_and_filters": {
      "pattern": "Üst toolbar: arama (Command veya Input), durum filtre Tabs, tarih filtre Calendar, export/refresh butonları",
      "table": "shadcn Table + sticky header; satır hover bg-muted/60",
      "status_badges": {
        "submitted": "bg-secondary text-foreground",
        "reviewing": "bg-[hsl(var(--status-info)/0.12)] text-[hsl(var(--status-info))]",
        "approved": "bg-[hsl(var(--status-success)/0.12)] text-[hsl(var(--status-success))]",
        "rejected": "bg-[hsl(var(--status-danger)/0.12)] text-[hsl(var(--status-danger))]",
        "cancelled": "bg-muted text-muted-foreground"
      },
      "loading": "Skeleton satırları (8–12 row) + toolbar skeleton",
      "empty_state": "Card içinde: başlık + açıklama + ‘Filtreleri Sıfırla’ ghost button",
      "data_testid": "admin-applications-table"
    }
  },

  "page_blueprints": {
    "priority_order": [
      "1) / (Home) — reklam trafiği ilk temas",
      "2) /basvuru (Apply wizard) — dönüşüm",
      "3) /siparis/:reference ve /takip — güven + destek yükünü azaltır",
      "4) /hesabim — tekrar kullanım",
      "5) Admin — operasyon verimliliği",
      "6) SEO rehber sayfaları — okunabilirlik + iç link"
    ],
    "home": {
      "hero": {
        "layout": "Sol: H1 + kısa güven cümlesi + 2 CTA; Sağ: ‘Örnek Vize’ kartı + mini fiyat özeti",
        "background": "hero-glow + noise-overlay (çok düşük opaklık)",
        "trust": "Hero altında AuthorityStrip + partner logoları marquee",
        "data_testid": "home-hero"
      },
      "sections": [
        "Fiyatlar (PricingTabs) — şeffaf ücret kırılımı + kur notu",
        "Nasıl Çalışır (3-5 adım) — timeline/stepper görseli",
        "Ücretsiz Ön Değerlendirme (mini wizard embed)",
        "Yorumlar + örnek vize + SSS kısa"
      ]
    },
    "apply": {
      "sticky_summary": "Sağ panel: toplam, yolcu sayısı, ek hizmetler, kur notu, güven rozetleri; mobilde alt sticky bar + ‘Detay’ Drawer",
      "ocr": "Pasaport OCR sonrası otomatik doldurma: form alanlarında ‘AI ile dolduruldu’ küçük badge + ‘Geri Al’ link",
      "data_testid": "apply-page"
    },
    "order_status": {
      "hero": "Sipariş referansı (mono) + durum badge + WhatsApp destek butonu",
      "timeline": "Dikey timeline + gerekli aksiyonlar (evrak yükle vb.)",
      "data_testid": "order-status-page"
    },
    "seo_guides": {
      "reading": "Geniş satır uzunluğu kontrolü: prose benzeri sınıflar; içerik kartları; iç linkler (VisaGuideLinks)",
      "toc": "Desktop’ta sağda sticky içerik listesi (ScrollArea)"
    },
    "admin": {
      "layout": "AdminLayout: sidebar + üst toolbar; yoğun ekranlarda iki satırlı toolbar (mobilde Sheet)",
      "detail": "Başvuru detayında: sol içerik (form verileri) + sağ aksiyon paneli (durum güncelle, PDF yükle, WhatsApp gönder)"
    }
  },

  "motion_and_microinteractions": {
    "durations": {
      "micro": "150–200ms",
      "panel": "220–260ms"
    },
    "easing": {
      "standard": "cubic-bezier(0.2, 0.8, 0.2, 1)",
      "exit": "cubic-bezier(0.4, 0, 1, 1)"
    },
    "rules": [
      "Sadece opacity/transform animasyonu (performans).",
      "Hover: kartlarda translateY(-1px) + shadow-soft; butonda translateY(-1px) + shadow.",
      "Scroll reveal: Framer Motion ile section bazlı (prefers-reduced-motion’da kapalı).",
      "Form validation: hata mesajı fade-in (opacity) 150ms.",
      "Timeline güncellemesi: ilgili adımda 2 kez yumuşak pulse (opacity)."
    ],
    "framer_scaffold_js": {
      "note": "Proje JS/JSX. Örnek kullanım:",
      "snippet": "import { motion, useReducedMotion } from 'framer-motion';\n\nexport default function Section({ children }) {\n  const reduce = useReducedMotion();\n  return (\n    <motion.section\n      initial={reduce ? false : { opacity: 0, y: 10 }}\n      whileInView={reduce ? undefined : { opacity: 1, y: 0 }}\n      viewport={{ once: true, amount: 0.2 }}\n      transition={{ duration: 0.22, ease: [0.2, 0.8, 0.2, 1] }}\n    >\n      {children}\n    </motion.section>\n  );\n}"
    }
  },

  "accessibility": {
    "checklist": [
      "Tüm form alanlarında label + aria-describedby (hata metni id).",
      "Renkle tek başına anlam verme (skor/durum metinle desteklenir).",
      "Focus-visible her interaktif öğede belirgin (var(--focus-ring)).",
      "Dokunma hedefleri min 44x44px (özellikle navbar, stepper, tablo aksiyonları).",
      "Tablo: başlık hücreleri th + scope; satır aksiyonları için tooltip."
    ]
  },

  "testing_and_data_testid": {
    "rules": [
      "Mevcut data-testid’ler korunacak (isim değişikliği yok).",
      "Yeni eklenen her buton/link/input/menü/önemli bilgi alanına data-testid ekle.",
      "Kebab-case; rol odaklı: örn ‘apply-summary-drawer-open-button’, ‘admin-filter-status-tabs’."
    ]
  },

  "image_urls": {
    "hero_or_marketing": [
      {
        "category": "passport-flatlay",
        "description": "Belgeler / güven / başvuru hazırlığı hissi veren açık zemin görseli (hero yan görsel veya Documents sayfası üst banner).",
        "url": "https://images.unsplash.com/photo-1613244469730-f1aa82dbe7df?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzNDR8MHwxfHNlYXJjaHwzfHxwYXNzcG9ydCUyMGZsYXQlMjBsYXklMjBsaWdodCUyMGJhY2tncm91bmR8ZW58MHx8fHdoaXRlfDE3ODgzNzE3MzB8MA&ixlib=rb-4.1.0&q=85"
      }
    ],
    "fallbacks": [
      {
        "category": "abstract",
        "description": "Stock görsel bulunamazsa: hero’da sadece hero-glow + noise-overlay + SampleVisa bileşeni kullan.",
        "url": ""
      }
    ]
  },

  "instructions_to_main_agent": {
    "implementation_sequence": [
      "1) index.css token rafinesi (değerleri güncelle, isimleri koru).",
      "2) Global yardımcı sınıflar: .card-surface, .card-hoverable, .hero-glow, .noise-overlay iyileştirmeleri (gradient %20 kuralına uy).",
      "3) Navbar/Footer: spacing, sticky davranış, mobil menü Sheet; CTA butonları netleştir.",
      "4) Home: hero + PricingTabs + PreEvaluation embed + trust strip + testimonials.",
      "5) Apply wizard: stepper + sticky summary + file dropzone + cross-sell adımı.",
      "6) Track/OrderStatus: timeline + aksiyon kartları.",
      "7) Admin: toolbar + table density + empty/loading states.",
      "8) SEO rehber sayfaları: okunabilirlik (satır uzunluğu, başlık ritmi, TOC)."
    ],
    "do_not_break": [
      "API çağrıları ve payload alanları",
      "Form field name/id",
      "Mevcut data-testid değerleri",
      "Route path’leri",
      "Light-only (dark mode ekleme)"
    ],
    "js_only_note": "Bileşen örnekleri .js/.jsx formatında tutulmalı; .tsx önerme.",
    "stitch_alignment": "Google Stitch yaklaşımı gibi: DESIGN.md benzeri tek kaynak (bu dosya) + token-first + bileşen anatomisi net. Yeni ekran üretirken ‘Anatomy + Vibe + Content’ prompt şablonunu kullanın."
  },

  "general_ui_ux_design_guidelines_appendix": "<General UI UX Design Guidelines>\n    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json\n\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.\n</General UI UX Design Guidelines>"
}
