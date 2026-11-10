Read-only · public data · v1

# MEELTE Web API

Four read-only endpoints that return MEELTE's public ads and events, for building the SEO pages on meelte.com. This page covers access, the endpoints, every field, and the rules for using it safely.

Version **1** Live since **30 Oct 2026** Owner **MEELTE backend team**

[Rules](#rules) [Access](#access) [Endpoints](#endpoints) [Paging](#paging) [Examples](#examples) [What is returned](#returned) [Ad fields](#ads) [Event fields](#events) [Errors](#errors) [SEO notes](#seo)

## Rules for using it safely

This API reads from the same live database the MEELTE app uses, so read these before writing code.

### Do Required

- Call the API from your **server or build step** (SSR, ISR or static generation). Visitors' browsers and crawlers should never call it directly.
- **Cache every response.** Revalidate list pages every 10–15 minutes and detail pages every 15–60 minutes. One crawler visit must not equal one API call.
- Keep the key in an environment variable (for example `MEELTE_SUPABASE_ANON_KEY`) and send it in **headers**.
- Build and test against **dev**; point only production builds at **prod**.
- Use `has_ended` to decide whether an ad or event is still running.
- On `429` or `5xx`, back off and retry later. Keep at most 4 requests in flight.
- If something looks wrong (for example content you did not expect to be public), stop and tell MEELTE.

### Don't Never

- Never call anything except the four `web_*` endpoints: no `/rest/v1/<table>`, no storage API, no other RPC.
- Never send `POST`, `PATCH`, `PUT` or `DELETE`. This integration is `GET` only.
- Never ask for, accept or use a `service_role` key or a database password. This API needs only the anon key.
- Never commit the key to git, paste it in tickets or chats, or put it in production URLs (`?apikey=` is for quick manual tests only).
- Don't show internal fields on pages or in JSON-LD: user ids (`creator_id`, `created_by` on events, `dates_last_updated_by`), `status`, `reward_claimed`, `admin_status`, `photo_path`, `previous_*`.
- Don't upload, re-host or edit MEELTE images. Link to `photo_url` / `cover_url` (an image CDN that resizes on the fly is fine).

## Access

Both environments run the same API. Dev holds test data only.

| Environment | Base URL | Use for |
| --- | --- | --- |
| Dev | `https://rlorvocjvjnqunncfmsj.supabase.co/rest/v1/rpc/` | Local development, previews, testing |
| Prod | `https://itudwwxgpnxymhgdhgpw.supabase.co/rest/v1/rpc/` | The live meelte.com build only |

**Key.** Each environment has its own anon (public) key. MEELTE sends it to you privately. It only allows reading what this API returns. Send it in both headers on every request:

Headers

```
apikey: <MEELTE_SUPABASE_ANON_KEY>
Authorization: Bearer <MEELTE_SUPABASE_ANON_KEY>
```

A request without the key gets `401` "No API key found in request". That is also what you see when you paste the URL into a browser.

## Endpoints

All four are `GET` requests and return JSON. Parameters go in the query string. A parameter the endpoint does not know returns `404`, so send only the ones listed.

GET/web_list_ads

Ads that are running now, newest first. Returns an array of [ad objects](#ads).

| Parameter | Type | Default | Meaning |
| --- | --- | --- | --- |
| `p_limit` | integer | 24 | Page size. Values below 1 become 1, values above 50 become 50. |
| `p_category` | text | none | Exact, case-sensitive category name, for example `Groceries`. Leave it out (or send `All`) for every category. |
| `p_before_created_at` | timestamp | none | Cursor: `created_at` of the last row of the previous page. See [Paging](#paging). |
| `p_before_id` | text | none | Cursor: `id` of that same last row. |

GET/web_get_ad?p_id=\<ad id>

One ad by id, including ads that have ended (`has_ended: true`), so old shared links can still show an "ended" page. Returns an array with 0 or 1 item. Rejected ads are never returned.

GET/web_list_events

Public events that are running or upcoming, newest first. Same parameters as `web_list_ads`. Returns an array of [event objects](#events).

GET/web_get_event?p_id=\<event id>

One public event by id, including ended ones (`has_ended: true`). Returns an array with 0 or 1 item. Private (invite-only) and rejected events are never returned.

**Single object instead of an array.** Add the header `Accept: application/vnd.pgrst.object+json` to the two `get` endpoints to receive one object. If the id is unknown, the response is then `406`, which your site should turn into a 404 page.

## Paging

Lists use a cursor instead of page numbers, so pages stay fast and nothing is skipped when new items arrive.

1. Request the first page with no cursor.
2. Take the **last** row of that page. Send its `created_at` as `p_before_created_at` and its `id` as `p_before_id`. Always send both.
3. Repeat until a page comes back with fewer items than `p_limit`. That was the last page.

URL-encode the timestamp: the `+` in `+00:00` must be sent as `%2B`. `encodeURIComponent` or `URLSearchParams` does this for you. A timestamp that cannot be parsed returns `400`.

## Examples

Replace the key placeholder with the value from your environment.

curl · first page of ads (dev)

```
curl "https://rlorvocjvjnqunncfmsj.supabase.co/rest/v1/rpc/web_list_ads?p_limit=24" \
  -H "apikey: $MEELTE_SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $MEELTE_SUPABASE_ANON_KEY"
```

curl · one event as a single object (dev)

```
curl "https://rlorvocjvjnqunncfmsj.supabase.co/rest/v1/rpc/web_get_event?p_id=EVENT_ID" \
  -H "apikey: $MEELTE_SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $MEELTE_SUPABASE_ANON_KEY" \
  -H "Accept: application/vnd.pgrst.object+json"
```

Server-side JavaScript · fetch every live ad (for a sitemap)

```
const BASE = process.env.MEELTE_API_BASE; // e.g. https://itudwwxgpnxymhgdhgpw.supabase.co/rest/v1/rpc
const KEY = process.env.MEELTE_SUPABASE_ANON_KEY;
const HEADERS = { apikey: KEY, Authorization: `Bearer ${KEY}` };

async function getPage(fn, params) {
  const url = `${BASE}/${fn}?${new URLSearchParams(params)}`;
  const res = await fetch(url, { headers: HEADERS });
  if (!res.ok) throw new Error(`${fn} failed: HTTP ${res.status}`);
  return res.json();
}

export async function allLiveAds() {
  const limit = 50;
  const ads = [];
  let params = { p_limit: limit };
  for (;;) {
    const page = await getPage("web_list_ads", params);
    ads.push(...page);
    if (page.length < limit) break;
    const last = page[page.length - 1];
    params = { p_limit: limit, p_before_created_at: last.created_at, p_before_id: last.id };
  }
  return ads;
}
```

## What is returned

| Case | Lists | Get by id |
| --- | --- | --- |
| Running or upcoming (end date in the future) | Yes | Yes, `has_ended: false` |
| Ended, or no end date | No | Yes, `has_ended: true` |
| Rejected by MEELTE moderation | No | No (empty) |
| Private (invite-only) event | No | No (empty) |
| Ad or event that starts later | Yes | Yes, `has_ended: false` |

Changes made in the app or by MEELTE's admins show up in the API immediately; nothing is copied or delayed. The `status` field is stored by the app and can be out of date, so never use it to decide whether something is live.

## Ad fields

36 fields per ad. Timestamps are ISO 8601 in UTC (for example `2026-10-30T16:43:37.633664+00:00`); prices are numbers in Indian rupees (INR), as the app shows them with ₹. Any field can be `null` unless noted.

| Field | Type | Meaning | Show on page |
| --- | --- | --- | --- |
| `id` | text | Ad id. Use it in the URL `/ad/{id}`. Never null. | URL only |
| `product_name` | text | Main title of the ad. Never null (can be empty). | Yes |
| `brand_name` | text | Shop or brand name. Never null (can be empty). | Yes |
| `description` | text | Free text from the creator. Never null (can be empty). | Yes |
| `category` | text | Category name. `Other` / `Others` means the creator typed their own, see `custom_category`. | Yes |
| `custom_category` | text | Creator's own category when `category` is Other. | Yes |
| `photo_url` | text | Public URL of the main photo. | Yes |
| `ad_type` | text | `single` or `catalog`. A catalog ad's product list is not part of this API yet. | Optional |
| `final_price` | number | Price the customer pays (INR). Set when `discount_type` is `pricing`. | Yes |
| `original_price` | number | Price before the discount (INR). Show struck through when it is higher than `final_price`. | Yes |
| `discount_type` | text | `pricing` = show the two prices; `flat` = "FLAT {discount_percentage}% OFF"; `upto` = "UPTO {discount_percentage}% OFF". | Yes |
| `discount_percentage` | number | Percentage for `flat` / `upto`. | Yes |
| `location_name` | text | Readable place, as picked by the creator. | Yes |
| `lat`, `lng` | number | Map position of the ad. | Yes |
| `city`, `state`, `country` | text | Usually empty for ads today; don't depend on them. | If present |
| `start_at`, `end_at` | timestamp | When the offer starts and ends. | Yes |
| `has_ended` | boolean | `true` when `end_at` has passed or is missing. Always `false` in lists. Never null. | Drives the page state |
| `created_by` | text | Creator's display name (`Deleted User` for deleted accounts). | Yes |
| `likes_count`, `comments_count` | integer | Counts from the app. Never null. | Optional |
| `created_at` | timestamp | When the ad was posted; also the paging cursor. Never null. | Optional |
| `creator_id` | text | Internal user id of the creator. | No |
| `status` | text | Stored by the app; can be out of date. Use `has_ended`. | No |
| `admin_status` | text | Moderation state: `null` or `approved`. | No |
| `reward_claimed` | boolean | Internal app flag. | No |
| `photo_path` | text | Internal storage path of the photo. | No |
| `original_photo_url`, `original_photo_path` | text | Legacy; normally empty. | No |
| `previous_start_at`, `previous_end_at` | timestamp | Dates before an admin correction. | No |
| `dates_last_updated_by`, `dates_last_updated_at` | text, timestamp | Internal admin audit (staff user id and time). | No |

## Event fields

28 fields per event. Same formats as ads.

| Field | Type | Meaning | Show on page |
| --- | --- | --- | --- |
| `id` | text | Event id. Use it in the URL `/event/{id}`. Never null. | URL only |
| `title` | text | Event title. Never null (can be empty). | Yes |
| `description` | text | Free text from the host. Never null (can be empty). | Yes |
| `category`, `custom_category` | text | Same rules as for ads. | Yes |
| `cost` | number | Joining cost in INR. `0` means free (the app shows "FREE"). Never null. | Yes |
| `cover_url` | text | Public URL of the cover image. | Yes |
| `location_name` | text | Readable venue name. | Yes |
| `address` | text | Venue address typed by the host. | Yes |
| `lat`, `lng` | number | Map position of the venue. | Yes |
| `city`, `state`, `country` | text | Filled for some events only. | If present |
| `start_time`, `end_time` | timestamp | When the event starts and ends. | Yes |
| `has_ended` | boolean | `true` when `end_time` has passed or is missing. Always `false` in lists. Never null. | Drives the page state |
| `creator_name` | text | Host's display name (`Deleted User` for deleted accounts). | Yes |
| `creator_photo_url` | text | Host's profile photo. | Optional |
| `attendees_count`, `likes_count`, `comments_count` | integer | Counts from the app. Never null. | Optional |
| `created_at` | timestamp | When the event was posted; also the paging cursor. Never null. | Optional |
| `is_public` | boolean | Always `true` here. | No |
| `created_by` | text | Internal user id of the host. | No |
| `status` | text | Stored by the app; can be out of date. Use `has_ended`. | No |
| `admin_status` | text | Moderation state: `null` or `approved`. | No |
| `reward_claimed` | boolean | Internal app flag. | No |

## Errors and edge cases

Errors come back as JSON with `code`, `message`, `details` and `hint`.

| HTTP | When | What your site should do |
| --- | --- | --- |
| 200 `[]` | List is empty, or the id is unknown, rejected or private | Empty state, or a 404 page for a detail URL |
| 400 | A parameter has the wrong format (for example a bad cursor timestamp) | Fix the request; don't retry as is |
| 401 | No key, or a wrong key | Check the environment variable |
| 404 | Unknown parameter name (code `PGRST202`) | Send only the parameters listed above |
| 406 | Single-object header and no row (code `PGRST116`) | 404 page |
| 429 / 5xx | Too many requests, or a temporary problem | Serve the cached page; retry later with backoff |

## SEO notes

Agreed or recommended points for the meelte.com pages. Check the ones marked "confirm" with MEELTE before you ship them.

| Topic | Guidance |
| --- | --- |
| Page URLs | Keep `https://meelte.com/ad/{id}` and `https://meelte.com/event/{id}`. The app already shares these links, and on phones with the app installed they open the app. |
| Files that must keep working | If meelte.com moves to your hosting, whatever meelte.com serves today at these paths must keep working unchanged: `/.well-known/assetlinks.json` (Android app links), the iOS `apple-app-site-association` file if MEELTE has one, `/privacy.html`, `/terms.html`, `/safety.html` and `/acc-dlt.html` (account deletion page required by the Play Store). Get the files from MEELTE and plan the switch together. |
| Ended items | Show the page with a clear "This offer has ended" / "This event has ended" state, add `noindex`, and leave it out of the sitemap. **Confirm with MEELTE.** |
| Sitemap | Build it from the list endpoints (live items only), regenerated at most hourly. Use `created_at` as `lastmod`; there is no "last edited" time in the API. |
| Structured data | Ads: `Product` with an `Offer` (`priceCurrency` `INR`, `price` from `final_price`, `validFrom` / `priceValidUntil` from the dates). When `final_price` is empty (flat / upto discounts), don't invent a price. Events: `Event` with `startDate`, `endDate`, a `Place` (name, address, geo), `isAccessibleForFree` when `cost` is 0, and the host's name as `organizer`. Never put user ids in JSON-LD. |
| AI crawlers | MEELTE allows them. `robots.txt` should allow GPTBot, ClaudeBot, PerplexityBot and Google-Extended, as well as normal search crawlers. |
| Categories | There is no categories endpoint yet. Build category pages from the categories present in the list results, or ask MEELTE for the list. |

Questions, missing fields or anything unexpected: contact the MEELTE backend team before working around it. The API contract only changes through MEELTE; new fields will be announced on this page.