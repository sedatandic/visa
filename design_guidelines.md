{
  "brand": {
    "product": "VizeAtlas Dubai",
    "positioning": "Türkiye’den Dubai/BAE’ye seyahat edenler için hızlı, şeffaf ve kurumsal vize başvurusu.",
    "brand_attributes": [
      "Kurumsal güven",
      "Editoryal netlik (jenerik SaaS değil)",
      "Şeffaf fiyat",
      "Hızlı işlem",
      "Mobilde kolay"
    ],
    "visual_direction": {
      "style_fusion": [
        "Swiss grid (net hiyerarşi) + editorial tipografi (karakterli başlıklar)",
        "UAE bayrak renkleriyle ‘kurumsal’ renk blokları (gradient değil) + ince çizgisel ayırıcılar",
        "Form/dash alanlarında ‘government-like’ ciddiyet: düşük radius, yüksek kontrast, belirgin focus"
      ],
      "anti_patterns": [
        "Mor/mavi SaaS gradient hero",
        "Aşırı yuvarlak köşeler (pill UI)",
        "Emoji ikonlar",
        "Kart içi gradientler",
        "Her yerde aynı teal aksan (mevcut tema tamamen değişecek)"
      ]
    }
  },

  "typography": {
    "font_pairing": {
      "heading": {
        "family": "Spectral",
        "fallback": "Georgia, serif",
        "weights": [400, 500, 600, 700]
      },
      "body": {
        "family": "IBM Plex Sans",
        "fallback": "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
        "weights": [400, 500, 600, 700]
      },
      "ui_mono_optional": {
        "family": "IBM Plex Mono",
        "weights": [400, 500, 600]
      },
      "rationale": "Spectral (serif) başlıklarda ‘insan eliyle’ editoryal güven verir; IBM Plex Sans form/admin gibi yoğun UI alanlarında okunaklı ve kurumsal. Poppins-benzeri jenerik hissi kırar."
    },
    "font_loading": {
      "file": "/app/frontend/public/index.html",
      "replace_google_fonts_link_with": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Spectral:wght@400;500;600;700&display=swap"
    },
    "css_vars": {
      "file": "/app/frontend/src/index.css",
      "set": {
        "--font-heading": "\"Spectral\", Georgia, serif",
        "--font-body": "\"IBM Plex Sans\", Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
        "--font-mono": "\"IBM Plex Mono\", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace"
      }
    },
    "type_scale_tailwind": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl leading-[1.05] tracking-[-0.02em]",
      "h2": "text-base md:text-lg leading-[1.35] text-muted-foreground",
      "section_title": "text-2xl sm:text-3xl font-semibold tracking-[-0.015em]",
      "body": "text-sm sm:text-base leading-7",
      "small": "text-xs sm:text-sm"
    },
    "usage_rules": [
      "H1/H2/H3 ve .font-heading: Spectral",
      "Body, form label, tablo metni: IBM Plex Sans",
      "Takip kodu, başvuru kodu, admin ID gibi alanlar: IBM Plex Mono (opsiyonel)"
    ]
  },

  "color_system": {
    "constraints": [
      "UAE bayrak renklerinden türetilmiş 4 renk birlikte kullanılacak: yeşil, kırmızı (ham #FF0000 YASAK), beyaz, siyah.",
      "Kırmızı/yeşil birlikte kullanıldığında durumlar sadece renkle anlatılmayacak: ikon + metin şart.",
      "WCAG AA kontrast hedefi (özellikle buton, badge, link).",
      "Gradient sadece dekoratif overlay; viewport’un %20’sini geçmeyecek; küçük elementlerde gradient yok."
    ],
    "palette_hex": {
      "uae_green": "#0B6B3A",
      "uae_green_2": "#0F7A43",
      "uae_red": "#B11226",
      "uae_red_2": "#8F0F1F",
      "uae_black": "#0B0F14",
      "uae_white": "#FFFFFF",

      "paper": "#FBFBFA",
      "ink": "#0B0F14",
      "ink_muted": "#3B4652",
      "border": "#D7DDE3",
      "surface": "#FFFFFF",
      "surface_2": "#F3F5F7",

      "success": "#0B6B3A",
      "warning": "#B7791F",
      "info": "#0F4C81",
      "danger": "#B11226"
    },

    "css_tokens_to_set_in_index_css": {
      "file": "/app/frontend/src/index.css",
      "light": {
        "--background": "40 20% 98%",
        "--foreground": "210 22% 6%",

        "--card": "0 0% 100%",
        "--card-foreground": "210 22% 6%",

        "--popover": "0 0% 100%",
        "--popover-foreground": "210 22% 6%",

        "--primary": "152 82% 23%",
        "--primary-foreground": "0 0% 100%",

        "--secondary": "210 20% 96%",
        "--secondary-foreground": "210 22% 10%",

        "--muted": "210 20% 96%",
        "--muted-foreground": "215 16% 28%",

        "--accent": "352 78% 38%",
        "--accent-foreground": "0 0% 100%",

        "--destructive": "352 78% 38%",
        "--destructive-foreground": "0 0% 100%",

        "--border": "214 18% 86%",
        "--input": "214 18% 86%",
        "--ring": "152 82% 23%",

        "--radius": "0.625rem",

        "--sidebar": "0 0% 100%",
        "--sidebar-foreground": "210 22% 6%",
        "--sidebar-border": "214 18% 86%",
        "--sidebar-accent": "210 20% 96%",
        "--sidebar-accent-foreground": "210 22% 10%",
        "--sidebar-ring": "152 82% 23%",

        "--chart-1": "152 82% 23%",
        "--chart-2": "352 78% 38%",
        "--chart-3": "210 22% 6%",
        "--chart-4": "210 20% 60%",
        "--chart-5": "210 20% 80%"
      },
      "dark": {
        "--background": "210 22% 6%",
        "--foreground": "0 0% 98%",

        "--card": "210 22% 9%",
        "--card-foreground": "0 0% 98%",

        "--popover": "210 22% 9%",
        "--popover-foreground": "0 0% 98%",

        "--primary": "152 70% 40%",
        "--primary-foreground": "210 22% 6%",

        "--secondary": "210 18% 14%",
        "--secondary-foreground": "0 0% 98%",

        "--muted": "210 18% 14%",
        "--muted-foreground": "215 14% 70%",

        "--accent": "352 70% 52%",
        "--accent-foreground": "210 22% 6%",

        "--destructive": "352 70% 52%",
        "--destructive-foreground": "210 22% 6%",

        "--border": "210 18% 18%",
        "--input": "210 18% 18%",
        "--ring": "152 70% 40%",

        "--radius": "0.625rem",

        "--sidebar": "210 22% 8%",
        "--sidebar-foreground": "0 0% 98%",
        "--sidebar-border": "210 18% 18%",
        "--sidebar-accent": "210 18% 14%",
        "--sidebar-accent-foreground": "0 0% 98%",
        "--sidebar-ring": "152 70% 40%",

        "--chart-1": "152 70% 40%",
        "--chart-2": "352 70% 52%",
        "--chart-3": "0 0% 98%",
        "--chart-4": "210 18% 55%",
        "--chart-5": "210 18% 30%"
      },
      "additional_custom_props": {
        "--shadow-soft": "0 10px 30px rgba(11, 15, 20, 0.10)",
        "--shadow-card": "0 8px 20px rgba(11, 15, 20, 0.08)",
        "--shadow-float": "0 18px 50px rgba(11, 15, 20, 0.18)",
        "--focus-ring": "0 0 0 4px rgba(11, 107, 58, 0.22)",
        "--noise-opacity": "0.05",

        "--brand-green": "152 82% 23%",
        "--brand-red": "352 78% 38%",
        "--brand-black": "210 22% 6%",
        "--brand-white": "0 0% 100%",

        "--status-success": "152 82% 23%",
        "--status-warning": "38 70% 42%",
        "--status-info": "206 78% 28%",
        "--status-danger": "352 78% 38%"
      }
    },

    "where_to_use_colors": {
      "primary_green": [
        "Ana CTA butonları (Başvuru Yap, Ödemeyi Tamamla)",
        "Wizard stepper aktif adım çizgisi/ring",
        "Admin KPI kartlarında ‘pozitif’ metrik vurgusu"
      ],
      "accent_red": [
        "İkincil vurgu (örn. ‘Hızlı Sonuç’, ‘Sınırlı süre’ gibi küçük highlight)",
        "Destructive aksiyonlar (Sil/İptal)",
        "Hata durumları (Alert/Banner)"
      ],
      "black_white": [
        "Metin ve yüzeylerin ana kontrastı",
        "Navbar/footer yapısal çizgiler",
        "Admin tablo başlıkları"
      ],
      "avoid": [
        "Kırmızı ve yeşili aynı komponent içinde sadece renk farkıyla ayırmak",
        "Kırmızı metni beyaz zeminde küçük puntoda kullanmak (kontrast düşebilir)"
      ]
    },

    "allowed_gradients": {
      "restriction": "Gradient alanı viewport’un %20’sini geçmeyecek; kartların içinde gradient yok; küçük UI elementlerinde gradient yok.",
      "hero_overlay": "radial-gradient(900px circle at 18% 10%, rgba(11, 107, 58, 0.14), transparent 55%), radial-gradient(700px circle at 82% 0%, rgba(177, 18, 38, 0.10), transparent 60%)"
    },

    "selection_and_noise": {
      "selection": "::selection { background-color: hsl(var(--brand-green) / 0.18); color: hsl(var(--foreground)); }",
      "noise_overlay": "Mevcut .noise-overlay kullanılabilir; opacity --noise-opacity ile kontrol edilecek."
    }
  },

  "layout_and_grid": {
    "container": "max-w-6xl mx-auto px-4 sm:px-6",
    "section_spacing": "py-14 sm:py-20",
    "grid_rules": [
      "Landing: mobil tek kolon; md: 2 kolon; lg: 12 kolon mantığıyla 7/5 veya 8/4 split.",
      "Fiyatlar: md:grid-cols-2 lg:grid-cols-3; ‘En Popüler’ kartı ring ile vurgula (gradient değil).",
      "Form wizard: sol içerik + sağ sticky özet (lg+); mobilde özet accordion/collapsible.",
      "Admin: md+ tablo; mobilde card-list; tablo header sticky + yatay scroll."
    ],
    "radius_and_surfaces": {
      "radius": {
        "global": "--radius: 0.625rem",
        "cards": "rounded-xl",
        "buttons": "rounded-lg",
        "inputs": "rounded-lg"
      },
      "surface_priority": [
        "Okuma alanları: solid (paper/surface)",
        "Vurgu alanları: border + ince renk şeridi (sol border)"
      ]
    }
  },

  "components": {
    "component_path": {
      "accordion": "/app/frontend/src/components/ui/accordion.jsx",
      "alert": "/app/frontend/src/components/ui/alert.jsx",
      "badge": "/app/frontend/src/components/ui/badge.jsx",
      "breadcrumb": "/app/frontend/src/components/ui/breadcrumb.jsx",
      "button": "/app/frontend/src/components/ui/button.jsx",
      "calendar": "/app/frontend/src/components/ui/calendar.jsx",
      "card": "/app/frontend/src/components/ui/card.jsx",
      "checkbox": "/app/frontend/src/components/ui/checkbox.jsx",
      "dialog": "/app/frontend/src/components/ui/dialog.jsx",
      "drawer": "/app/frontend/src/components/ui/drawer.jsx",
      "dropdown_menu": "/app/frontend/src/components/ui/dropdown-menu.jsx",
      "form": "/app/frontend/src/components/ui/form.jsx",
      "input": "/app/frontend/src/components/ui/input.jsx",
      "label": "/app/frontend/src/components/ui/label.jsx",
      "pagination": "/app/frontend/src/components/ui/pagination.jsx",
      "progress": "/app/frontend/src/components/ui/progress.jsx",
      "scroll_area": "/app/frontend/src/components/ui/scroll-area.jsx",
      "select": "/app/frontend/src/components/ui/select.jsx",
      "separator": "/app/frontend/src/components/ui/separator.jsx",
      "sheet": "/app/frontend/src/components/ui/sheet.jsx",
      "sonner": "/app/frontend/src/components/ui/sonner.jsx",
      "table": "/app/frontend/src/components/ui/table.jsx",
      "tabs": "/app/frontend/src/components/ui/tabs.jsx",
      "textarea": "/app/frontend/src/components/ui/textarea.jsx",
      "tooltip": "/app/frontend/src/components/ui/tooltip.jsx"
    },

    "button_system": {
      "tokens": {
        "radius": "var(--radius)",
        "shadow": "0 10px 22px rgba(11, 15, 20, 0.10)",
        "motion": "transition-colors transition-shadow duration-150"
      },
      "variants": {
        "primary": {
          "use": "Başvuru Yap / Ödemeyi Tamamla / Kaydet",
          "classes": "bg-primary text-primary-foreground hover:bg-primary/90 shadow-[var(--shadow-card)] hover:shadow-[var(--shadow-soft)]",
          "micro_interaction": "hover:-translate-y-[1px] active:translate-y-0 active:scale-[0.99] (transform sadece ilgili elementte)"
        },
        "secondary": {
          "use": "Fiyatları Gör / Belgeleri İncele",
          "classes": "bg-secondary text-secondary-foreground border border-border hover:bg-secondary/80"
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
        "data-testid=\"wizard-next-step-button\"",
        "data-testid=\"admin-save-status-button\""
      ]
    },

    "status_badges": {
      "component": "badge",
      "rule": "Durumlar sadece renkle değil: ikon + metin. (lucide: CheckCircle, Clock, AlertTriangle, XCircle)",
      "mapping": {
        "Taslak": "bg-muted text-foreground border border-border",
        "Belgeler Bekleniyor": "bg-[hsl(var(--status-warning))/0.16] text-[hsl(var(--foreground))] border border-[hsl(var(--status-warning))/0.25]",
        "İncelemede": "bg-[hsl(var(--status-info))/0.14] text-[hsl(var(--foreground))] border border-[hsl(var(--status-info))/0.25]",
        "Onaylandı": "bg-[hsl(var(--status-success))/0.14] text-[hsl(var(--foreground))] border border-[hsl(var(--status-success))/0.25]",
        "Reddedildi": "bg-[hsl(var(--status-danger))/0.14] text-[hsl(var(--foreground))] border border-[hsl(var(--status-danger))/0.25]"
      },
      "data_testid": "application-status-badge"
    },

    "forms_and_wizard": {
      "wizard_stepper": {
        "pattern": "Üstte yatay stepper (mobilde yatay scroll) + Progress bar; adım başlıkları kısa.",
        "components": ["progress", "card", "separator"],
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
      "dropzone": {
        "visual": "Kesik çizgili border + ikon + sürükle-bırak metni; hover’da border primary.",
        "states": {
          "idle": "border-dashed border-border bg-card",
          "drag_over": "border-[hsl(var(--ring))] bg-[hsl(var(--ring))]/5",
          "uploading": "progress + ‘Yükleniyor…’",
          "success": "Badge: Yüklendi (success)",
          "error": "Alert destructive"
        },
        "data_testid": [
          "passport-upload-input",
          "biometric-photo-upload-input",
          "uploaded-passport-preview"
        ]
      }
    },

    "admin_panel": {
      "kpi_cards": "Card + sol border accent (success/info/warning/danger) — gradient yok.",
      "filters": "Select + Input; her biri data-testid ile.",
      "table": "Table + sticky header + zebra (bg-muted/40) + row hover (bg-muted/60).",
      "data_testid": [
        "admin-applications-search-input",
        "admin-status-filter-select",
        "admin-applications-table",
        "admin-kpi-cards"
      ]
    }
  },

  "motion_and_microinteractions": {
    "principles": [
      "Hover: 120–180ms (transition-colors/opacity/shadow).",
      "Modal/Drawer: 180–240ms.",
      "Reduced motion: App.css zaten reduce-motion içeriyor; yeni animasyonlar buna saygılı olmalı."
    ],
    "library": {
      "name": "framer-motion",
      "install": "npm i framer-motion",
      "usage": [
        "Hero CTA ve trust rozetlerinde hafif giriş (opacity + y).",
        "Wizard adım geçişlerinde crossfade.",
        "Admin KPI kartlarında stagger (çok hafif)."
      ]
    },
    "no_universal_transition": "transition-all kullanma; sadece transition-colors, transition-shadow, transition-opacity."
  },

  "imagery": {
    "image_urls": [
      {
        "category": "hero",
        "description": "Dubai skyline / geniş kadraj (hero sağ görsel kartı veya masked image).",
        "url": "https://images.unsplash.com/photo-1656994865204-9646ebddd2cb?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMzV8MHwxfHNlYXJjaHwxfHxEdWJhaSUyMHNreWxpbmUlMjBnb2xkZW4lMjBob3VyJTIwZWRpdG9yaWFsfGVufDB8fHxncmVlbnwxNzg4MTE4Mzg3fDA&ixlib=rb-4.1.0&q=85"
      },
      {
        "category": "supporting",
        "description": "Başvuru/form sayfası yan görseli için ‘documents flatlay’ (stok SaaS değil, gerçek foto).",
        "url": "https://images.unsplash.com/photo-1491317079341-38313806b657?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2ODh8MHwxfHNlYXJjaHwxfHxwYXNzcG9ydCUyMGFwcGxpY2F0aW9uJTIwZG9jdW1lbnRzJTIwZmxhdGxheXxlbnwwfHx8d2hpdGV8MTc4ODExODM5NXww&ixlib=rb-4.1.0&q=85"
      },
      {
        "category": "supporting",
        "description": "Blog/makaleler kapak görseli için minimal çalışma masası flatlay.",
        "url": "https://images.unsplash.com/photo-1617175093778-8517ba3e14d9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2ODh8MHwxfHNlYXJjaHwyfHxwYXNzcG9ydCUyMGFwcGxpY2F0aW9uJTIwZG9jdW1lbnRzJTIwZmxhdGxheXxlbnwwfHx8d2hpdGV8MTc4ODExODM5NXww&ixlib=rb-4.1.0&q=85"
      }
    ],
    "direction": [
      "Fotoğraflar: gerçek, yüksek çözünürlük, düşük doygunluk; aşırı HDR yok.",
      "Hero’da tam ekran foto + koyu overlay yapma; bunun yerine görseli kart içinde kullan.",
      "Admin’de fotoğraf minimum; doküman preview dialog ile."
    ]
  },

  "implementation_plan": {
    "files_to_change": [
      {
        "path": "/app/frontend/public/index.html",
        "change": "Google Fonts linkini Spectral + IBM Plex Sans (+ opsiyonel Plex Mono) ile değiştir."
      },
      {
        "path": "/app/frontend/src/index.css",
        "change": "Mevcut teal/sand tokenlarını UAE türevi tokenlarla değiştir; .dark bloğu ekle; ::selection ve --focus-ring güncelle; --radius düşür (0.625rem)."
      },
      {
        "path": "/app/frontend/tailwind.config.js",
        "change": "Gerekirse sidebar/chart tokenları için renk mapping zaten var; ek tokenlar (status-*) kullanılacaksa Tailwind’e eklemek yerine CSS var + arbitrary value kullan."
      },
      {
        "path": "/app/frontend/src/App.css",
        "change": "Merkezleme yok; reduce-motion bloğu kalsın. Ek global stil ekleme (tema index.css’te)."
      }
    ],
    "notes": [
      "Mevcut fonksiyonellik bozulmamalı: sadece token/font/sınıf düzeyi değişiklik.",
      "Tüm interaktif ve kritik bilgi elementlerine data-testid ekle (kebab-case).",
      "Kırmızı/yeşil durumlar: ikon + metin + badge; sadece renk ile ayrım yok."
    ]
  },

  "instructions_to_main_agent": [
    "Mevcut turkuaz/teal + krem temayı tamamen kaldır: index.css :root tokenlarını bu dosyadaki light/dark ile değiştir.",
    "index.html font linkini Spectral + IBM Plex Sans (+ Plex Mono) ile değiştir; index.css’te --font-heading/--font-body güncelle.",
    "UAE renklerini ‘karışık’ kullan: primary=yeşil, accent/destructive=koyu kırmızı, metin=near-black, yüzey=beyaz; küçük vurgu şeritleri/ayırıcılar ile siyah-beyaz dengesi kur.",
    "Gradient sadece hero dekoratif overlay (max %20 viewport). Kartlarda ve footer’da gradient yok.",
    "Aşırı yuvarlak köşeleri azalt: --radius 0.625rem; buton/input rounded-lg, kart rounded-xl.",
    "Status renkleri (success/warning/info/danger) için CSS var kullan; badge + ikon + metin ile göster.",
    "Tüm butonlar, linkler, inputlar, selectler, tab trigger’lar, wizard next/back, ödeme CTA, admin filtreleri ve tablo satır aksiyonlarına data-testid ekle (kebab-case).",
    "Shadcn UI dışı HTML dropdown/calendar/toast kullanma; mevcut /components/ui bileşenlerini kullan."
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
