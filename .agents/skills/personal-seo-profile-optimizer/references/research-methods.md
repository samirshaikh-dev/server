# Research Methods

Contents:
1. Source labeling
2. Website / URL research
3. Competitor and comparative research
4. SERP research
5. Job-market research
6. SEO data sources and metrics
7. Handling missing data

---

## 1. Source labeling

Every substantive statement in a report carries one of three labels. This is what separates a useful audit from confident-sounding noise.

| Label | Means | Example |
| --- | --- | --- |
| `[Verified]` | Directly observed in a source consulted during this session | `[Verified]` The homepage H1 reads "Full Stack Engineer". |
| `[Inference]` | A reasonable read of observed evidence | `[Inference]` The site targets agency clients rather than employers, based on the pricing page and "book a call" CTAs. |
| `[Recommendation]` | A suggestion | `[Recommendation]` Move "React" into the H1. |

Never let an inference wear the clothes of measured data. "React developer is a high-volume keyword" is a fabrication unless a source said so; "React appears in the title of most postings sampled" is verifiable.

---

## 2. Website / URL research

Fetch the page. Do not infer content from the URL.

Extract:

- Page title and meta description
- H1, H2, H3 hierarchy — headings reveal intended topic structure
- Body copy and repeated terminology
- Technical vocabulary (frameworks, tools, protocols)
- Product / service vocabulary
- Industry vocabulary
- Named entities (companies, products, technologies, people)
- Internal link anchor text — reveals what the site considers its own important topics
- Search intent the page serves: informational, navigational, commercial, transactional
- Content structure and depth

Then separate signal from noise. A word appearing often isn't automatically a target keyword — navigation labels, boilerplate, and cookie notices repeat too. Strategic terms usually show up in more than one privileged position: title, H1, early body copy, anchor text, or meta description.

Sort findings into: primary, secondary, supporting/semantic, long-tail, technology, role, industry, brand/entity.

Do not fetch content behind logins, paywalls, or anything restricted.

---

## 3. Competitor and comparative research

When several URLs are provided — peers, people holding the target job, agencies in the same niche — research each with the same method and report differences: terminology one uses that another doesn't, positioning differences, how specific vs. generic each is.

Never declare a winner. Ranking people against each other isn't the point, and the person reading the report has context you don't. Present the delta and let them choose.

---

## 4. SERP research

Search the queries a hiring manager or client would actually type: `react developer portfolio`, `freelance n8n automation developer`, `hire ai engineer india`, and so on.

Look for:

- Result titles and how they're phrased
- Terminology that recurs across independent results
- People-also-ask style questions
- Featured snippet framing
- Related searches
- Common page structures among top results

This is qualitative language research, not rank tracking. Its purpose is finding the words real people use, which often differ from internal job-title language ("automation engineer" vs. "workflow developer").

---

## 5. Job-market research

Sample real, current postings for the target role — ideally 8–15 across a few sources, and in the person's target geography if they have one.

Record recurring: job titles, technologies, frameworks, responsibilities, architecture terms, tools, certifications, soft skills, industry terms.

Sort into:

- **Frequently requested** — appears across most postings sampled
- **Emerging** — appears in recent postings, not yet standard
- **Specialized** — matters in a niche, not across the role

Frequency claims must be honest about their basis. Write it like this:

> `[Verified]` Across 12 "AI Engineer" postings sampled in September 2026 (LinkedIn, Wellfound), Python appeared in 11 and RAG or retrieval-augmented generation in 7.

Never write "in high demand" as a bare assertion. Either cite what was sampled and when, or don't make the claim.

---

## 6. SEO data sources and metrics

If an SEO data source is genuinely accessible — Semrush, Ahrefs, Google Keyword Planner, Search Console, Google Trends, or another reputable API with working credentials — use it and collect: keyword, search volume, difficulty, intent, CPC, ranking position, traffic estimate, SERP features, related keywords.

Access means credentials or a connected tool that works right now. An API existing in the world is not access. If the person mentions having Search Console or Semrush, ask whether they can export or connect it rather than assuming.

---

## 7. Handling missing data

Most sessions will have no SEO API. This is fine and the report is still valuable — keyword relevance, profile gaps, and copy quality don't require volume data.

State the limitation once, near the top:

> `[Note]` No SEO data source was available in this session, so search volume, difficulty, and ranking data are marked `Data unavailable`. Keyword selection below is based on page content, job postings sampled, and SERP language.

Then write `Data unavailable` in the relevant table cells. Never leave a plausible-looking number in a column just because the column exists.

If the person wants real metrics, tell them what would get it: connecting Search Console for their own site's actual query data (free), or a Semrush/Ahrefs trial for competitive volume.
