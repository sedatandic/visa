{
  "design_system_name": "Dubai Vize Online — Flightin Sky Panels (Reference Match)",
  "version": "2026-09",
  "brand_attributes": [
    "airy",
    "trustworthy",
    "modern travel-tech",
    "premium but friendly",
    "mobile-first conversion"
  ],
  "reference_images": {
    "1_buttons_typography": "https://customer-assets-rejwkqb3.emergentagent.net/job_visa-application-ae/artifacts/xj711b60_IMG_1046.jpeg",
    "2_sections_on_sky": "https://customer-assets-rejwkqb3.emergentagent.net/job_visa-application-ae/artifacts/iwwznrcq_IMG_1047.jpeg",
    "3_desktop_landing_right_column": "https://customer-assets-rejwkqb3.emergentagent.net/job_visa-application-ae/artifacts/7rchuhx6_IMG_1048.jpeg",
    "4_hero_desktop_mobile": "https://customer-assets-rejwkqb3.emergentagent.net/job_visa-application-ae/artifacts/v42eitr3_IMG_1049.jpeg"
  },

  "font_selection": {
    "reasoning": "Reference uses Google Sans/Product Sans (not open-licensed). Closest from approved list is Figtree (geometric grotesque, friendly, modern). Montserrat is also close but feels more display/rigid; use Figtree for the full system.",
    "google_fonts": {
      "primary": {
        "family": "Figtree",
        "weights": ["400", "500", "600", "700", "800"],
        "use_for": ["headings", "body", "buttons", "forms"]
      },
      "fallback": ["system-ui", "-apple-system", "Segoe UI", "Roboto", "sans-serif"]
    },
    "italic_usage": {
      "where": [
        "Home hero H1: italicize 1–3 key words (e.g., 'Dubai vizenizi' or 'online') to match reference hero variant",
        "Pricing page hero: optional italic emphasis",
        "Never italicize long paragraphs"
      ],
      "how": "Use font-style: italic on a span with slightly tighter tracking (tracking-[-0.02em])"
    }
  },

  "typography_scale": {
    "h1": "text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-[-0.03em] leading-[1.02]",
    "h2": "text-2xl sm:text-3xl font-bold tracking-[-0.02em] leading-tight",
    "h3": "text-xl sm:text-2xl font-bold tracking-[-0.015em]",
    "body": "text-sm sm:text-base leading-relaxed",
    "small": "text-xs sm:text-sm",
    "eyebrow": "text-xs font-extrabold uppercase tracking-[0.18em]",
    "numbers": "tabular-nums"
  },

  "color_system": {
    "notes": [
      "Palette must follow reference: sky blues + off-white panels + charcoal buttons + tiny warm cream/yellow accent.",
      "Keep logo harmony: logo is dark navy/teal badge; charcoal UI neutrals will not clash; avoid teal as primary UI color.",
      "All values below are expressed as HSL triplets for shadcn tokens (space-separated)."
    ],

    "light": {
      "core_tokens_hsl": {
        "--background": "205 100% 97%",
        "--foreground": "0 0% 12%",

        "--card": "60 20% 98%",
        "--card-foreground": "0 0% 12%",

        "--popover": "60 20% 98%",
        "--popover-foreground": "0 0% 12%",

        "--primary": "0 0% 12%",
        "--primary-foreground": "0 0% 100%",

        "--secondary": "205 55% 92%",
        "--secondary-foreground": "0 0% 12%",

        "--muted": "210 25% 94%",
        "--muted-foreground": "0 0% 38%",

        "--accent": "38 78% 88%",
        "--accent-foreground": "0 0% 12%",

        "--destructive": "0 72% 52%",
        "--destructive-foreground": "0 0% 100%",

        "--border": "210 18% 88%",
        "--input": "210 18% 88%",
        "--ring": "205 85% 55%"
      },

      "brand_extension_tokens_hsl": {
        "--sky": "205 95% 92%",
        "--sky-deep": "205 85% 55%",
        "--panel": "60 20% 98%",
        "--panel-2": "38 78% 96%",
        "--charcoal": "0 0% 12%",
        "--charcoal-2": "0 0% 18%",
        "--ink": "0 0% 10%",
        "--cream-tag": "42 95% 72%",
        "--focus": "205 85% 55%"
      },

      "gradients": {
        "sky_backdrop": "linear-gradient(180deg, hsl(205 100% 96%) 0%, hsl(205 95% 92%) 35%, hsl(0 0% 100%) 100%)",
        "sky_glow_spots": "radial-gradient(900px circle at 18% 8%, hsl(205 95% 92% / 0.85), transparent 55%), radial-gradient(700px circle at 82% 12%, hsl(205 85% 55% / 0.18), transparent 60%)",
        "allowed_usage": [
          "Only as page background/backdrop (not on cards).",
          "Keep gradients behind content; content sits on solid panels.",
          "If readability suffers, reduce opacity or remove glow spots."
        ]
      }
    },

    "dark": {
      "core_tokens_hsl": {
        "--background": "220 18% 10%",
        "--foreground": "0 0% 96%",

        "--card": "220 16% 13%",
        "--card-foreground": "0 0% 96%",

        "--popover": "220 16% 13%",
        "--popover-foreground": "0 0% 96%",

        "--primary": "0 0% 96%",
        "--primary-foreground": "0 0% 12%",

        "--secondary": "220 14% 18%",
        "--secondary-foreground": "0 0% 96%",

        "--muted": "220 12% 18%",
        "--muted-foreground": "0 0% 72%",

        "--accent": "38 35% 22%",
        "--accent-foreground": "0 0% 96%",

        "--destructive": "0 72% 52%",
        "--destructive-foreground": "0 0% 100%",

        "--border": "220 12% 22%",
        "--input": "220 12% 22%",
        "--ring": "205 85% 60%"
      },

      "brand_extension_tokens_hsl": {
        "--sky": "205 35% 18%",
        "--sky-deep": "205 55% 60%",
        "--panel": "220 16% 13%",
        "--panel-2": "220 14% 16%",
        "--charcoal": "0 0% 96%",
        "--charcoal-2": "0 0% 88%",
        "--ink": "0 0% 98%",
        "--cream-tag": "42 70% 55%",
        "--focus": "205 85% 60%"
      },

      "gradients": {
        "sky_backdrop": "linear-gradient(180deg, hsl(220 18% 10%) 0%, hsl(205 28% 14%) 45%, hsl(220 16% 12%) 100%)",
        "allowed_usage": [
          "Dark mode keeps a subtle sky tint only in marketing pages.",
          "Admin screens should use solid background for readability."
        ]
      }
    }
  },

  "design_tokens_css": {
    "instructions": [
      "Implement in /app/frontend/src/index.css under :root and .dark.",
      "Replace existing petrol/copper tokens; keep variable names stable where possible (see migration_map).",
      "Set --font-heading and --font-body to Figtree.",
      "Do not use transition: all anywhere."
    ],
    "radius_scale": {
      "--radius": "1.25rem",
      "--radius-sm": "0.875rem",
      "--radius-lg": "1.75rem",
      "--radius-xl": "2rem",
      "usage": [
        "Panels: radius-xl (32px)",
        "Cards: radius-lg (28px)",
        "Inputs: radius (20px)",
        "Pills/buttons: fully rounded (9999px) via Tailwind rounded-full"
      ]
    },
    "shadow_scale": {
      "--shadow-soft": "0 10px 30px hsl(220 30% 10% / 0.10)",
      "--shadow-card": "0 14px 40px hsl(220 30% 10% / 0.12)",
      "--shadow-float": "0 26px 70px hsl(220 30% 10% / 0.16)",
      "--shadow-inset": "inset 0 1px 0 hsl(0 0% 100% / 0.55)",
      "notes": [
        "Shadows should be diffuse (large blur, low alpha) like the reference.",
        "In dark mode, reduce blur alpha: use hsl(0 0% 0% / 0.45) but keep subtle."
      ]
    },
    "spacing_system": {
      "principle": "2–3x more spacing than feels comfortable; panels breathe.",
      "panel_padding": "p-5 sm:p-7 lg:p-8",
      "section_padding": "py-14 sm:py-20",
      "grid_gutters": "gap-4 sm:gap-6 lg:gap-8"
    }
  },

  "layout_principles": {
    "page_backdrop": {
      "pattern": "Sky background + floating off-white panels",
      "implementation": {
        "marketing_pages": [
          "Wrap page in <div className='min-h-screen bg-[image:var(--sky-bg)]'> via a utility class that sets background-image using CSS var.",
          "Add a fixed cloud image layer (compressed .webp) with opacity 0.18–0.28 and blur-sm; keep it decorative only.",
          "Place content inside a centered panel container with max-w-6xl and large rounded corners."
        ],
        "admin_pages": [
          "No sky background.",
          "Use solid bg-background and standard container; keep panels/cards for hierarchy."
        ],
        "performance": [
          "Use a single cloud image (webp) repeated no-repeat; avoid huge multi-layer gradients.",
          "Prefer static noise overlay (already present in index.css) but tune opacity to 0.025–0.04 in light mode for this airy theme.",
          "Animate only opacity/transform for entrance; never animate background-position."
        ]
      }
    },

    "floating_panel_pattern": {
      "what": "Large rounded panel that holds each major section (hero widget, pricing, FAQ, testimonials)",
      "classes": [
        "bg-card/90 backdrop-blur-[2px]",
        "rounded-[var(--radius-xl)]",
        "border border-border/70",
        "shadow-[var(--shadow-float)]"
      ],
      "notes": [
        "Panels should not be full-bleed; keep 16px side padding on mobile.",
        "Use subtle translucency only if text contrast remains AA."
      ]
    },

    "home_page_structure_adaptation": {
      "mapping_from_flight_reference": {
        "flight_search_widget": "Visa type + travel date selector widget",
        "airlines_strip": "Trust/authority strip (GDRFA, TÜRSAB, banks, payment providers)",
        "destinations_grid": "Visa types grid (Tourist 30/60, Express, Multiple entry, etc.)",
        "special_offer_right_column": "Lead capture: WhatsApp support + discount code / campaign",
        "our_services_dark_panel": "Services block: Visa processing, OCR, eSIM, insurance, tracking"
      },
      "desktop_layout": "Use a 12-col grid: main content col-span-8, right rail col-span-4. On mobile, stack with right rail after hero.",
      "mobile_layout": "Single column; hero heading then widget panel; trust strip; visa cards; guides; testimonials; FAQ."
    }
  },

  "components": {
    "component_path": {
      "shadcn_primary": [
        "/app/frontend/src/components/ui/button.jsx",
        "/app/frontend/src/components/ui/card.jsx",
        "/app/frontend/src/components/ui/tabs.jsx",
        "/app/frontend/src/components/ui/toggle-group.jsx",
        "/app/frontend/src/components/ui/input.jsx",
        "/app/frontend/src/components/ui/select.jsx",
        "/app/frontend/src/components/ui/calendar.jsx",
        "/app/frontend/src/components/ui/accordion.jsx",
        "/app/frontend/src/components/ui/badge.jsx",
        "/app/frontend/src/components/ui/avatar.jsx",
        "/app/frontend/src/components/ui/progress.jsx",
        "/app/frontend/src/components/ui/table.jsx",
        "/app/frontend/src/components/ui/sonner.jsx",
        "/app/frontend/src/components/ui/dialog.jsx",
        "/app/frontend/src/components/ui/sheet.jsx",
        "/app/frontend/src/components/ui/separator.jsx"
      ],
      "optional_external": {
        "framer_motion": {
          "why": "Entrance animations for panels/cards and subtle hover motion.",
          "install": "npm i framer-motion",
          "usage_note": "Only animate transform/opacity; respect prefers-reduced-motion."
        }
      }
    },

    "buttons": {
      "primary_pill_charcoal": {
        "visual": "Charcoal pill with white text + trailing icon (plane/bolt/rocket).",
        "tailwind": "rounded-full bg-primary text-primary-foreground px-5 py-3 text-sm font-semibold shadow-[var(--shadow-soft)] hover:bg-[hsl(var(--charcoal-2))] focus-visible:ring-2 focus-visible:ring-[hsl(var(--focus))] focus-visible:ring-offset-2 focus-visible:ring-offset-background",
        "icon": "Use lucide-react icons (Plane, Zap, Rocket) sized 18-20.",
        "data_testid_examples": [
          "data-testid=\"hero-apply-now-button\"",
          "data-testid=\"visa-widget-submit-button\""
        ]
      },
      "secondary_pill_light": {
        "visual": "Light pill (transparent/sky tint) with charcoal text; subtle border.",
        "tailwind": "rounded-full bg-transparent text-foreground px-5 py-3 text-sm font-semibold border border-border/80 hover:bg-secondary/60",
        "data_testid_examples": ["data-testid=\"hero-secondary-cta-button\""]
      },
      "icon_button_round": {
        "visual": "Circular charcoal icon button.",
        "tailwind": "h-11 w-11 rounded-full bg-primary text-primary-foreground shadow-[var(--shadow-soft)] hover:bg-[hsl(var(--charcoal-2))]",
        "data_testid_examples": ["data-testid=\"visa-widget-swap-button\""]
      },
      "press_motion": {
        "rules": [
          "Hover: translateY(-1px) + shadow slightly stronger.",
          "Active: translateY(1px) (already in base CSS).",
          "Disabled: opacity-50 cursor-not-allowed; no hover lift."
        ]
      }
    },

    "segmented_tabs": {
      "use": "Visa type selector (Tourist/Express/Multiple), also Apply wizard step switch (if needed).",
      "shadcn": "tabs.jsx OR toggle-group.jsx (preferred for pill segments)",
      "visual": "Pill container; active segment charcoal with white text; inactive transparent.",
      "tailwind_container": "inline-flex rounded-full border border-border/80 bg-card/70 p-1",
      "tailwind_item_inactive": "rounded-full px-4 py-2 text-sm font-semibold text-foreground/70 hover:text-foreground",
      "tailwind_item_active": "rounded-full bg-primary text-primary-foreground shadow-[var(--shadow-soft)]"
    },

    "cards_and_panels": {
      "card_white": {
        "tailwind": "rounded-[var(--radius-lg)] bg-card border border-border/70 shadow-[var(--shadow-card)]",
        "use": ["visa type cards", "blog cards", "testimonial cards"]
      },
      "card_cream": {
        "tailwind": "rounded-[var(--radius-lg)] bg-[hsl(var(--panel-2))] border border-border/60 shadow-[var(--shadow-card)]",
        "use": ["sale tag container", "highlighted pricing card", "add-ons (eSIM/insurance)"]
      },
      "panel_dark_services": {
        "tailwind": "rounded-[var(--radius-xl)] bg-[hsl(0_0%_12%)] text-white border border-white/10 shadow-[var(--shadow-float)]",
        "inner_cards": "Use cream cards inside: bg-[hsl(var(--panel-2))] text-foreground",
        "use": ["Home: Our Services block"]
      }
    },

    "forms": {
      "field_style": {
        "inputs": "Use shadcn Input/Select/Textarea. Apply rounded-full or rounded-[var(--radius)] depending on density.",
        "tailwind_input": "h-12 rounded-full bg-white/80 dark:bg-card border border-border/80 shadow-[var(--shadow-inset)] focus-visible:ring-2 focus-visible:ring-[hsl(var(--focus))] focus-visible:ring-offset-2 focus-visible:ring-offset-background",
        "labels": "Use Label with text-xs font-semibold text-foreground/70",
        "help_text": "text-xs text-muted-foreground",
        "touch_targets": "Minimum 44px height for all primary inputs/buttons"
      },
      "file_upload": {
        "use": "Passport OCR + photo upload",
        "pattern": "Large dashed dropzone card with icon + helper text; show thumbnail preview in a small rounded card.",
        "tailwind_dropzone": "rounded-[var(--radius-lg)] border border-dashed border-border/80 bg-card/70 p-6 hover:bg-secondary/40"
      },
      "stepper": {
        "use": "Apply wizard (4 steps)",
        "pattern": "Top sticky stepper inside a floating panel; each step is a pill with number.",
        "tailwind": "sticky top-2 z-20 rounded-full bg-card/80 backdrop-blur px-2 py-2 border border-border/70 shadow-[var(--shadow-soft)]"
      }
    },

    "tracking_timeline": {
      "use": "/takip application tracking",
      "pattern": "Vertical timeline inside a floating panel; each step is a card row with status dot + connector.",
      "status_colors": {
        "done": "bg-[hsl(205_85%_55%)]",
        "current": "bg-[hsl(var(--cream-tag))]",
        "pending": "bg-muted"
      },
      "tailwind": {
        "container": "rounded-[var(--radius-xl)] bg-card border border-border/70 shadow-[var(--shadow-float)] p-6",
        "row": "grid grid-cols-[20px_1fr] gap-4 py-4",
        "dot": "h-3 w-3 rounded-full",
        "connector": "ml-[5px] mt-1 w-px flex-1 bg-border"
      },
      "data_testid_examples": [
        "data-testid=\"tracking-timeline\"",
        "data-testid=\"tracking-step-current\""
      ]
    },

    "admin_panel_adaptation": {
      "principle": "Calmer subset: no sky background, tighter density, same typography and buttons.",
      "layout": "Use solid bg-background; cards for filters and tables; keep radius-lg but reduce shadow intensity.",
      "tables": {
        "shadcn": "table.jsx",
        "row_hover": "hover:bg-secondary/40",
        "header": "bg-muted/60",
        "data_testid_examples": ["data-testid=\"admin-applications-table\""]
      }
    }
  },

  "motion_and_microinteractions": {
    "principles": [
      "Animate only transform and opacity.",
      "Use short durations: 140–220ms.",
      "Use easing: cubic-bezier(0.2, 0.8, 0.2, 1).",
      "Respect prefers-reduced-motion (already present in App.css)."
    ],
    "recommended_interactions": {
      "panel_entrance": "Fade + slight rise (y: 8 -> 0).",
      "card_hover": "translateY(-2px) + shadow-soft.",
      "segmented_control": "Active pill slides with layout animation (Framer Motion optional).",
      "scroll": "No parallax on text; optional subtle parallax on decorative plane/cloud images only."
    }
  },

  "accessibility": {
    "requirements": [
      "WCAG AA contrast for text on panels and buttons.",
      "Visible focus ring on all interactive elements (use --focus / --ring).",
      "44px minimum touch targets.",
      "Do not rely on color alone for status (timeline uses icon + label)."
    ],
    "focus_style": "Use :focus-visible with ring + ring-offset; avoid removing outlines without replacement."
  },

  "image_urls": {
    "notes": [
      "Prefer local assets for clouds/sky to avoid third-party latency.",
      "Add 1–2 compressed .webp cloud backdrops in /public/brand/ or /public/images.",
      "Use existing logo assets at /app/frontend/public/brand/."
    ],
    "categories": [
      {
        "category": "background_clouds",
        "description": "Soft cloud photographic overlay behind panels (opacity 0.18–0.28).",
        "urls": [
          "LOCAL: /brand/sky-clouds-1.webp (to be added)",
          "LOCAL: /brand/sky-clouds-2.webp (to be added)"
        ]
      },
      {
        "category": "trust_strip_logos",
        "description": "Authority/payment logos in original colors on white strip.",
        "urls": [
          "LOCAL: /brand/trust/gdrfa.svg",
          "LOCAL: /brand/trust/tursab.svg",
          "LOCAL: /brand/trust/visa.svg",
          "LOCAL: /brand/trust/mastercard.svg"
        ]
      }
    ]
  },

  "migration_map": {
    "goal": "Remap existing token names so most components keep working without rewriting.",
    "token_remaps": [
      {
        "old": "--brand-green",
        "new": "--sky-deep",
        "note": "Previously petrol teal; now use sky-deep for info accents and focus rings. Avoid using it as primary button fill."
      },
      {
        "old": "--brand-copper",
        "new": "--cream-tag",
        "note": "Copper accent becomes warm cream/yellow used sparingly (sale tag, highlight chips)."
      },
      {
        "old": "--brand-black",
        "new": "--charcoal",
        "note": "Ensure primary buttons and key text use charcoal."
      },
      {
        "old": "--sand-surface",
        "new": "--panel",
        "note": "Sand surfaces become off-white floating panels."
      },
      {
        "old": "--navy",
        "new": "--charcoal",
        "note": "Dark blocks now charcoal (not teal)."
      },
      {
        "old": "--font-heading",
        "new": "Figtree",
        "note": "Remove Tinos/Times look; headings become geometric sans."
      }
    ],
    "component_level_notes": [
      "Buttons: ensure shadcn Button variants map primary to charcoal (hsl(var(--primary))).",
      "Badges: use cream-tag for SALE/urgent; otherwise muted.",
      "Cards: increase radius and shadow to match floating panel aesthetic."
    ]
  },

  "instructions_to_main_agent": [
    "1) Update /app/frontend/src/index.css :root and .dark tokens to the new sky/charcoal system above; set --font-heading and --font-body to Figtree.",
    "2) Introduce a marketing-page wrapper class (e.g., .sky-shell) that applies the sky gradient + optional cloud overlay; keep admin pages on solid background.",
    "3) Increase radii across Card/Popover/Dialog/Sheet to match 24–32px feel; use rounded-full for pills.",
    "4) Update Button variants in /components/ui/button.jsx so primary = charcoal pill, secondary = light pill, icon = round.",
    "5) Implement segmented controls using ToggleGroup/Tabs with pill container styling.",
    "6) Ensure every interactive element and key info element has data-testid in kebab-case.",
    "7) Keep dark mode: marketing pages can have subtle dark-sky backdrop; admin stays solid for readability.",
    "8) Do not change backend APIs or routes; only UI styling/layout.",
    "9) Verify contrast on sky background: all text must sit on solid panels; never place paragraphs directly on sky photo."
  ],

  "general_ui_ux_design_guidelines": "<General UI UX Design Guidelines>  \n    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json\n\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.\n</General UI UX Design Guidelines>"
}
