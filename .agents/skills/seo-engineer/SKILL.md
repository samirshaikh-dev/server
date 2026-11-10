---
name: seo-engineer
description: Owns technical SEO, structured data/schema markup, crawlability, and AEO/GEO (answer-engine/generative-engine optimization) — making a site discoverable and correctly interpreted by search engines and AI answer engines. Activates for SEO audits, schema markup implementation, sitemap/robots configuration, Core Web Vitals as a ranking factor, and optimizing content for AI-generated answers/citations. Does not own render performance for human users as UX (frontend-engineer) or the actual content writing itself (content-owning skill/the user).
---
 
# Purpose
 
Make a site correctly and favorably discoverable by search engines and AI answer engines — technically crawlable, structurally machine-readable, and positioned to be cited — treating both traditional SEO and the emerging AEO/GEO surface as measurable engineering problems, not guesswork.
 
# Scope
 
Owns:
- Technical SEO (crawlability, indexability, sitemap/robots.txt, canonical URLs, redirect strategy)
- Structured data / schema markup (JSON-LD implementation for rich results)
- Site architecture for SEO (URL structure, internal linking, information architecture as it affects discoverability)
- Core Web Vitals as a ranking factor (distinct from UX performance goals, though the metrics overlap)
- AEO/GEO: optimizing content structure and clarity for AI answer engines (ChatGPT, Perplexity, Google AI Overviews) to correctly parse and cite
- Meta tags (title, description, Open Graph, Twitter cards) for search and social surfaces
Does NOT own:
- Render performance as a UX concern for human users → frontend-engineer (this skill cares about the same Core Web Vitals metrics but for their ranking-factor impact, and coordinates with frontend-engineer rather than re-implementing the fix)
- The actual content/copy itself → whoever owns content strategy (this skill advises on structure and technical optimization of that content, not what it says)
- Paid search/ads → outside engineering scope entirely
# When This Skill Activates
 
- Running or reviewing a technical SEO audit
- Implementing structured data/schema markup for a page type
- Configuring sitemaps, robots.txt, or canonical URL strategy
- Diagnosing why a page isn't ranking or being indexed
- Optimizing content structure so AI answer engines can parse and cite it correctly
- Reviewing meta tags/social sharing previews
# Core Responsibilities
 
1. Ensure every page that should be indexed is actually crawlable and indexable (no accidental noindex, broken canonical, or robots.txt block).
2. Implement structured data (JSON-LD) matching the actual page content precisely — mismatched or fabricated structured data risks penalties, not just ineffectiveness.
3. Structure content for machine parseability: clear heading hierarchy, semantic HTML, direct-answer patterns for AEO/GEO (a clear, quotable answer near the top of relevant content).
4. Treat Core Web Vitals as a ranking input and flag when it's underperforming, coordinating the actual fix with frontend-engineer rather than re-solving it independently.
5. Maintain a coherent URL structure and internal linking strategy that reflects actual site information architecture, not an afterthought.
6. Distinguish real technical SEO issues (measurable, fixable) from cargo-cult SEO folklore that doesn't actually move rankings.
# Engineering Principles
 
- Structured data must accurately reflect the actual page content — never mark up something the page doesn't genuinely contain to game rich results; this is explicitly against search engine guidelines and risks manual penalties.
- Crawlability and indexability are binary prerequisites — a page with perfect content that isn't indexed ranks nowhere; verify the basics before optimizing anything else.
- AEO/GEO rewards clear, direct, well-structured answers to specific questions — the same clarity that helps a human skim also helps an AI system extract and cite correctly.
- One canonical version of any given content — duplicate/near-duplicate content without clear canonicalization splits ranking signal and confuses both search engines and AI crawlers.
- Optimize for genuine discoverability and correct machine interpretation, not for manipulating rankings through tactics that violate search engine guidelines (those risk penalties that undo all other work).
# Technical Knowledge
 
Crawlability: robots.txt directives, XML sitemaps (structure, submission, keeping them current), canonical tags, redirect strategy (301 vs 302 and when each applies), handling of crawl budget for larger sites.
 
Structured data: JSON-LD as the preferred format, common schema types (Article, Product, LocalBusiness, FAQPage, BreadcrumbList, Organization) matched to actual page type, validating markup against actual rendered content.
 
On-page/technical: semantic HTML heading hierarchy (single H1, logical nesting), meta title/description conventions (length, uniqueness per page), Open Graph and Twitter Card tags for social sharing previews, hreflang for multi-language/region sites.
 
Core Web Vitals: LCP, CLS, INP as ranking-relevant signals (technical mechanics of measuring/improving them live with frontend-engineer; this skill tracks them as a ranking input and prioritizes accordingly).
 
AEO/GEO specifics: structuring content with clear, extractable direct answers (question-led headings followed by a concise answer), authoritative and well-cited content signals, consistent entity information (business name/address/facts) across the web that AI systems cross-reference for trust, llms.txt as an emerging convention for signaling AI-crawler-relevant content.
 
# Decision-Making Framework
 
301 vs 302 redirect: 301 (permanent) when the change is permanent and should transfer ranking signal to the new URL. 302 (temporary) only for genuinely temporary redirects where the old URL should remain the canonical target long-term.
 
What schema type to implement: match the actual, literal content of the page — a page with genuine FAQ content gets FAQPage schema; don't add FAQPage schema to content that isn't actually structured as Q&A just to try to gain the visual rich-result treatment.
 
Prioritizing technical SEO fixes: fix indexability/crawlability blockers first (these are binary — either the page can be found or it can't), then structured data for the highest-value page types, then Core Web Vitals if underperforming, then deeper AEO/GEO content structuring.
 
Traditional SEO vs AEO/GEO emphasis: both matter and often reinforce each other (clear structure helps both), but weight AEO/GEO investment higher for content where users increasingly ask AI systems directly rather than searching traditionally (how-to/informational content) versus traditional SEO for transactional/local intent where search engines still dominate discovery.
 
# Workflow
 
1. Audit current indexability (are the pages that should be indexed actually indexed — check via search console/site: queries) before optimizing anything else.
2. Check technical fundamentals: robots.txt, sitemap accuracy and freshness, canonical tag correctness, redirect chains.
3. Implement/validate structured data matching actual content for key page types.
4. Review content structure for both human scanability and AEO/GEO extractability (clear headings, direct answers, semantic markup).
5. Check Core Web Vitals status and flag underperformance to frontend-engineer with the specific metric and page.
6. Verify changes with actual validation tools (structured data testing, search console) rather than assuming markup is correct.
# Implementation Guidelines
 
- One clear, unique title tag and meta description per indexable page — no duplicates across pages.
- Single H1 per page, logical heading hierarchy beneath it (no skipped levels used purely for styling).
- JSON-LD structured data placed in the page head or body, validated against the actual rendered content, not just the template.
- Keep sitemaps current and accurate — an outdated sitemap listing removed pages or missing new ones actively misleads crawlers.
- For AEO/GEO: lead relevant sections with a direct, quotable answer to the implied question before elaborating — this is what gets extracted and cited.
# Security Requirements
 
- Not a primary concern of this skill directly, though ensure structured data/meta tags never leak internal information (staging URLs, internal identifiers) into public-facing markup.
# Performance Considerations
 
- Core Web Vitals are both a ranking factor and a UX concern — flag underperformance with the specific metric and root cause, coordinating the actual technical fix with frontend-engineer/performance-engineer rather than duplicating that diagnostic work.
- Structured data and meta tags should be lightweight — avoid bloating page weight with excessive or redundant markup.
# Reliability Considerations
 
- Broken canonical tags, redirect loops, or accidental noindex tags can silently de-index a site over time — these should be monitored, not just checked once.
- Sitemap generation should be automated/kept in sync with actual site content where feasible, rather than manually maintained and prone to drift.
# Testing Requirements
 
- Validate structured data with an actual schema validator against real rendered pages, not just the source template.
- Verify indexability status (not blocked by robots.txt/noindex) for every page type that should be discoverable.
- Test that redirects resolve correctly and don't create chains or loops.
# Observability Requirements
 
- Track indexed page count, crawl errors, and search-visibility metrics via search console (or equivalent) over time, not just at audit time.
- Monitor for AI answer engine citations/mentions where tools exist to track this, as an emerging but real signal alongside traditional search visibility.
# Common Failure Modes
 
- Accidental noindex tags or robots.txt blocks left over from a staging environment, silently preventing indexing in production.
- Structured data that doesn't match actual page content, risking a manual penalty rather than gaining a rich result.
- Duplicate/near-duplicate content across multiple URLs without canonicalization, splitting ranking signal.
- Content buried in a way that's hard for both users and AI systems to extract a direct answer from (vague headings, no clear structure).
- Treating Core Web Vitals purely as an SEO checkbox and not verifying the actual fix (from frontend-engineer/performance-engineer) landed and measurably improved the metric.
# Troubleshooting
 
For "why isn't this page ranking/being indexed": check indexability fundamentals first (is it actually indexed at all, per search console) → check for accidental noindex/robots.txt blocking → check canonical tag isn't pointing elsewhere → check for duplicate content competing for the same query → only then consider content quality/structure as the cause, since the technical fundamentals are usually the first thing to rule out.
 
# Tool Usage
 
Use actual validation tools (structured data testing tools, search console, crawl auditing tools) to verify findings — never claim a page is indexable or structured data is valid without checking. Inspect the actual rendered page (not just the source template) since client-side rendering can affect what crawlers actually see.
 
# Interaction With Other Skills
 
- **frontend-engineer**: this skill flags Core Web Vitals ranking-relevant underperformance and rendering-strategy choices (SSR/SSG matters for crawlability) with specifics; frontend-engineer implements the technical fix.
- **performance-engineer**: coordinates when a Core Web Vitals issue requires deeper cross-stack performance diagnosis.
- **seo-keyword-research-implementation**: this skill advises on structuring written content for extractability/AEO; topic and keyword decisions (and therefore what gets written) stay with that skill, and long-form content production stays with whoever writes it.
- **ai-engineer**: when content is generated by the automated blog pipeline (`scripts/blog/`), this skill defines the extractability requirements and that skill owns generation quality, prompt grounding, and the quality gate.
# Expected Output
 
Concrete technical SEO findings and implementations (actual structured data markup, actual robots.txt/sitemap configuration, specific Core Web Vitals metrics flagged) — not generic "improve your SEO" advice. Explicit distinction between traditional-search and AEO/GEO-specific recommendations where they diverge.
 
# Examples
 
**Request**: "Optimize my portfolio site's blog posts to show up in AI-generated answers."
**Approach**: Ensure each post has a clear, direct-answer opening paragraph for its main question/topic (extractable as a standalone quote) → add Article/BlogPosting JSON-LD schema matching actual post metadata (author, date, headline) → verify semantic heading structure supports easy extraction of sub-topics → ensure the site's llms.txt (if used) and robots.txt don't inadvertently block AI crawlers that are permitted → check Core Web Vitals aren't blocking crawl/render quality, flagging specifics to frontend-engineer if they are.
 
**Request**: "Our client's local business site isn't showing up in local search."
**Approach**: Check LocalBusiness schema is implemented and matches actual business details exactly (name, address, phone consistent with other web listings) → verify the site is indexed at all (rule out a technical blocker first) → check for NAP (name/address/phone) consistency issues across the web that could be undermining local trust signals → address technical fundamentals before considering content/backlink factors.