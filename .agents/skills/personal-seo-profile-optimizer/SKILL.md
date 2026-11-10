---
name: personal-seo-profile-optimizer
description: Research keywords and search language for a person's professional presence, then turn that research into concrete optimization recommendations for LinkedIn, GitHub, a portfolio or personal website, a resume, project descriptions, and bios. Use this whenever someone wants to be found more easily by recruiters, clients, or search engines — including requests like "optimize my LinkedIn headline", "why isn't my portfolio ranking", "what keywords should a React developer use", "review my GitHub profile", "rewrite my About section", "analyze this site's keywords", "help me rank for AI engineer", or any request to audit, rewrite, or keyword-research a professional profile, resume, personal site, or project description — even if the person never says "SEO" or "keywords".
---

# Personal SEO Research & Profile Optimization

Research first, recommend second. The value of this skill is that every suggested keyword traces back to something real — the person's actual experience, a page that was read, a job posting that was found, or a clearly labeled inference — rather than a plausible-sounding list generated from nothing.

Work like a blend of SEO researcher, technical recruiter, personal branding strategist, and web analytics specialist. Priority order when these conflict:

**Accuracy → Relevance → Natural language → Evidence → Actionability → keyword quantity (last).**

## The hard rules

These exist because a profile that overstates skills fails the interview, and invented metrics destroy trust in everything else in the report.

- **Never fabricate data.** No made-up search volume, keyword difficulty, ranking position, traffic, CPC, backlink counts, trend lines, or job-market percentages. If a number isn't available from a source actually consulted, write `Data unavailable`.
- **Never recommend claiming a skill the person hasn't demonstrated.** A keyword that requires unproven experience gets labeled `LEARN FIRST → then consider adding` and goes in its own section, never in the "add this to your headline" list.
- **Never keyword-stuff.** Recommendations must read like a human wrote them. If a rewritten About section sounds like a tag cloud, it's wrong.
- **Label every claim.** Each finding is `[Verified]` (from a source consulted in this session), `[Inference]` (a reasonable read of that evidence), or `[Recommendation]` (a suggestion). See `references/research-methods.md` for how to apply these consistently.
- **GTM/GA4 do not affect rankings.** Treat them as measurement, never as an SEO lever.

## Step 1 — Read what you were given, then start

Don't interrogate the person before producing anything. Inputs arrive in many shapes; match the shape and go:

| What they provided | What to prioritize |
| --- | --- |
| Role + stack only | Role and stack keyword maps, job-market language. Produce a preliminary map immediately. |
| A URL | Website research first, then keywords derived from it. |
| An existing profile, resume, or README | Gap analysis first — present / missing / underused / unsupported. |
| Multiple URLs | Comparative research. Report differences; do not declare a winner. |
| A specific platform ("my LinkedIn") | Scope the report to that platform's sections, skip the rest. |
| Very little ("help me get found") | Ask only for target role and current profile/site link, then proceed. |

Ask at most one clarifying question, and only when the answer changes the output substantially (e.g. no target role at all). Otherwise state assumptions inline and keep going.

## Step 2 — Research

Use the tools actually available. Web search and page fetching for websites, SERP language, and job postings. SEO APIs (Semrush, Ahrefs, Search Console, Keyword Planner, Trends) only when credentials genuinely exist — otherwise say so plainly and rely on qualitative research.

Full method — what to extract from a page, how to read SERPs, how to sample job postings without overclaiming, how to handle missing data: `references/research-methods.md`.

When a URL is provided, read it rather than guessing from the domain name. Extract title, meta description, heading hierarchy, repeated terminology, technical and industry vocabulary, entities, and the search intent the page is serving. Not every word on a page is a target keyword — distinguish strategic terms from incidental ones.

## Step 3 — Build the keyword map

Generate from three engines, then merge and dedupe:

1. **Role engine** — job titles and their variants, core responsibilities, engineering concepts, and the natural phrases people actually search.
2. **Stack engine** — each technology, its ecosystem, and genuinely natural combinations (`React + Node.js` yes; `PostgreSQL + Tailwind` no).
3. **Evidence engine** — terminology harvested from the researched site, competitor pages, SERPs, and job postings.

Worked examples of all three, plus the combination rules: `references/keyword-engines.md`.

Classify every keyword that reaches the report as Primary, Secondary, Technical, Role, Skill, Semantic, Long-tail, Industry, or Entity. Rate relevance qualitatively — `High` / `Medium` / `Low`. Don't invent numeric scores or a "best keyword" ranking unless asked; a false precision ranking invites people to optimize for the wrong term.

## Step 4 — Gap analysis

When existing profile content is available, sort every relevant keyword into exactly four buckets:

- **Present** — already there and reading naturally.
- **Missing** — supported by their experience but absent from the text.
- **Underused** — the concept is implied but never named in searchable language (e.g. they describe building a design system but never write "component architecture").
- **Unsupported** — relevant to the target role but unproven by anything they've shown. This bucket is the integrity check. Label it `LEARN FIRST` and keep it separate from recommendations.

## Step 5 — Platform recommendations

Write actual copy, not instructions to write copy. A headline recommendation means a headline they can paste.

Detailed playbooks — LinkedIn headline formulas and About structure, GitHub bio/repo/README patterns, website metadata and project pages, technical SEO checklist, resume ATS notes: `references/platform-playbooks.md`.

Scope to whatever platforms are in play. Offer 2–3 variations for anything short and high-leverage (headline, bio, meta description) since fit is personal.

## Step 6 — Tracking and next steps

Recommend GA4 events worth measuring and, if relevant, how to wire them through GTM. Event list and the measurement architecture: `references/tracking-and-automation.md`. That file also covers building an automated pipeline if the person asks for one.

Close with a sequenced action plan. Positioning first, because every downstream asset inherits it:

```
1. Fix positioning (target role + primary keyword)
2. LinkedIn (highest recruiter traffic, fastest to change)
3. GitHub (bio, pinned repos, READMEs)
4. Website (titles, H1s, project pages, technical SEO)
5. Tracking (GA4 events)
6. Monitor search and engagement data
7. Iterate
```

Adjust the order when their situation calls for it — someone job hunting next week should not start with sitemap work.

## Report format

Use this structure, dropping sections that don't apply to what was asked. A person who only asked about their LinkedIn headline should not receive a twelve-section audit.

```
## 1. Research Summary
What was researched, with what tools, and what wasn't available.

## 2. Primary Keywords
| Keyword | Category | Relevance | Source |

## 3. Secondary Keywords
| Keyword | Category | Relevance |

## 4. Technical Keywords
Grouped: Languages · Frameworks · Libraries · Databases · Cloud · DevOps · Automation · APIs

## 5. Role Keywords

## 6. Long-Tail Keywords

## 7. Job-Market Language
With source and time period on any frequency claim.

## 8. Profile Gap Analysis
Present / Missing / Underused / LEARN FIRST

## 9. LinkedIn
Headline variations · About strategy · Experience · Skills

## 10. GitHub
Bio · Repo names and descriptions · README keywords

## 11. Website
Title · Meta description · H1 · Project pages · Technical SEO

## 12. Tracking

## 13. Action Plan
```

Keep tables scannable — a 90-row keyword table is less useful than 25 well-chosen rows with the rest summarized. Lead the report with the two or three findings that matter most; people act on the top of the page.

## Worked example, compressed

**Input:** "I'm a backend dev, mostly Node and Postgres, trying to get AI engineering roles. Here's my LinkedIn headline: `Software Developer | Passionate about technology`"

**Good response shape:** Flag the headline as the biggest problem — it contains no role keyword, no technology, and no specialization, so it's invisible to recruiter search. Research current AI engineering postings. Produce a keyword map separating what they can claim today (Node.js, PostgreSQL, REST APIs, backend architecture) from the bridge terms their target role demands (LLM integration, RAG, prompt engineering, vector databases) — the latter marked `LEARN FIRST` unless they confirm experience. Offer three concrete headlines using only supported claims, e.g. `Backend Engineer | Node.js · PostgreSQL · REST APIs | Building toward AI/LLM systems`. Then note that "building toward" is honest positioning while `AI Engineer` is not yet earned.

**Bad response shape:** A headline stuffed with AI keywords they can't defend, plus a table of invented search volumes.
