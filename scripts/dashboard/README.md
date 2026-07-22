# Site traffic dashboard

Founder-only dashboard for justus.health pageviews, waitlist signups, and
founding-athlete CTA clicks, generated from PostHog. Nothing here is published;
the output directory and the IP config are gitignored because this repo is
public and served raw at justus.health.

## Usage

```bash
scripts/site-dashboard.sh              # last 30 days, opens in browser
scripts/site-dashboard.sh --days 7     # different window
scripts/site-dashboard.sh --demo       # sample data, no API key needed
```

## One-time setup

Create a PostHog **Personal API key**: us.posthog.com → Settings →
Personal API keys → scope **Query: Read**. Then either:

```bash
export POSTHOG_PERSONAL_API_KEY=phx_...
```

or save it in 1Password as an item named **PostHog Personal API Key**
(field `credential`) in the **Justus** vault — the script reads
`op://Justus/PostHog Personal API Key/credential` automatically.

## Excluding your own traffic

Two layers:

1. **Device opt-out (primary).** Visit any page once per browser with
   `https://justus.health/?internal=1`. That browser stops sending events
   entirely (persists in localStorage). `?internal=0` re-enables.
   Do this on your phone, laptop browsers, and any test devices.
2. **IP backstop (historical + forgotten devices).** `config.local.json`
   holds `exclude_ips`; every query filters those out. Update it when your
   home IP changes (`curl -s https://api.ipify.org`).

Queries also drop any event not from the `justus.health` host, which removes
localhost testing and preview noise.

## Notes

- Waitlist signups are `waitlist_submitted` events captured on form submit —
  available without a paid LaunchList account. Directionally accurate;
  LaunchList remains the source of truth for the actual list.
- Founding-athlete applications arrive via Slack + Airtable; the dashboard
  counts only the CTA clicks (`founding_athlete_application_clicked`).
