# Tracking and Automation

Contents:
1. What GTM is and isn't
2. Events worth tracking
3. GTM mechanics
4. Reading the data
5. Automating the research pipeline

---

## 1. What GTM is and isn't

Google Tag Manager is a measurement and experimentation layer. It does not improve rankings, and saying otherwise is a common piece of bad SEO advice worth correcting if the person believes it.

What it does give: evidence about which parts of a portfolio people actually engage with, which turns profile optimization from guesswork into iteration.

```
Personal Website
      ↓
Google Tag Manager
      ↓
Google Analytics 4
      ↓
User / Event Data
      ↓
Performance Analysis
      ↓
Content Optimization
```

---

## 2. Events worth tracking

For a portfolio or personal site, the events that answer real questions:

```
portfolio_project_view     — which projects get attention
project_demo_click         — which projects are compelling enough to try
resume_download            — serious interest signal
contact_click              — the actual conversion
github_click               — where technical visitors go
linkedin_click             — where recruiter-type visitors go
skill_section_view         — whether people scroll that far
scroll_depth_75            — whether pages hold attention
outbound_link_click        — where people leave to
```

Recommend a handful, not all of them. Five well-defined events that get reviewed beat twenty that never do.

Give each event one or two useful parameters — `project_name` on `portfolio_project_view`, `destination` on `outbound_link_click` — so the data can be segmented later.

---

## 3. GTM mechanics

When explaining setup, cover the four pieces and how they relate:

- **Tags** — what fires (a GA4 event)
- **Triggers** — when it fires (click on `#resume-download`, scroll past 75%)
- **Variables** — what data comes along (click URL, page path, a custom `data-project` attribute)
- **Events** — the named things landing in GA4

Typical flow for a portfolio:

1. Install the GTM container snippet
2. Configure the GA4 configuration tag
3. Create a click trigger per meaningful interaction, targeting a stable selector or data attribute
4. Create a GA4 event tag per trigger, with parameters
5. Verify in GTM Preview mode
6. Mark the meaningful ones as key events (conversions) in GA4

Recommend stable `data-*` attributes or IDs for triggers rather than CSS classes, since classes change during redesigns and silently break tracking.

Also worth setting up, and free: Google Search Console. It's the only source of the person's own real query data — which searches surfaced their site, and where they ranked. For someone with no SEO tooling, this is the single highest-value connection.

---

## 4. Reading the data

After a few weeks there's enough to act on. Useful reads:

- Projects with high views but no demo clicks — the description isn't selling the work
- Pages with traffic but no scroll depth — the opening copy isn't landing
- Search Console queries that bring impressions but few clicks — the title or meta description needs rewriting
- Queries surfacing the site that don't match the target role — positioning is off

Feed these back into the keyword map and repeat. That loop is the point of the tracking.

---

## 5. Automating the research pipeline

Only design this when the person asks for automation. Shape:

```
Input (URL / Role / Stack)
        ↓
Research (fetch pages, SERPs, job postings)
        ↓
Keyword Extraction
        ↓
Keyword Classification
        ↓
Job Market Analysis
        ↓
Profile Analysis
        ↓
Gap Detection
        ↓
Recommendations
        ↓
GTM / GA4 Tracking
        ↓
Periodic Re-analysis
```

Reasonable building blocks: Python or Node for the pipeline, FastAPI for an internal API, n8n for scheduling and glue, PostgreSQL for storing keyword snapshots over time, React for a dashboard. Data sources: Search Console API, GA4 Data API, GTM API, and Semrush or Ahrefs if the person pays for them.

Two cautions worth passing on. First, only wire in an API when credentials actually exist — a pipeline that assumes an Ahrefs key nobody has is a pipeline that doesn't run. Second, storing keyword and ranking snapshots over time is what makes automation worth building at all; a one-shot script just repeats what a manual session already produced.

Respect robots.txt and terms of service in anything that fetches pages, and rate-limit politely.
