{
  "brand": {
    "name": "Dubai Vize Online",
    "design_personality": [
      "kurumsal + güven veren",
      "premium (pasaport/ödeme akışı için ciddi)",
      "editorial (serif başlıklarla otorite)",
      "sıcak kum nötrleri + soğuk petrol teal kontrastı",
      "minimal ama zengin detay (hairline border + noise + kontrollü gradyan)"
    ],
    "non_negotiables": [
      "KIRMIZI tema tamamen kaldırılacak; kırmızı sadece destructive/error semantiği için kalacak.",
      "Renk paleti logodan türetilecek: petrol teal + bakır/bronz ana ikili; royal mavi ikincil vurgu; kırık beyaz/kum nötrleri.",
      "Gradyan sadece dekoratif/hero arka planlarında ve büyük yüzeylerde; viewport'un %20'sini aşmayacak.",
      "Mevcut JSX yapısı bozulmadan: öncelik CSS token değişimi.",
      "Tüm interaktif ve kritik bilgi öğelerinde data-testid zorunlu."
    ]
  },

  "typography": {
    "font_pairing": {
      "heading": {
        "css_var": "--font-heading",
        "recommended": "Playfair Display",
        "fallbacks": ["Crimson Text", "Montserrat", "serif"],
        "usage": "H1/H2/H3, sayfa başlıkları, fiyat başlıkları, hero headline"
      },
      "body": {
        "css_var": "--font-body",
        "recommended": "Figtree",
        "fallbacks": ["Montserrat", "system-ui", "sans-serif"],
        "usage": "paragraflar, form label/help text, tablo içerikleri"
      },
      "mono": {
        "css_var": "--font-mono",
        "recommended": "Roboto Mono",
        "fallbacks": ["Source Code Pro", "ui-monospace", "monospace"],
        "usage": "referans kodu, başvuru numarası, ödeme/işlem id"
      }
    },
    "text_size_hierarchy": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl",
      "h2": "text-base md:text-lg",
      "body": "text-sm md:text-base",
      "small": "text-xs"
    },
    "type_rules": [
      "Başlıklarda serif + daha düşük letter-spacing: h1/h2 için tracking-[-0.02em] korunabilir.",
      "UI etiketleri (badge/eyebrow) uppercase + tracking-[0.16em] kullanılabilir; renk artık bakır/teal olacak.",
      "Form alanlarında okunabilirlik için body font-weight 400-500; kritik değerlerde 600."
    ]
  },

  "color_system": {
    "source_palette_from_logo": {
      "copper_bronze": ["#A06030", "#B0733C", "#B08050"],
      "sand_neutrals": ["#C0A080", "#F7F4EF", "#FFFFFF"],
      "petrol_teal": ["#003040", "#0E5A66", "#146070"],
      "bright_teal": ["#2090A0"],
      "royal_navy": ["#1E3A8A", "#2B4B9B"]
    },

    "token_strategy": {
      "goal": "Shadcn HSL tokenlarını (index.css) logoya göre yeniden map etmek; eski token isimlerini kırmadan yeni değerlere taşımak.",
      "backward_compat": {
        "--brand-green": "Artık PRIMARY teal olacak (isim kalsa da değer teal).",
        "--brand-red": "Sadece destructive/error için kullanılacak; UI vurgusu olmayacak.",
        "--gold": "Bakır/bronz accent olarak kullanılacak.",
        "--navy": "Petrol teal'in en koyu tonu olarak kullanılacak (admin sidebar/hero dark)."
      }
    },

    "css_tokens_light": {
      "note": "Tüm değerler HSL formatında (Tailwind/shadcn uyumlu). Hex -> HSL yaklaşık dönüşüm; uygulamada görsel QA ile küçük ayar yapılabilir.",

      "--background": "36 33% 97%",
      "--foreground": "195 100% 12%",

      "--card": "0 0% 100%",
      "--card-foreground": "195 100% 12%",

      "--popover": "0 0% 100%",
      "--popover-foreground": "195 100% 12%",

      "--primary": "191 67% 26%",
      "--primary-foreground": "0 0% 100%",

      "--secondary": "36 28% 93%",
      "--secondary-foreground": "195 100% 14%",

      "--muted": "36 18% 92%",
      "--muted-foreground": "195 18% 34%",

      "--accent": "28 55% 42%",
      "--accent-foreground": "0 0% 100%",

      "--destructive": "0 72% 50%",
      "--destructive-foreground": "0 0% 100%",

      "--border": "36 16% 86%",
      "--input": "36 16% 86%",
      "--ring": "191 67% 26%",

      "--radius": "0.9rem",

      "brand_legacy_tokens": {
        "--navy": "195 100% 12%",
        "--sand-surface": "36 28% 93%",
        "--cloud": "36 33% 97%",
        "--gold": "28 55% 42%",
        "--teal-hover": "191 67% 22%",
        "--success": "191 67% 22%",

        "--brand-green": "191 67% 26%",
        "--brand-green-soft": "191 35% 92%",
        "--brand-green-deep": "195 100% 12%",

        "--brand-red": "0 72% 50%",
        "--brand-black": "195 100% 12%",
        "--brand-white": "0 0% 100%",

        "--status-success": "191 67% 22%",
        "--status-warning": "32 90% 45%",
        "--status-info": "210 70% 40%",
        "--status-danger": "0 72% 50%"
      },

      "charts": {
        "--chart-1": "191 67% 26%",
        "--chart-2": "28 55% 42%",
        "--chart-3": "221 55% 45%",
        "--chart-4": "36 18% 60%",
        "--chart-5": "195 18% 34%"
      },

      "shadows": {
        "--shadow-soft": "0 10px 30px hsl(195 60% 10% / 0.10)",
        "--shadow-card": "0 8px 20px hsl(195 60% 10% / 0.08)",
        "--shadow-float": "0 18px 50px hsl(195 60% 10% / 0.14)",
        "--focus-ring": "0 0 0 4px hsl(191 67% 26% / 0.22)"
      },

      "gradients": {
        "--gradient-hero": "linear-gradient(135deg, hsl(191 67% 26% / 0.14) 0%, hsl(221 55% 45% / 0.10) 55%, hsl(36 33% 97% / 0.0) 100%)",
        "--gradient-wave": "linear-gradient(90deg, hsl(191 67% 26%) 0%, hsl(221 55% 45%) 100%)",
        "--gradient-sand": "linear-gradient(180deg, hsl(36 33% 97%) 0%, hsl(36 28% 93%) 100%)"
      }
    },

    "css_tokens_dark": {
      "note": "Dark mod: petrol teal yüzey + kum tonlu metin; bakır accent daha kontrollü. Okunabilirlik için kontrast yüksek tutulur.",

      "--background": "195 100% 8%",
      "--foreground": "36 33% 94%",

      "--card": "195 100% 10%",
      "--card-foreground": "36 33% 94%",

      "--popover": "195 100% 10%",
      "--popover-foreground": "36 33% 94%",

      "--primary": "191 67% 38%",
      "--primary-foreground": "195 100% 8%",

      "--secondary": "195 40% 14%",
      "--secondary-foreground": "36 33% 94%",

      "--muted": "195 35% 14%",
      "--muted-foreground": "36 12% 72%",

      "--accent": "28 55% 52%",
      "--accent-foreground": "195 100% 8%",

      "--destructive": "0 72% 52%",
      "--destructive-foreground": "0 0% 100%",

      "--border": "195 35% 18%",
      "--input": "195 35% 18%",
      "--ring": "191 67% 38%",

      "--radius": "0.9rem",

      "brand_legacy_tokens": {
        "--navy": "195 100% 8%",
        "--sand-surface": "195 40% 14%",
        "--cloud": "195 35% 14%",
        "--gold": "28 55% 52%",
        "--teal-hover": "191 67% 34%",
        "--success": "191 67% 38%",

        "--brand-green": "191 67% 38%",
        "--brand-green-soft": "191 35% 18%",
        "--brand-green-deep": "195 100% 8%",

        "--brand-red": "0 72% 52%",
        "--brand-black": "195 100% 8%",
        "--brand-white": "0 0% 100%",

        "--status-success": "191 67% 38%",
        "--status-warning": "32 90% 55%",
        "--status-info": "221 55% 55%",
        "--status-danger": "0 72% 52%"
      },

      "charts": {
        "--chart-1": "191 67% 38%",
        "--chart-2": "28 55% 52%",
        "--chart-3": "221 55% 55%",
        "--chart-4": "36 12% 72%",
        "--chart-5": "195 18% 60%"
      },

      "shadows": {
        "--shadow-soft": "0 10px 30px hsl(195 80% 2% / 0.35)",
        "--shadow-card": "0 8px 20px hsl(195 80% 2% / 0.28)",
        "--shadow-float": "0 18px 50px hsl(195 80% 2% / 0.42)",
        "--focus-ring": "0 0 0 4px hsl(191 67% 38% / 0.22)"
      },

      "gradients": {
        "--gradient-hero": "linear-gradient(135deg, hsl(191 67% 38% / 0.18) 0%, hsl(221 55% 55% / 0.12) 55%, hsl(195 100% 8% / 0.0) 100%)",
        "--gradient-wave": "linear-gradient(90deg, hsl(191 67% 38%) 0%, hsl(221 55% 55%) 100%)",
        "--gradient-sand": "linear-gradient(180deg, hsl(195 100% 10%) 0%, hsl(195 100% 8%) 100%)"
      }
    },

    "contrast_notes": {
      "aa_safe_pairs": [
        {
          "pair": "Primary button",
          "bg": "--primary (petrol teal)",
          "text": "--primary-foreground (white)",
          "note": "Teal koyu tutulduğu için beyaz metin AA geçer. Eğer primary daha açık yapılırsa metni --primary-foreground yerine --background (dark) yapmayın; primary'yi koyulaştırın."
        },
        {
          "pair": "Copper accent button",
          "bg": "--accent (bakır)",
          "text": "--accent-foreground (white)",
          "note": "Bakır tonu yeterince koyu seçildi (L düşük). Eğer tasarımda daha açık kum-bakır istenirse metni beyaz yerine --foreground (petrol) yapın."
        }
      ],
      "avoid": [
        "Açık kum (#C0A080 benzeri) zemin üstüne beyaz metin kullanmayın.",
        "Bakır üstüne ince font-weight (300-400) kullanmayın; en az 600."
      ]
    }
  },

  "role_mapping_table": {
    "primary_actions": {
      "use": "--primary",
      "examples": [
        "Hero: 'Hemen Başvur'",
        "Wizard: 'Devam Et'",
        "Ödeme: 'Ödemeyi Tamamla'"
      ],
      "tailwind": "bg-primary text-primary-foreground hover:bg-primary/90 focus-visible:ring-2 focus-visible:ring-ring"
    },
    "secondary_actions": {
      "use": "--secondary + border",
      "examples": ["Hero: 'Fiyatları Gör'", "Wizard: 'Geri'"],
      "tailwind": "bg-secondary text-secondary-foreground border border-border hover:bg-secondary/70"
    },
    "accent_actions": {
      "use": "--accent",
      "examples": ["Cross-sell: 'eSIM Ekle'", "Sigorta: 'Pakete Ekle'"]
    },
    "links": {
      "use": "--primary",
      "tailwind": "text-primary underline-offset-4 hover:underline"
    },
    "badges": {
      "info": "bg-primary/10 text-primary border-primary/20",
      "copper": "bg-[hsl(var(--accent)/0.12)] text-[hsl(var(--accent))] border-[hsl(var(--accent)/0.25)]"
    },
    "stepper_timeline": {
      "active": "dot/bg: --primary, text: --foreground",
      "completed": "dot/bg: --accent (bakır) veya --primary (teal) + check icon",
      "upcoming": "dot/bg: --muted, text: --muted-foreground",
      "connector": "border --border"
    },
    "pricing": {
      "price": "text-foreground",
      "discount": "badge copper",
      "total": "text-primary font-semibold"
    },
    "admin_sidebar": {
      "bg": "--navy (petrol teal en koyu)",
      "item_active": "bg-primary/15 text-foreground",
      "item_hover": "bg-primary/10",
      "divider": "border-border/60"
    },
    "semantic": {
      "success": "--status-success (teal)",
      "warning": "--status-warning (amber)",
      "info": "--status-info (royal)",
      "destructive": "--destructive (red)"
    }
  },

  "layout_and_grid": {
    "global": {
      "container": "container-page (max-w-6xl px-4 sm:px-6)",
      "spacing": [
        "section: py-14 sm:py-20",
        "cards: p-5 sm:p-6",
        "forms: gap-4 sm:gap-6",
        "wizard footer: sticky bottom-0 bg-background/90 backdrop-blur border-t"
      ]
    },
    "public_home": {
      "hero": {
        "structure": [
          "Left: headline + trust bullets + CTA row",
          "Right: skyline image card + mini 'fiyat hesapla' widget",
          "Background: hero-glow + noise-overlay (opacity düşük)"
        ],
        "gradient_usage": "Sadece hero arka planında --gradient-hero; içerik kartlarında gradient yok."
      },
      "trust_sections": [
        "'Neden Biz' 3-4 kart: KVKK/SSL, iade politikası, canlı destek/WhatsApp, şeffaf fiyat",
        "'Süreç' 4 adım: timeline/stepper görsel",
        "'Yorumlar' pull-quote style (editorial)"
      ]
    },
    "application_wizard": {
      "pattern": "shadcn multi-step form + sticky footer navigation",
      "mobile_first": "Stepper üstte yatay scroll veya condensed timeline; CTA footer sabit"
    },
    "admin": {
      "pattern": "Sidebar + topbar + content cards",
      "density": "Tablo sayfalarında daha sıkı padding (p-4), detay sayfalarında p-6"
    }
  },

  "components": {
    "component_path": {
      "buttons": "/app/frontend/src/components/ui/button.jsx",
      "cards": "/app/frontend/src/components/ui/card.jsx",
      "badges": "/app/frontend/src/components/ui/badge.jsx",
      "forms": "/app/frontend/src/components/ui/form.jsx",
      "inputs": "/app/frontend/src/components/ui/input.jsx",
      "select": "/app/frontend/src/components/ui/select.jsx",
      "tabs": "/app/frontend/src/components/ui/tabs.jsx",
      "table": "/app/frontend/src/components/ui/table.jsx",
      "progress": "/app/frontend/src/components/ui/progress.jsx",
      "calendar": "/app/frontend/src/components/ui/calendar.jsx",
      "dialog": "/app/frontend/src/components/ui/dialog.jsx",
      "sheet_drawer": "/app/frontend/src/components/ui/sheet.jsx",
      "sonner_toast": "/app/frontend/src/components/ui/sonner.jsx",
      "accordion_faq": "/app/frontend/src/components/ui/accordion.jsx",
      "breadcrumb": "/app/frontend/src/components/ui/breadcrumb.jsx",
      "navigation_menu": "/app/frontend/src/components/ui/navigation-menu.jsx"
    },
    "recommended_new_ui_patterns_without_rewriting_logic": {
      "stepper": {
        "reference": [
          "https://www.shadcn.io/blocks/form-multi-step",
          "https://www.shadcn.io/blocks/stepper-condensed-timeline",
          "https://www.shadcn.io/blocks/stepper-booking-reservation"
        ],
        "implementation_note_js": "Projede .jsx var; bloklardan alınan JSX direkt kullanılabilir. Stepper için ekstra component yazılacaksa export const Stepper = ... şeklinde named export kullanın."
      }
    }
  },

  "motion_and_microinteractions": {
    "principles": [
      "Hover: sadece color/shadow/border transition (transition-colors, transition-shadow).",
      "Press: button active: scale-[0.98] (transform transition ayrı).",
      "Scroll: hero'da çok hafif parallax (background image translateY) opsiyonel.",
      "Reduced motion: App.css zaten reduce-motion override içeriyor; yeni animasyonlar buna saygılı olmalı."
    ],
    "token_suggestions": {
      "durations": {
        "fast": "150ms",
        "base": "200ms",
        "slow": "320ms"
      },
      "easings": {
        "standard": "cubic-bezier(0.2, 0.8, 0.2, 1)",
        "emphasized": "cubic-bezier(0.2, 0.9, 0.2, 1)"
      }
    },
    "examples": {
      "card_hover": "hover:border-primary/40 hover:shadow-[var(--shadow-soft)] transition-shadow duration-200",
      "primary_button": "transition-colors duration-200 hover:bg-primary/90 active:scale-[0.98]"
    }
  },

  "accessibility": {
    "requirements": [
      "WCAG AA kontrast: özellikle bakır üstünde beyaz metin QA ile doğrulanmalı.",
      "Focus-visible: index.css :focus-visible box-shadow var(--focus-ring) ile korunacak.",
      "Form error states: destructive kırmızı sadece hata metni/border için; arka planı çok geniş alanlarda kırmızı yapmayın.",
      "Touch targets: mobilde butonlar min-h-11, input min-h-11 önerilir."
    ],
    "data_testid_rules": {
      "convention": "kebab-case; rol odaklı",
      "examples": [
        "data-testid=\"hero-primary-cta-button\"",
        "data-testid=\"application-stepper\"",
        "data-testid=\"wizard-next-button\"",
        "data-testid=\"payment-total-amount\"",
        "data-testid=\"admin-sidebar-nav\""
      ]
    }
  },

  "image_urls": {
    "logo": [
      {
        "category": "brand",
        "description": "Header ve footer için şeffaf logo",
        "url": "/brand/logo.png"
      }
    ],
    "hero": [
      {
        "category": "public_home",
        "description": "Dubai skyline (hero sağ görsel kartı / arka plan görseli).",
        "url": "https://images.pexels.com/photos/18341554/pexels-photo-18341554.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
      }
    ],
    "supporting": [
      {
        "category": "public_sections",
        "description": "Desert dunes (rehber/blog kapakları veya süreç bölümü arka planı - düşük opaklık).",
        "url": "https://images.unsplash.com/photo-1553324533-33616fe1c4de?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
      }
    ]
  },

  "instructions_to_main_agent": [
    "Öncelik: /app/frontend/src/index.css içindeki :root tokenlarını bu guideline'daki light tokenlarla değiştir; ardından .dark selector ekleyip dark tokenları tanımla (mevcut dosyada dark yok).",
    "Mevcut legacy token isimlerini KIRMA: --brand-green artık teal olacak; --gold bakır accent; --navy petrol teal.",
    "index.css içindeki .eyebrow rengi şu an brand-red; bunu brand tokenlara göre bakır veya primary yap (tercihen accent/bakır).",
    "flag-strip ve hero-glow gradientleri kırmızıya bağlı; bunları --gradient-wave ve --gradient-hero ile değiştir. Gradient alanı hero ile sınırlı kalsın.",
    "Button/Badge gibi shadcn bileşenleri tokenları otomatik tüketir; JSX'e dokunmadan tema değişimi büyük ölçüde gerçekleşir.",
    "Admin sidebar varsa (navy token kullanan), arka plan artık petrol teal olacak; aktif item primary/15.",
    "Favicon için /public/brand/logo.png'den üretim gerekiyorsa build pipeline'a dokunmadan mevcut favicon yolunu güncelle (varsa).",
    "Tüm yeni eklenen interaktif öğelere data-testid ekle; mevcutlarda eksikse kritik akışlarda tamamla (başvuru wizard, ödeme, takip)."
  ],

  "general_ui_ux_design_guidelines_appendix": "<General UI UX Design Guidelines>\n    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json\n\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.\n</General UI UX Design Guidelines>"
}
