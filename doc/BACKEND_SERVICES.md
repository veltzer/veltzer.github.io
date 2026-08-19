# Backend Services for a Static Site

Notes on adding dynamic features -- forums, storage, counters, uploads -- to a
site that is otherwise static files on GitHub Pages.

Written because counterapi turned out to be cumbersome. That counter has since
been removed from the site altogether (see the DROPPED entry in
`doc/problems.txt`), so what follows is about dynamic features in general
rather than about restoring it. The short version is that its
CORS preflight rejects the `Authorization` header, so authenticated calls fail
from a browser even with a valid token, which forced a public workspace; and
the free tier caps at 5 public counters, which put per-page counting out of
reach.

**Figures below were checked against the vendors' own pricing pages in August
2026.** Free tiers in this market change often -- re-check before committing.

## The short answer

Yes, one class of product bundles storage + database + uploads + auth: it is
called **Backend-as-a-Service (BaaS)**. Supabase, Appwrite, Firebase and
PocketBase are the main ones.

**But no BaaS ships a forum.** A forum is an application, not a primitive.
Every option below covers three of the four things asked for and leaves the
forum to either be built on their database or handled by a separate,
purpose-built service.

So the realistic shape is *two* services, not one:

- a comments/forum service (giscus), and
- a BaaS or edge platform for counters, storage and uploads.

## Comparison

| | Storage | Counters | Uploads | Forum | Free tier | Pauses when idle? |
|---|---|---|---|---|---|---|
| **Cloudflare** (Workers/D1/R2/KV) | R2 10 GB | D1 or KV | R2 | no | 100k req/day | **no** |
| **Supabase** | 1 GB files, 500 MB Postgres | Postgres table | yes | no | 5 GB egress, 50k MAU | yes, after 1 week |
| **Appwrite** | 2 GB | DB table | yes | no | 5 GB bandwidth, 75k MAU | yes, after 1 week |
| **Firebase** | Firestore + Storage | Firestore | yes | no | varies | no |
| **PocketBase** | self-hosted | yes | yes | no | free, you host it | n/a |
| **giscus** | -- | -- | -- | **yes** | free, unlimited | no |

### The inactivity trap

This is the single most important line in that table for a personal blog.

**Supabase and Appwrite both pause free projects after 1 week of inactivity.**
For a low-traffic site that is not a hypothetical -- a quiet week means the
backend is asleep when the next reader arrives, and counters and uploads fail
until it wakes.

The usual workaround is a scheduled ping (a GitHub Actions cron hitting the
project twice a week) to reset the timer. That works, but it means the feature
depends on a keepalive job that can itself break silently, which is exactly the
kind of hidden dependency worth avoiding for something as small as a hit
counter.

**Cloudflare's free tier does not pause on inactivity.** For this site's
traffic profile that is the deciding difference.

## Recommended combination

**giscus for the forum, Cloudflare for everything else.**

### giscus (forum / comments)

Comments backed by GitHub Discussions. No database, no moderation panel to run,
no server. Free with no usage cap, no tracking and no ads.

Requirements: the repo must be public (this one is), have Discussions enabled,
and have the giscus app installed. Comments map to pages by URL, pathname or
title.

The real tradeoff: **readers must sign in with GitHub to comment.** For a blog
whose posts are mostly technical that is a mild filter; for the philosophy and
religion posts, which are the ones most likely to draw discussion, it is a real
barrier. Worth weighing honestly rather than assuming it is free of cost.

Note also that giscus documents itself as under active development and says
features may break or change as GitHub evolves Discussions.

### Cloudflare (counters, storage, uploads)

Free tier, all without an inactivity pause:

- Workers: 100,000 requests/day
- D1 (SQL): 5 GB storage, 5M row reads/day, 100k row writes/day
- KV: 1 GB, 100k reads/day, but only **1,000 writes/day**
- R2 (object storage): 10 GB-month, 1M class-A ops/month

For per-page counters, D1 is the right primitive, not KV: at ~80 posts the
1,000 writes/day KV ceiling is a real constraint, while D1's 100k writes/day is
not. A Worker owns the credentials server-side and sets its own CORS headers,
which structurally avoids the problem that made counterapi unusable -- the
browser never sends an `Authorization` header at all.

A Worker would also have reached the "each page" half of the old counter goal,
which counterapi's 5-counter free tier blocked. That goal has since been
dropped rather than solved -- noted here only so the capability is not
mistaken for an outstanding task.

## Alternatives worth knowing

- **PocketBase** -- a single Go binary with embedded SQLite, auth, file storage,
  realtime and an admin UI. No vendor, no free-tier games, no pausing. The cost
  is that you supply and maintain a host. Fits the taste already visible in this
  repo (zola, rsconstruct: single binaries, no runtime dependencies), and is
  the best option if self-hosting is acceptable.
- **Supabase** -- the most capable of the hosted BaaS options and plain Postgres
  underneath, so there is little lock-in. Reconsider it if the site ever needs
  real auth or relational queries; the inactivity pause is the only thing
  arguing against it here.
- **Firebase** -- mature and does not pause, but NoSQL and meaningful Google
  lock-in.
- **GoatCounter** -- not a BaaS, but still the right answer for *analytics* as
  opposed to a number displayed on the page. Per `doc/ANALYTICS.md` it stores
  only aggregate data, and its own GDPR page argues no consent banner is needed
  because no personally identifiable information is collected.

## Things to weigh before adding any of this

1. **A static site with a backend is no longer a static site.** Today the only
   operational dependency is `zola build` plus GitHub Pages. Each service added
   brings an account, an API key, a dashboard, and a thing that can be down
   while the site itself is up.
2. **Third-party JavaScript has a privacy cost.** giscus loads scripts from
   GitHub and Cloudflare from Cloudflare. That sits in tension with the
   reasoning in `doc/ANALYTICS.md` that recommended GoatCounter partly on
   privacy grounds.
3. **Comments need moderation.** giscus routes this through GitHub's own
   moderation tools, which is a genuine advantage over a self-built forum --
   but it is still recurring work, not a one-time setup.
4. **Free tiers move.** Everything above was verified in August 2026 and should
   be re-checked before any of it is relied upon.

## Sources

- https://supabase.com/pricing
- https://appwrite.io/pricing
- https://developers.cloudflare.com/workers/platform/pricing/
- https://giscus.app
- https://github.com/pocketbase/pocketbase
- https://www.goatcounter.com/help/gdpr
