---
name: seo-keyword-research-implementation
description: Analyzes a website, researches relevant search keywords (primary, secondary, long-tail, semantic, commercial-intent, location-based), maps them to pages without cannibalization, and implements them across titles, meta descriptions, headings, content, URLs, alt text, internal links, structured data, and FAQ sections. Use this skill whenever the user asks to research keywords, do keyword research, improve rankings for specific terms, optimize a page/site for search, plan content around keywords, fix keyword cannibalization, or asked to grow organic traffic — even if they don't say "SEO" explicitly (e.g. "what should I write about to rank for X", "why is this page not showing up for [term]", "help me plan blog topics that will actually get found"). Complements seo-engineer (which owns technical crawlability, schema mechanics, and Core Web Vitals as a ranking factor) by owning the keyword strategy and on-page content layer built on top of that technical foundation.
---

# Purpose

Turn keyword research into a defensible, business-relevant content and on-page strategy, then implement it naturally across a real site — without fabricating metrics, without keyword stuffing, and without touching a page before understanding what it's actually for.

# Scope

Owns:
- Keyword research (primary, secondary, long-tail, semantic/LSI, commercial-intent, location-based)
- Search intent classification and keyword clustering
- Competitor/SERP content analysis for target terms
- Keyword-to-page mapping and cannibalization resolution
- On-page implementation: titles, meta descriptions, headings, body content, URLs/slugs, image alt text, internal linking/anchor text, FAQ sections
- Content gap analysis and new-page recommendations driven by keyword opportunity

Does NOT own (hand off instead):
- Technical crawlability, robots.txt/sitemap mechanics, canonical strategy, Core Web Vitals diagnostics, and schema *mechanics* → **seo-engineer** (this skill still decides *which* schema type and *what* FAQ content to mark up; seo-engineer implements/validates the markup itself when the two overlap)
- The site's actual rendering/component code → **frontend-engineer**
- Paid search/ads → outside scope entirely
- Brand voice/content strategy decisions that aren't keyword-driven → whoever owns content strategy; this skill optimizes structure and terms within that voice, not the voice itself

# When This Skill Activates

- "Do keyword research for [site/topic]"
- "Why isn't this page ranking for [term]"
- "What should I write about to get found for X"
- "Optimize this page/post for SEO"
- "Help me plan a content calendar / blog topics"
- "Are we cannibalizing keywords across these pages"
- "Add FAQ schema / expand this page's headings for search"
- Any request implying growth of organic search or AI-answer-engine visibility through content/terms rather than pure technical fixes

# Non-Negotiable Rules

1. **Never fabricate data.** No invented search volume, keyword difficulty scores, ranking positions, or competitor traffic numbers. If real metrics are needed and no tool/data source is available, say so explicitly and work from qualitative signal (SERP inspection, actual competitor content, on-page evidence) instead of making numbers up.
2. **Understand before you touch.** Never edit a page's copy, titles, or structure until you know what that page is actually for, who it serves, and what already exists on it.
3. **Users first, engines second.** Every implementation must read naturally to a human. If a change would only make sense to a crawler, don't make it.
4. **No stuffing, no cannibalization.** Don't force the same primary keyword onto multiple pages without a clear strategic reason (e.g. deliberate hub-and-spoke). Don't repeat a term unnaturally to hit a density target — density targets aren't a real ranking factor.
5. **Preserve meaning and voice.** Rewrites must keep the original intent and brand tone. This is an optimization pass, not a rewrite-from-scratch pass, unless the user asks for the latter.
6. **Prioritize business value over vanity volume.** A lower-volume keyword that matches real user/business intent beats a high-volume irrelevant one.
7. **Match the stack.** Before implementing anything in a codebase, inspect the actual project (framework, CMS, templating, existing conventions) and follow it — don't assume Next.js/React/WordPress by default.
8. **Explain every change.** For each implemented or recommended change: what it was, why it changed, and the expected SEO benefit.

# Workflow

Run this pipeline top to bottom; each stage's output feeds the next. Skip stages the user has already completed, but don't skip understanding the site itself.

1. **Website Analysis** — purpose, business model, target audience, products/services, industry, existing site structure.
2. **SEO Audit** — inventory existing titles, meta descriptions, headings, URLs, content, internal links, and current keyword usage per page. Flag content gaps, weak/missing metadata, cannibalization, and obvious technical issues (hand technical issues to seo-engineer, but note them).
3. **Keyword Research** — generate candidate keywords across type (primary/secondary/long-tail/semantic/commercial-intent/location-based); see "Keyword Research Guidance" below.
4. **Search Intent Analysis** — classify each candidate as informational, navigational, commercial, or transactional; discard/deprioritize mismatches against the page's actual purpose.
5. **Competitor/SERP Research** — see "Competitor & SERP Research" below.
6. **Keyword Clustering** — group keywords into topic clusters by shared intent and semantic relatedness.
7. **Keyword Mapping** — assign each cluster to one existing page, or recommend a new page if no good landing page exists; see "Keyword Mapping" below.
8. **Content Optimization** — rewrite/expand content per page per the mapping; see "Content Optimization Guidelines."
9. **Technical Implementation** — apply on-page changes (titles, metas, headings, URLs, alt text, internal links, FAQ, structured-data recommendations) matching the site's actual stack.
10. **Validation** — re-check every implemented change for natural language, correct mapping, no stuffing, no new cannibalization.
11. **SEO Report** — before/after summary; see "Validation & Reporting."

# Keyword Research Guidance

Keyword types to cover, per relevant page/topic:
- **Primary**: the single main term the page should be found for.
- **Secondary**: closely related terms the same page can also reasonably rank for.
- **Long-tail**: specific, lower-competition, often multi-word phrases with clear intent — usually the fastest realistic wins for smaller/newer sites.
- **Semantic/LSI**: conceptually related terms and entities that signal topical depth to both search engines and AI answer engines.
- **Commercial-intent**: terms signaling purchase/conversion readiness ("best," "buy," "pricing," "near me," "vs").
- **Location-based**: geo-modified terms when the business serves specific areas (city/region + service).

Sourcing keywords:
- Prefer actual data sources (Search Console, Keyword Planner, SEMrush/Ahrefs, or whatever tool the user has access to) for volume/difficulty when the user needs real numbers or has one connected.
- Without a connected data tool, do qualitative research instead: web_search for the terms, inspect actual SERP results and "People also ask" content, note what real competitors target — but present this as qualitative signal, not as volume/difficulty numbers. Never assign a number to something you didn't retrieve from a real source.
- Always tie keyword suggestions back to the business's actual products/services/audience from Stage 1 — relevance filters before volume does.

# Competitor & SERP Research

- Identify who actually ranks for target terms (via web_search/SERP inspection), not assumed competitors.
- Analyze their content structure: headings used, topics covered, depth, format (guide vs. product page vs. FAQ), and what intent they're clearly serving.
- Look for gaps: questions they don't answer, structure that's hard to scan, thin content, missing comparison/decision-support content — these are the openings.
- The goal is "genuinely more useful/complete," not "copy their structure." Never reproduce competitor copy; synthesize the gap into original content recommendations.

# Keyword Mapping

- One primary keyword (and its cluster) per page — this is the core anti-cannibalization rule.
- Check existing pages first: does a page already substantially serve this intent? Map there rather than creating a duplicate.
- Only recommend a new page when: (a) an important cluster has no reasonable existing home, and (b) the intent is distinct enough from existing pages to not cannibalize them.
- When two existing pages already compete for the same term, resolve it — don't just document it: consolidate, differentiate the intent/angle of each, or canonicalize (flag the canonical decision to seo-engineer if it's a technical canonical tag).
- Document the mapping explicitly: keyword cluster → target page → role of that page in the cluster (pillar vs. supporting).

# Content Optimization Guidelines

- Rewrite/expand in the site's existing voice — read a few existing pages first if voice isn't obvious.
- Lead relevant sections with a direct, clear answer to the implied question (helps both human scanners and AI answer engines) before elaborating.
- Improve genuine thinness or gaps identified in competitor research; don't pad for length.
- Keep one clear H1 per page; logical H2/H3 nesting that reflects real content structure, not keyword-target insertion points.

# On-Page Implementation Checklist

Apply per mapped page, matching the site's actual stack/CMS conventions:

- **Title tag**: unique per page, primary keyword near the front, natural phrasing, within typical display length.
- **Meta description**: unique per page, includes primary/secondary keyword naturally, written to earn the click (not just describe).
- **Headings**: single H1 containing the primary keyword or a close natural variant; H2/H3s reflect secondary/long-tail terms where they genuinely organize the content.
- **Body content**: natural integration, no density targets, semantic/related terms used where they'd appear in genuine expert writing.
- **URL/slug**: short, descriptive, keyword-relevant, consistent with existing site URL conventions — don't restructure existing URLs without flagging redirect implications to seo-engineer.
- **Image alt text**: descriptive of the actual image, includes keyword only when genuinely accurate — never keyword-stuff alt text.
- **Internal links/anchor text**: link to/from topically related pages using descriptive (not generic "click here") anchor text; support the pillar/supporting structure from the mapping stage.
- **Structured data**: recommend the schema type that matches actual page content (Article, Product, LocalBusiness, FAQPage, BreadcrumbList); hand implementation/validation to seo-engineer when it's a pure markup task, or implement directly if it's simple and within this skill's edit.
- **FAQ sections**: build from real "People also ask"/competitor-gap questions found in research, each with a direct, extractable answer.

# Technical Awareness

- Note framework/CMS-relevant constraints (Next.js metadata API, WordPress Yoast/RankMath fields, Django template blocks, static site frontmatter, etc.) and implement within them — inspect the actual project first.
- Flag (don't silently fix) anything touching canonical URLs, indexing directives, robots.txt, sitemap, or Core Web Vitals — route to **seo-engineer**.
- Consider mobile usability and page structure impact of content changes, but defer deep Core Web Vitals/performance diagnosis to seo-engineer/frontend-engineer/performance-engineer.

# Validation & Reporting

For every engagement, produce a report that includes:
- **Before/after** for each changed element (title, meta, headings, key content, URL if changed).
- Clear labeling of **existing content**, **recommended changes**, and **newly created content** — never blur these.
- The **keyword mapping table**: cluster → page → intent → role.
- **Prioritization** of remaining recommendations by impact, effort, and urgency (e.g. quick on-page wins first, new-page content investments later).
- Explicit note of anything **out of scope** and handed to another skill (seo-engineer, frontend-engineer, content strategy owner), with what was flagged.
- No invented metrics anywhere in the report — qualitative findings stay qualitative unless backed by a real retrieved number.

# Common Failure Modes

- Fabricating search volume or difficulty to make a recommendation look more rigorous than the available data supports.
- Mapping the same primary keyword to multiple pages, splitting ranking signal (cannibalization).
- Editing content before understanding the page's actual purpose or audience.
- Keyword stuffing headings, alt text, or anchor text past the point of natural readability.
- Copying competitor structure/content wholesale instead of synthesizing genuine gaps.
- Recommending new pages for keyword clusters that a existing page could have reasonably absorbed.
- Implementing on-page changes that ignore the site's actual framework/CMS conventions.

# Interaction With Other Skills

- **seo-engineer**: hands off structured-data markup implementation/validation, robots.txt/sitemap/canonical mechanics, and Core Web Vitals diagnostics; receives back technical blockers that affect which pages are even worth targeting with keywords.
- **frontend-engineer**: hands off component/rendering-level implementation when on-page changes require code beyond content/metadata edits.
- **ui-ux-engineer**: coordinates when heading/content restructuring has layout implications.
- **content-owning skill/the user**: this skill optimizes structure and keyword integration; final brand-voice sign-off stays with whoever owns content strategy.

# Expected Output

Concrete keyword research (typed and clustered, with intent classification), an explicit keyword-to-page map, actual before/after on-page implementations (not generic "add more keywords" advice), and a prioritized SEO report distinguishing existing/changed/new content — grounded only in real retrieved data, never fabricated metrics.