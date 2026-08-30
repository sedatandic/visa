{
  "brand": {
    "name_options": [
      {
        "name": "Dubai Vize Merkezi",
        "rationale": "Açık, arama niyetine uygun, güven veren; jenerik ama güçlü."
      },
      {
        "name": "VizeAtlas Dubai",
        "rationale": "Daha özgün marka hissi; ‘atlas’ güven + rehberlik çağrışımı yapar."
      },
      {
        "name": "Dubai Vize Ofisi",
        "rationale": "Resmî tonda; ‘ofis’ kelimesi güveni artırır."
      }
    ],
    "recommended_name": "VizeAtlas Dubai",
    "wordmark_logo_concept": {
      "concept": "Tipografik wordmark + küçük ‘kapı/kemer’ (Dubai arch) simgesi",
      "details": [
        "Sembol: minimal kemer formu (tek çizgi), içinde küçük bir ‘check’ negatif alan.",
        "Renk: Navy (metin) + Teal (vurgu noktası).",
        "Kullanım: Navbar sol; favicon için sadece kemer+check."
      ]
    },
    "brand_attributes": [
      "Güven veren",
      "Resmî ama sıcak",
      "Hızlı ve net",
      "Mobilde kolay",
      "Şeffaf fiyat/akış"
    ]
  },

  "design_personality": {
    "style_fusion": [
      "Swiss grid + editorial spacing (net hiyerarşi)",
      "Soft ‘sand’ surfaces (seyahat hissi) + teal aksan (güven/teknoloji)",
      "Bento-card düzeni (fiyatlar/özellikler) + sade devlet-formu ciddiyeti (başvuru sihirbazı)"
    ],
    "do_not_copy": [
      "dubaivizeal.com ile aynı renkler, aynı ikon seti, aynı hero kompozisyonu kullanılmayacak",
      "Aynı kart şekilleri/gradient dili birebir taklit edilmeyecek",
      "Metinler tamamen özgün ve Türkçe yazılacak"
    ]
  },

  "typography": {
    "google_fonts": {
      "heading": {
        "family": "Space Grotesk",
        "weights": [400, 500, 600, 700]
      },
      "body": {
        "family": "Work Sans",
        "weights": [400, 500, 600]
      }
    },
    "tailwind_usage": {
      "headings": "font-[var(--font-heading)]",
      "body": "font-[var(--font-body)]"
    },
    "type_scale": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl leading-[1.05] tracking-[-0.02em]",
      "h2": "text-base md:text-lg leading-[1.35] text-muted-foreground",
      "section_title": "text-2xl sm:text-3xl font-semibold tracking-[-0.015em]",
      "body": "text-sm sm:text-base leading-7",
      "small": "text-xs sm:text-sm"
    }
  },

  "color_system": {
    "notes": [
      "Tema: açık (light) — güven + okunabilirlik.",
      "Aksan rengi teal; kum (sand) yüzeyler; navy başlıklar.",
      "Gradient sadece hero arka planında dekoratif overlay olarak (viewport < %20)."
    ],
    "palette_hex": {
      "navy_ink": "#0B1F33",
      "navy_ink_2": "#102A43",
      "teal_primary": "#0EA5A4",
      "teal_hover": "#0B8E8D",
      "sand_bg": "#FBF7F0",
      "sand_surface": "#F4EBDD",
      "cloud": "#F6F8FB",
      "border": "#D9E2EC",
      "text": "#0B1F33",
      "muted_text": "#52606D",
      "success": "#16A34A",
      "warning": "#F59E0B",
      "danger": "#DC2626"
    },
    "css_tokens_to_set_in_index_css": {
      "light": {
        "--background": "36 56% 97%",
        "--foreground": "210 45% 12%",
        "--card": "0 0% 100%",
        "--card-foreground": "210 45% 12%",
        "--popover": "0 0% 100%",
        "--popover-foreground": "210 45% 12%",
        "--primary": "181 84% 35%",
        "--primary-foreground": "0 0% 100%",
        "--secondary": "36 45% 92%",
        "--secondary-foreground": "210 45% 12%",
        "--muted": "210 20% 96%",
        "--muted-foreground": "210 14% 36%",
        "--accent": "181 84% 35%",
        "--accent-foreground": "0 0% 100%",
        "--destructive": "0 84% 55%",
        "--destructive-foreground": "0 0% 100%",
        "--border": "210 22% 86%",
        "--input": "210 22% 86%",
        "--ring": "181 84% 35%",
        "--radius": "0.75rem"
      },
      "additional_custom_props": {
        "--font-heading": "Space Grotesk",
        "--font-body": "Work Sans",
        "--shadow-soft": "0 10px 30px rgba(11,31,51,0.08)",
        "--shadow-card": "0 8px 20px rgba(11,31,51,0.06)",
        "--shadow-float": "0 18px 50px rgba(11,31,51,0.14)",
        "--focus-ring": "0 0 0 4px rgba(14,165,164,0.22)",
        "--noise-opacity": "0.06"
      }
    },
    "allowed_gradients": {
      "hero_overlay": "radial-gradient(900px circle at 20% 10%, rgba(14,165,164,0.14), transparent 55%), radial-gradient(700px circle at 80% 0%, rgba(245,158,11,0.10), transparent 60%)",
      "restriction": "Gradient alanı viewport’un %20’sini geçmeyecek; kartların içinde gradient yok."
    }
  },

  "layout_and_grid": {
    "container": "max-w-6xl mx-auto px-4 sm:px-6",
    "section_spacing": "py-12 sm:py-16",
    "grid_rules": [
      "Landing: 12 kolon mantığı; mobilde tek kolon, md’de 2 kolon, lg’de 3-4 kolon.",
      "Fiyat kartları: md:grid-cols-2 lg:grid-cols-3; ‘En Popüler’ kartı 1. sırada ve hafif vurgulu.",
      "Admin: geniş tablo için horizontal scroll + sticky header."
    ],
    "radius_and_surfaces": {
      "card_radius": "rounded-xl",
      "button_radius": "rounded-lg",
      "input_radius": "rounded-lg",
      "surface_backgrounds": [
        "Sayfa arka planı: sand_bg",
        "Kartlar: beyaz",
        "İkincil bloklar: cloud veya sand_surface"
      ]
    }
  },

  "components": {
    "component_path": {
      "button": "/app/frontend/src/components/ui/button.jsx",
      "card": "/app/frontend/src/components/ui/card.jsx",
      "badge": "/app/frontend/src/components/ui/badge.jsx",
      "accordion": "/app/frontend/src/components/ui/accordion.jsx",
      "tabs": "/app/frontend/src/components/ui/tabs.jsx",
      "progress": "/app/frontend/src/components/ui/progress.jsx",
      "input": "/app/frontend/src/components/ui/input.jsx",
      "label": "/app/frontend/src/components/ui/label.jsx",
      "textarea": "/app/frontend/src/components/ui/textarea.jsx",
      "select": "/app/frontend/src/components/ui/select.jsx",
      "checkbox": "/app/frontend/src/components/ui/checkbox.jsx",
      "radio_group": "/app/frontend/src/components/ui/radio-group.jsx",
      "dialog": "/app/frontend/src/components/ui/dialog.jsx",
      "sheet": "/app/frontend/src/components/ui/sheet.jsx",
      "table": "/app/frontend/src/components/ui/table.jsx",
      "calendar": "/app/frontend/src/components/ui/calendar.jsx",
      "sonner_toast": "/app/frontend/src/components/ui/sonner.jsx"
    },
    "button_system": {
      "variants": {
        "primary": {
          "use": "Başvuru Yap / Ödemeyi Tamamla / Kaydet",
          "classes": "bg-primary text-primary-foreground hover:bg-[color:var(--teal-hover)] focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))]",
          "motion": "hover:translate-y-[-1px] active:translate-y-0 active:scale-[0.99]"
        },
        "secondary": {
          "use": "Fiyatları Gör / Belgeleri İncele",
          "classes": "bg-secondary text-secondary-foreground hover:bg-[hsl(var(--secondary))]/80 border border-border"
        },
        "ghost": {
          "use": "Navbar linkleri / küçük aksiyonlar",
          "classes": "hover:bg-muted"
        },
        "destructive": {
          "use": "Admin: Sil/İptal",
          "classes": "bg-destructive text-destructive-foreground hover:bg-destructive/90"
        }
      },
      "sizes": {
        "md": "h-11 px-5 text-sm",
        "lg": "h-12 px-6 text-base",
        "icon": "h-11 w-11"
      },
      "data_testid_examples": [
        "data-testid=\"hero-apply-now-button\"",
        "data-testid=\"pricing-select-plan-button\"",
        "data-testid=\"wizard-next-step-button\""
      ]
    },
    "cards": {
      "base": "bg-card border border-border rounded-xl shadow-[var(--shadow-card)]",
      "hover": "hover:shadow-[var(--shadow-soft)] hover:border-[hsl(var(--ring))]/40",
      "pricing_card": {
        "structure": [
          "Başlık + kısa açıklama",
          "Fiyat (₺) + ‘KDV dahil’ etiketi",
          "Özellik listesi (lucide Check)",
          "CTA: Planı Seç"
        ],
        "popular_state": "ring-2 ring-[hsl(var(--ring))] bg-white"
      }
    },
    "wizard_stepper": {
      "pattern": "Üstte yatay stepper (mobilde scrollable) + Progress bar",
      "steps": [
        "Kişisel Bilgiler",
        "Seyahat Bilgileri",
        "Belgeler",
        "Özet",
        "Ödeme"
      ],
      "components": ["progress", "tabs (opsiyonel)", "card"],
      "microcopy": {
        "helper": "Bilgileriniz yalnızca başvurunuz için kullanılır.",
        "upload_hint": "JPG/PNG/PDF • Maks. 10MB"
      },
      "data_testid": [
        "wizard-stepper",
        "wizard-personal-info-form",
        "wizard-document-upload-dropzone",
        "wizard-summary-section"
      ]
    },
    "file_upload_dropzone": {
      "visual": "Kesik çizgili border + ikon + sürükle-bırak metni + küçük açıklama",
      "states": {
        "idle": "border-dashed border-border bg-white",
        "drag_over": "border-[hsl(var(--ring))] bg-[hsl(var(--ring))]/5",
        "uploading": "progress + ‘Yükleniyor…’",
        "success": "Badge: Yüklendi",
        "error": "Alert destructive"
      },
      "preview": "Yüklenen pasaport/biometrik için küçük thumbnail + ‘Değiştir’",
      "data_testid": [
        "passport-upload-input",
        "biometric-photo-upload-input",
        "uploaded-passport-preview"
      ]
    },
    "faq": {
      "component": "accordion",
      "rules": [
        "Soru başlıkları kısa ve net",
        "Cevaplar 2-5 satır; gerekirse ‘Detaylı bilgi’ linki"
      ],
      "data_testid": ["faq-accordion"]
    },
    "status_badges": {
      "component": "badge",
      "mapping": {
        "Taslak": "bg-muted text-foreground",
        "Belgeler Bekleniyor": "bg-[rgba(245,158,11,0.18)] text-[color:#7A4B00]",
        "İncelemede": "bg-[rgba(14,165,164,0.16)] text-[color:#0B5F5E]",
        "Onaylandı": "bg-[rgba(22,163,74,0.16)] text-[color:#14532D]",
        "Reddedildi": "bg-[rgba(220,38,38,0.14)] text-[color:#7F1D1D]"
      },
      "data_testid": ["application-status-badge"]
    },
    "admin_table": {
      "component": "table",
      "features": [
        "Üstte KPI kartları (Bugün Başvuru, Ödeme Bekleyen, İncelemede, Onaylanan)",
        "Filtreler: Durum, Ödeme, Tarih",
        "Arama: takip kodu / ad soyad",
        "Satır aksiyonları: Detay, Durum Güncelle"
      ],
      "responsive": "Mobilde Card-list görünümü (table yerine) önerilir; md+ tablo",
      "data_testid": [
        "admin-applications-search-input",
        "admin-status-filter-select",
        "admin-applications-table"
      ]
    },
    "whatsapp_fab": {
      "visual": "Sağ altta yuvarlak buton + tooltip",
      "classes": "fixed bottom-5 right-5 z-50 h-12 w-12 rounded-full shadow-[var(--shadow-float)] bg-[#25D366] text-white hover:brightness-95",
      "data_testid": "whatsapp-floating-button"
    }
  },

  "motion_and_microinteractions": {
    "principles": [
      "Hızlı ve güven veren: 120–180ms hover, 180–240ms modal/step geçişleri.",
      "Sadece gerekli yerlerde animasyon: CTA, kart hover, step geçişi.",
      "Reduced motion desteği: prefers-reduced-motion ile animasyonları azalt."
    ],
    "recommended_library": {
      "name": "framer-motion",
      "install": "npm i framer-motion",
      "usage": [
        "Hero CTA giriş animasyonu (opacity + y)",
        "Wizard step geçişlerinde crossfade",
        "Pricing kartlarında hover lift"
      ]
    },
    "no_universal_transition": "transition-all kullanma; sadece transition-colors, transition-shadow, transition-opacity gibi."
  },

  "imagery": {
    "image_urls": {
      "hero": [
        {
          "category": "hero",
          "description": "Dubai skyline / Burj Khalifa geniş kadraj (golden hour). Unsplash/Pexels üzerinden seçilecek; tool erişimi başarısız olduğu için manuel ekleme gerekli.",
          "url": "MANUAL_REQUIRED"
        }
      ],
      "supporting": [
        {
          "category": "supporting",
          "description": "Pasaport + uçuş/seyahat flatlay (form sayfası yan görsel).",
          "url": "MANUAL_REQUIRED"
        },
        {
          "category": "texture",
          "description": "Çok hafif kum/noise dokusu (arka plan overlay).",
          "url": "MANUAL_REQUIRED"
        }
      ]
    },
    "direction": [
      "Fotoğraflar: gerçek, yüksek çözünürlük, aşırı doygun değil.",
      "Hero’da fotoğrafı tam ekran basma; sağda görsel kartı veya masked image (rounded-2xl) kullan.",
      "Okunabilirlik için fotoğraf üstüne koyu overlay değil; bunun yerine fotoğrafı kart içinde kullan."
    ]
  },

  "page_blueprints": {
    "/": {
      "sections": [
        "Navbar (logo + Fiyatlar/Belgeler/SSS/Takip/İletişim + Başvuru Yap CTA)",
        "Hero: Başlık + alt metin + 2 CTA (Başvuru Yap / Fiyatları Gör) + güven rozetleri",
        "Hızlı Fiyat Teaser (3 kart)",
        "4 Adımda Süreç (strip)",
        "Neden Biz? (ikonlu 3-4 madde)",
        "Müşteri Yorumları (carousel)",
        "SSS teaser (3 soru) + ‘Tümünü Gör’",
        "CTA band (sand_surface) + WhatsApp",
        "Footer (resmî linkler, iletişim, KVKK)"
      ],
      "data_testid": ["landing-hero", "landing-pricing-teaser", "landing-how-it-works"]
    },
    "/vize-tipleri": {
      "sections": [
        "Sayfa başlığı + kısa açıklama",
        "Fiyat karşılaştırma kartları (14/30/60 gün; tek/çok giriş)",
        "Dahil olanlar / hariç olanlar",
        "CTA: Başvuruya Başla"
      ],
      "data_testid": ["visa-types-pricing-grid"]
    },
    "/gerekli-belgeler": {
      "sections": [
        "Checklist (checkbox listesi) + indirme linkleri (örnek dilekçe vs.)",
        "Uyarı kutuları (fotoğraf kriterleri)",
        "CTA: Belgeleri Yükleyerek Başla"
      ],
      "data_testid": ["required-documents-checklist"]
    },
    "/sss": {
      "sections": ["Accordion SSS", "Alt CTA"],
      "data_testid": ["faq-page"]
    },
    "/basvuru": {
      "sections": [
        "Wizard stepper + progress",
        "Step 1: kişisel bilgiler",
        "Step 2: seyahat bilgileri (calendar ile tarih seçimi)",
        "Step 3: belge yükleme (dropzone + preview)",
        "Step 4: özet (kartlar halinde)",
        "Step 5: ödeme (Stripe redirect)"
      ],
      "data_testid": ["application-wizard"]
    },
    "/takip": {
      "sections": [
        "Takip kodu input + sorgula",
        "Durum timeline (badge + tarih)",
        "Ödeme bekliyorsa: ‘Ödemeyi Tamamla’"
      ],
      "data_testid": ["tracking-lookup-form", "tracking-status-timeline"]
    },
    "/admin/giris": {
      "sections": ["Login card (email/şifre)", "Güvenlik notu"],
      "data_testid": ["admin-login-form"]
    },
    "/admin": {
      "sections": [
        "KPI stat cards",
        "Filtre bar + arama",
        "Başvurular tablosu",
        "Pagination"
      ],
      "data_testid": ["admin-dashboard"]
    },
    "/admin/basvuru/:id": {
      "sections": [
        "Başvuru özeti (sol)",
        "Belgeler görüntüleyici (sağ) (dialog ile büyüt)",
        "Durum güncelle (select + kaydet)"
      ],
      "data_testid": ["admin-application-detail"]
    }
  },

  "accessibility_and_trust": {
    "rules": [
      "Formlarda label zorunlu; placeholder label yerine geçmez.",
      "Focus ring görünür olmalı (custom --focus-ring).",
      "Butonlar min h-44px tap target (h-11).",
      "Fiyatlarda ‘KDV dahil’ ve ‘Hizmet bedeli’ gibi şeffaf mikro metin.",
      "Footer’da KVKK/Aydınlatma metni linkleri."
    ]
  },

  "instructions_to_main_agent": [
    "App.css içindeki CRA demo stillerini kaldır; global hizalamayı merkezleme.",
    "index.css :root tokenlarını bu guideline’daki light tokenlarla değiştir; dark mode şart değil.",
    "Google Fonts’u index.html’e ekle ve body fontunu Work Sans yap; headinglerde Space Grotesk kullan.",
    "Tüm buton/input/link/filtre/CTA’lara data-testid ekle (kebab-case).",
    "Wizard ve admin için shadcn/ui bileşenlerini kullan; HTML dropdown/calendar kullanma.",
    "Gradient sadece hero dekoratif overlay; kartlarda solid yüzey."
  ]
}

<General UI UX Design Guidelines>  
    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms
    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text
   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json

 **GRADIENT RESTRICTION RULE**
NEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc
NEVER use dark gradients for logo, testimonial, footer etc
NEVER let gradients cover more than 20% of the viewport.
NEVER apply gradients to text-heavy content or reading areas.
NEVER use gradients on small UI elements (<100px width).
NEVER stack multiple gradient layers in the same viewport.

**ENFORCEMENT RULE:**
    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors

**How and where to use:**
   • Section backgrounds (not content backgrounds)
   • Hero section header content. Eg: dark to light to dark color
   • Decorative overlays and accent elements only
   • Hero section with 2-3 mild color
   • Gradients creation can be done for any angle say horizontal, vertical or diagonal

- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**

</Font Guidelines>

- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. 
   
- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.

- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.
   
- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly
    Eg: - if it implies playful/energetic, choose a colorful scheme
           - if it implies monochrome/minimal, choose a black–white/neutral scheme

**Component Reuse:**
	- Prioritize using pre-existing components from src/components/ui when applicable
	- Create new components that match the style and conventions of existing components when needed
	- Examine existing components to understand the project's component patterns before creating new ones

**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component

**Best Practices:**
	- Use Shadcn/UI as the primary component library for consistency and accessibility
	- Import path: ./components/[component-name]

**Export Conventions:**
	- Components MUST use named exports (export const ComponentName = ...)
	- Pages MUST use default exports (export default function PageName() {...})

**Toasts:**
  - Use `sonner` for toasts"
  - Sonner component are located in `/app/src/components/ui/sonner.tsx`

Use 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.
</General UI UX Design Guidelines>
