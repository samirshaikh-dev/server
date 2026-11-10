---
name: seo-strategy
description: Master strategic framework for technical search engine optimization (SEO), answer-engine optimization (AEO), generative-engine optimization (GEO), and machine-readable content syndication. Prioritizes high-leverage assets (sitemaps with authentic lastmod, IndexNow instant ping pipelines, multi-schema JSON-LD with Person/Organization/Service/FAQPage, clean markdown endpoints, and RSS/Atom feeds), Next.js metadata routes, and entity citation architecture across search engines and AI assistants.
---

# Purpose

Establish and enforce an authoritative, engineering-driven SEO & GEO/AEO strategy that guarantees maximum discoverability, rapid indexing, and verified citations across traditional search engines (Google, Bing) and autonomous AI models (ChatGPT, Claude, Perplexity, Google AI Overviews, Microsoft Copilot).

Treats discoverability not as marketing guesswork or keyword stuffing, but as a machine-readable data infrastructure problem: clean protocol endpoints, accurate entity graphs, sub-second indexing pipelines, and quote-ready direct answers.

---

# Scope

### Owns:
- **Prioritized File & Protocol Architecture**: Implementation and maintenance of high-value and medium-value machine-readable files (`sitemap.xml`, `robots.txt`, `llms.txt`, `llms-full.txt`, `feed.xml`, `manifest.webmanifest`, IndexNow verification keys, `security.txt`).
- **Instant Indexing Pipelines**: Instant indexing mechanisms (IndexNow API integration for Bing/Copilot/Seznam/Yandex).
- **AEO & GEO Direct-Answer Architecture**: Structuring content with question-led headings followed immediately by concise, extractable standalone answers that LLMs quote.
- **Machine-Readable Markdown Endpoints**: Maintaining non-HTML `.md` documentation counterparts (`/services.md`, `/pricing.md`, `/about.md`) for token-efficient agent ingestion.
- **Entity & Knowledge Graph Grounding**: Cross-linking JSON-LD schemas (`Organization`, `LocalBusiness`, `Service`, `FAQPage`, `Article`, `BreadcrumbList`, and `Person` for authors/leadership) with verified external entities (LinkedIn, Google Maps).
- **Next.js App Router Metadata Routes**: Designing and validating Next.js file-based metadata handlers (`app/robots.ts`, `app/sitemap.ts`, `app/manifest.ts`, `app/opengraph-image.tsx`, `app/feed.xml/route.ts`).
- **Pages That Function as Trust Engines**: Architectural requirements for `/pricing`, `/about`, `/faq`, and `/portfolio/[slug]` case studies.

### Does NOT own:
- **Core Web Vitals & Render UX**: Browser rendering performance, layout shifts, and CSS bundle optimization → `frontend-engineer` / `performance-engineer`.
- **Primary Keyword Clustering & Copywriting**: Identifying niche keyword volumes and writing editorial prose → `seo-keyword-research-implementation`.
- **Autonomous RAG & AI Agent Chatbots**: Embedding vectors, similarity search, and chatbot system prompts → `ai-engineer`.
- **Database Schema Storage**: Firestore collection structures and security rules → `database-engineer`.

---

# When This Skill Activates

- Setting up or auditing technical discovery files (`robots.ts`, `sitemap.ts`, `llms.txt`, `feed.xml`).
- Designing new public pages to ensure they satisfy both human conversion and AI citation standards.
- Establishing or updating schema markup (`src/lib/seo/schemas.ts`).
- Integrating fast-indexing pipelines (e.g. IndexNow webhooks upon CMS publishing).
- Preparing content for generative answer engines (ChatGPT Search, Perplexity, Gemini).
- Evaluating which SEO practices to prioritize vs. obsolete folklore to ignore.

---

# Strategic Value Hierarchy

Not all SEO assets are created equal. Effort must strictly follow measurable impact:

```
┌────────────────────────────────────────────────────────────────────────┐
│ HIGH VALUE (Critical infrastructure for SEO, AEO, and AI indexing)    │
│  1. sitemap.xml (Accurate, stable lastmod timestamps)                  │
│  2. IndexNow key file & ping utility (Instant Bing/Copilot discovery)  │
│  3. Comprehensive JSON-LD Schemas (Org, Service, FAQ, Person, Article) │
│  4. Plaintext Markdown Endpoints (/services.md, /pricing.md, etc.)     │
│  5. RSS/Atom Feed (/feed.xml for aggregators & AI crawlers)            │
├────────────────────────────────────────────────────────────────────────┤
│ MEDIUM VALUE (Enhanced CTR, trust signals, and site hygiene)           │
│  6. Dynamic OpenGraph / Twitter Cards (app/opengraph-image.tsx)        │
│  7. Web App Manifest & Favicons (app/manifest.ts)                      │
│  8. Standardized llms.txt & llms-full.txt (llmstxt.org specification)   │
│  9. Security Disclosure Policy (/.well-known/security.txt)             │
│ 10. Clean 301 Redirect Rules in next.config.ts                         │
│ 11. Search Console & Bing Webmaster Verification                       │
├────────────────────────────────────────────────────────────────────────┤
│ PAGES THAT WORK LIKE FILES (Entity citation drivers)                   │
│ 12. Transparent Pricing Page (/pricing with price tiers & FAQ schema)   │
│ 13. Leadership & Author Profile (/about with Person schema & LinkedIn) │
│ 14. Question-Led FAQ Sections (Immediate direct answers under H3)      │
│ 15. Citable Case Studies & Original Data (/portfolio/[slug])           │
│ 16. Helpful 404 Error Hub with recovery links                          │
├────────────────────────────────────────────────────────────────────────┤
│ SKIP / ANTI-PATTERNS (Zero ranking value or risk manual penalty)       │
│  ❌ ai.txt, humans.txt, ai-plugin.json (Obsolete or unparsed)          │
│  ❌ Meta keywords tags (Ignored by all major search engines)           │
│  ❌ Scaled auto-generated prompt variations (Classified as search spam)│
│  ❌ dynamic new Date() lastmod in sitemaps (Destroys crawl trust)      │
└────────────────────────────────────────────────────────────────────────┘
```

---

# Next.js 16 File Architecture Map

In this Next.js 16 App Router repository, discovery endpoints map directly to file conventions:

| Discovery Protocol | Code Location | Output Route | Purpose |
| :--- | :--- | :--- | :--- |
| **Robots Directives** | `src/app/robots.ts` | `/robots.txt` | Permits search bots and explicit AI agents (`GPTBot`, `PerplexityBot`, `DeepSeekBot`, `Claude-Search`). |
| **XML Sitemap** | `src/app/sitemap.ts` | `/sitemap.xml` | Maps canonical URLs with stable `lastmod` and realistic change frequencies. |
| **Web Manifest** | `src/app/manifest.ts` | `/manifest.webmanifest` | PWA manifest, background colors, and search result mobile icons. |
| **Dynamic Social Cards**| `src/app/opengraph-image.tsx` | `/opengraph-image` | Dynamic 1200x630 OG/Twitter banner using Next.js `ImageResponse`. |
| **RSS / Atom Feed** | `src/app/feed.xml/route.ts` | `/feed.xml` | RSS 2.0 XML endpoint with all published blog posts. |
| **IndexNow Key** | `public/<key>.txt` | `/<key>.txt` | Host validation key for instant IndexNow submissions. |
| **IndexNow Dispatcher** | `src/lib/seo/indexnow.ts` | Server Utility | Async function `submitToIndexNow(urls)` to ping Bing/IndexNow API. |
| **Curated LLM Index** | `public/llms.txt` | `/llms.txt` | llmstxt.org standard index with canonical markdown links. |
| **RFC Path Rewrite** | `public/.well-known/llms.txt` | `/.well-known/llms.txt` | Standalone copy & rewrite in `next.config.ts`. |
| **Full Knowledge Base** | `public/llms-full.txt` | `/llms-full.txt` | Complete unabridged markdown corpus of all services, industries, and FAQs. |
| **Markdown Pages** | `public/*.md` | `/services.md`, `/pricing.md`, `/about.md` | Clean markdown counterparts for token-budgeted AI tools. |
| **Security Disclosure** | `public/.well-known/security.txt`| `/.well-known/security.txt` | RFC 9116 security contact and vulnerability disclosure info. |

---

# Core Engineering Principles

1. **Authentic `lastmod` Integrity**:
   - Never use `new Date()` for static pages in `sitemap.ts`. Search engines detect identical timestamps changing across requests and flag the sitemap as spam, ignoring `lastmod` completely.
   - Use a stable release constant (e.g. `STABLE_RELEASE_DATE`) for static routes, and real modification timestamps (`post.dateModified`) for dynamic database content.

2. **Dual-Audience Indexing (HTML for Humans, Markdown for Agents)**:
   - Humans require rich visual layouts, Tailwind CSS styling, and interactive micro-animations.
   - Autonomous AI scrapers and search synthesizers prefer token-efficient plaintext markdown. Provide parallel clean `.md` endpoints for key pages (`/services.md`, `/pricing.md`, `/about.md`).

3. **Direct-Answer Pattern (AEO/GEO Requirement)**:
   - When answering questions in FAQs, blog posts, or service pages, structure sections as:
     `### [Question with natural search phrasing]`
     Followed immediately by a **1–2 sentence direct, standalone answer** containing the core facts, prices, or technical specifics.
   - Only after the direct answer should supporting context, bullet points, and nuance be provided. This enables LLMs to quote the answer verbatim without hallucination.

4. **Multi-Entity Schema Cross-Referencing**:
   - Never rely on a single schema type. Interlink schemas using `@id` references:
     - `WebSite` → points to `Organization` as publisher.
     - `Service` → points to `Organization` as provider.
     - `Article` → points to `Organization` as publisher and `Person` as author.
     - `Person` → points to `Organization` via `worksFor` and links to external social credentials via `sameAs`.

5. **Instant Indexing Over Passive Crawling**:
   - Passive crawling can take 7 to 30 days for new pages. Maintain an automated IndexNow dispatcher (`src/lib/seo/indexnow.ts`) that fires whenever content is created or updated in the CMS.

---

# Decision-Making Framework

### When to add a Markdown counterpart (`.md`):
- Add a `.md` version whenever a page contains structured commercial or technical facts that prospective clients ask AI models about:
  - Service catalogs (`/services.md`)
  - Pricing and packaging (`/pricing.md`)
  - Agency credentials and background (`/about.md`)
- Do not create `.md` files for purely visual galleries or temporary landing pages.

### When to create a dedicated page vs. a section:
- If a concept has distinct commercial search intent (e.g. *"website development cost in Vapi"*), create a **dedicated page** (`/pricing`) rather than hiding it as an accordion on the homepage. Pages receive canonical URLs, dedicated JSON-LD schemas, and targeted meta titles.

### IndexNow vs. Google Search Console:
- Google does **not** support IndexNow; rely on XML sitemaps and Search Console API for Google.
- Bing, Seznam, Naver, and Yandex **do** support IndexNow. Bing data powers **Microsoft Copilot** and **ChatGPT Search**. Submit to IndexNow immediately upon publishing.

---

# Implementation Workflow

1. **Audit Baseline Discovery Assets**:
   - Inspect `robots.ts` to ensure authorized AI bots are not blocked.
   - Inspect `sitemap.ts` to confirm stable dates and proper route priorities.
2. **Deploy Machine-Readable Endpoints**:
   - Ensure `public/llms.txt` conforms to `llmstxt.org` link syntax.
   - Ensure `public/llms-full.txt` contains unabridged text (not a smaller summary).
   - Verify `src/app/feed.xml/route.ts` generates valid RSS 2.0 XML.
   - Verify `src/app/manifest.ts` returns proper icons and display modes.
3. **Inject and Validate Schemas**:
   - Validate with Google Rich Results Test and Schema.org Validator.
   - Ensure `Person` schema is active on `/about` and `FAQPage` schema is active on `/pricing` and service pages.
4. **Trigger Instant Discovery**:
   - Call `submitToIndexNow([urls])` upon publishing new routes.

---

# Common Failure Modes & Guardrails

- **Sitemap Timestamp Drift**: Using `new Date()` inside `sitemap.ts` causing daily crawler de-prioritization.
- **llms.txt Role Inversion**: Making `llms.txt` huge and `llms-full.txt` truncated. Always keep `llms.txt` as a fast curated link index and `llms-full.txt` as the unabridged corpus.
- **Schema/Content Mismatch**: Putting FAQs in schema that do not appear visibly on the rendered page (triggers Google structured data manual action penalty).
- **Broken Markdown Links**: Adding links to `.md` files in `llms.txt` without actually creating the corresponding files in `public/`.
- **Cargo-Cult SEO Waste**: Wasting effort on `meta keywords`, `humans.txt`, or programmatic doorway spam that invites algorithmic penalties.

---

# Interaction With Other Skills

- **`seo-engineer`**: This strategy skill defines the *architectural priorities and discovery file roadmap*; `seo-engineer` executes on-page meta tags, canonical logic, and crawl audits.
- **`seo-keyword-research-implementation`**: Feeds high-volume commercial search terms and local intent queries into the headings and direct-answer blocks.
- **`frontend-engineer`**: Implements visual page layouts (`/pricing`, `/about`) ensuring server-component rendering and semantic HTML5 hierarchy.
- **`ai-engineer`**: Coordinates with `public/llms.txt` and `public/*.md` to ensure knowledge base chunks reflect active site documentation for retrieval-augmented workflows.
