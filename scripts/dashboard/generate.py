#!/usr/bin/env python3
"""Justus site-traffic dashboard generator.

Queries the PostHog project that instruments justus.health and renders a
single-file HTML dashboard (stdlib only, no dependencies).

Usage:
    python3 scripts/dashboard/generate.py [--days 30] [--demo] [--out PATH]

Auth (either works):
    export POSTHOG_PERSONAL_API_KEY=phx_...          # a Personal API key with
                                                     # "Query" read scope
    # or store it in 1Password as:
    #   op://Justus/PostHog Personal API Key/credential

Filters applied to every query:
    - only events from the live host (justus.health) — drops localhost,
      file://, and preview noise
    - excludes IPs listed in scripts/dashboard/config.local.json (gitignored)
    - browsers opted out via https://justus.health/?internal=1 never send
      events at all

Output goes to scripts/dashboard/out/ (gitignored — this repo is public).
"""

import argparse
import datetime as dt
import html
import http.client
import json
import os
import pathlib
import random
import subprocess
import sys
import urllib.error
import urllib.request

POSTHOG_API = "https://us.posthog.com"
PROJECT_TOKEN = "phc_pbMi5H1xZJmtZDDOw3plQzjBzs4dt8ohf1nY54Nl9N8"
OP_SECRET_REF = "op://Justus/PostHog Personal API Key/credential"
LIVE_HOST = "justus.health"

HERE = pathlib.Path(__file__).resolve().parent

# Chart mark color validated against #FAF9F7 (lightness band, chroma floor,
# contrast >= 3:1). The brand green #5C8A5C fails the chroma floor as a data
# color, so marks use this deeper step of the same hue; UI chrome keeps the
# site tokens.
MARK = "#4F8A4F"
MARK_HOVER = "#3E6E3E"


# ── auth ──────────────────────────────────────────────────────────────────

def resolve_api_key():
    key = os.environ.get("POSTHOG_PERSONAL_API_KEY", "").strip()
    if key:
        return key
    try:
        out = subprocess.run(
            ["op", "read", OP_SECRET_REF],
            capture_output=True, text=True, timeout=60,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    sys.exit(
        "No PostHog personal API key found.\n"
        "Create one at https://us.posthog.com → Settings → Personal API keys\n"
        "(scope: Query → Read), then either:\n"
        "  export POSTHOG_PERSONAL_API_KEY=phx_...\n"
        f"or save it in 1Password as {OP_SECRET_REF}"
    )


def api_get(key, path):
    req = urllib.request.Request(
        POSTHOG_API + path, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except (urllib.error.URLError, http.client.HTTPException, OSError) as e:
        if isinstance(e, urllib.error.HTTPError):
            raise
        sys.exit(f"Could not reach PostHog ({e}). Check the network and the "
                 "API key, then rerun.")


def discover_project_id(key):
    try:
        projects = api_get(key, "/api/projects/").get("results", [])
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            sys.exit("PostHog rejected the API key (401/403). Check the key "
                     "and that it has the Query read scope.")
        raise
    for p in projects:
        if p.get("api_token") == PROJECT_TOKEN:
            return p["id"]
    if len(projects) == 1:
        return projects[0]["id"]
    sys.exit("Could not find the Justus project among this key's projects.")


def hogql(key, project_id, query):
    body = json.dumps({"query": {"kind": "HogQLQuery", "query": query}}).encode()
    req = urllib.request.Request(
        f"{POSTHOG_API}/api/projects/{project_id}/query/",
        data=body,
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp).get("results", [])
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        sys.exit(f"PostHog query failed ({e.code}) for:\n{query}\n{detail}")
    except (urllib.error.URLError, http.client.HTTPException, OSError) as e:
        sys.exit(f"Could not reach PostHog ({e}). Check the network and "
                 "rerun.")


# ── queries ───────────────────────────────────────────────────────────────

def load_excluded_ips():
    cfg = HERE / "config.local.json"
    if cfg.exists():
        try:
            ips = json.loads(cfg.read_text()).get("exclude_ips", [])
            return [ip for ip in ips if ip.strip()]
        except (json.JSONDecodeError, AttributeError):
            print(f"warning: could not parse {cfg}, ignoring", file=sys.stderr)
    return []


def base_filter(ips):
    clause = f"properties.$host = '{LIVE_HOST}'"
    if ips:
        quoted = ", ".join("'" + ip.replace("'", "") + "'" for ip in ips)
        clause += f" AND coalesce(properties.$ip, '') NOT IN ({quoted})"
    return clause


def fetch_data(key, project_id, days, ips):
    base = base_filter(ips)
    window = f"timestamp >= now() - INTERVAL {days} DAY"

    daily = hogql(key, project_id, f"""
        SELECT toDate(timestamp) AS day,
               count() AS views,
               count(DISTINCT distinct_id) AS visitors
        FROM events
        WHERE event = '$pageview' AND {base} AND {window}
        GROUP BY day ORDER BY day
    """)

    totals = hogql(key, project_id, f"""
        SELECT count(), count(DISTINCT distinct_id)
        FROM events
        WHERE event = '$pageview' AND {base} AND {window}
    """)

    pages = hogql(key, project_id, f"""
        SELECT coalesce(nullif(properties.$pathname, ''), '/') AS path,
               count() AS views,
               count(DISTINCT distinct_id) AS visitors
        FROM events
        WHERE event = '$pageview' AND {base} AND {window}
        GROUP BY path ORDER BY views DESC LIMIT 15
    """)

    sources = hogql(key, project_id, f"""
        SELECT coalesce(
                 nullif(properties.utm_source, ''),
                 if(coalesce(properties.$referring_domain, '$direct') = '$direct',
                    'direct', properties.$referring_domain)
               ) AS source,
               count() AS views,
               count(DISTINCT distinct_id) AS visitors
        FROM events
        WHERE event = '$pageview' AND {base} AND {window}
        GROUP BY source ORDER BY views DESC LIMIT 12
    """)

    def event_counts(event):
        in_window = hogql(key, project_id, f"""
            SELECT count() FROM events
            WHERE event = '{event}' AND {base} AND {window}
        """)
        all_time = hogql(key, project_id, f"""
            SELECT count() FROM events
            WHERE event = '{event}' AND {base}
        """)
        return (in_window[0][0] if in_window else 0,
                all_time[0][0] if all_time else 0)

    signups_w, signups_all = event_counts("waitlist_submitted")
    cta_w, cta_all = event_counts("founding_athlete_application_clicked")

    return {
        "daily": [(str(r[0])[:10], int(r[1]), int(r[2])) for r in daily],
        "views_total": int(totals[0][0]) if totals else 0,
        "visitors_total": int(totals[0][1]) if totals else 0,
        "pages": [(r[0], int(r[1]), int(r[2])) for r in pages],
        "sources": [(r[0], int(r[1]), int(r[2])) for r in sources],
        "signups": (signups_w, signups_all),
        "cta": (cta_w, cta_all),
    }


def demo_data(days):
    rng = random.Random(42)
    today = dt.date.today()
    daily = []
    for i in range(days):
        day = today - dt.timedelta(days=days - 1 - i)
        views = max(0, int(6 + i * 1.1 + rng.gauss(0, 4)) +
                    (8 if day.weekday() >= 5 else 0))
        daily.append((day.isoformat(), views,
                      max(0, int(views * 0.62 + rng.gauss(0, 2)))))
    views_total = sum(v for _, v, _ in daily)
    return {
        "daily": daily,
        "views_total": views_total,
        "visitors_total": int(views_total * 0.55),
        "pages": [("/", 402, 260), ("/founding-athletes/", 88, 61),
                  ("/vs/chatgpt/", 54, 48), ("/guides/marathon-training-app/", 41, 36),
                  ("/vs/runna/", 33, 29), ("/compare/", 21, 17),
                  ("/vs/strava/", 18, 16), ("/guides/what-is-an-ai-fitness-coach/", 12, 11)],
        "sources": [("direct", 301, 190), ("reddit", 104, 88),
                    ("www.google.com", 77, 66), ("chatgpt.com", 41, 39),
                    ("networking-qr", 22, 14), ("com.slack", 9, 8)],
        "signups": (23, 61),
        "cta": (11, 19),
    }


# ── rendering ─────────────────────────────────────────────────────────────

def fill_days(daily, days):
    by_day = {d: (v, u) for d, v, u in daily}
    today = dt.date.today()
    out = []
    for i in range(days):
        day = today - dt.timedelta(days=days - 1 - i)
        v, u = by_day.get(day.isoformat(), (0, 0))
        out.append((day, v, u))
    return out


def nice_max(value):
    if value <= 0:
        return 4
    for step in (4, 8, 12, 20, 40, 60, 100, 200, 400, 600, 1000,
                 2000, 4000, 10000, 20000, 50000, 100000):
        if value <= step:
            return step
    return value


def bar_chart_svg(series):
    """Daily pageviews as an SVG bar chart. Single series: no legend needed."""
    W, H = 960, 240
    pad_l, pad_r, pad_t, pad_b = 40, 8, 14, 26
    cw, ch = W - pad_l - pad_r, H - pad_t - pad_b
    n = len(series)
    top = nice_max(max((v for _, v, _ in series), default=0))
    gap = 2
    bw = max(3.0, cw / n - gap)
    step = cw / n

    parts = []
    # recessive grid: quarter lines + labels
    for frac in (0.25, 0.5, 0.75, 1.0):
        y = pad_t + ch * (1 - frac)
        parts.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{W-pad_r}" '
                     f'y2="{y:.1f}" stroke="#ECEAE4" stroke-width="1"/>')
        parts.append(f'<text x="{pad_l-8}" y="{y+3.5:.1f}" text-anchor="end" '
                     f'class="axis">{int(top*frac)}</text>')
    # baseline
    parts.append(f'<line x1="{pad_l}" y1="{pad_t+ch}" x2="{W-pad_r}" '
                 f'y2="{pad_t+ch}" stroke="#D9D6CE" stroke-width="1"/>')

    max_v = max((v for _, v, _ in series), default=0)
    max_labeled = False
    label_every = max(1, n // 7)
    for i, (day, v, _u) in enumerate(series):
        x = pad_l + i * step + (step - bw) / 2
        h = ch * (v / top) if top else 0
        y = pad_t + ch - h
        r = min(3, bw / 2, h)
        if h > 0:
            parts.append(
                f'<path class="bar" data-i="{i}" d="M{x:.1f},{pad_t+ch:.1f} '
                f'L{x:.1f},{y+r:.1f} Q{x:.1f},{y:.1f} {x+r:.1f},{y:.1f} '
                f'L{x+bw-r:.1f},{y:.1f} Q{x+bw:.1f},{y:.1f} {x+bw:.1f},{y+r:.1f} '
                f'L{x+bw:.1f},{pad_t+ch:.1f} Z"/>')
        # selective direct label: the max day only
        if v == max_v and v > 0 and not max_labeled:
            parts.append(f'<text x="{x+bw/2:.1f}" y="{y-5:.1f}" '
                         f'text-anchor="middle" class="peak">{v}</text>')
            max_labeled = True
        if i % label_every == 0:
            parts.append(f'<text x="{x+bw/2:.1f}" y="{H-8}" '
                         f'text-anchor="middle" class="axis">'
                         f'{day.strftime("%b %-d")}</text>')
        # full-height hover target (bigger than the mark)
        parts.append(f'<rect class="hit" data-i="{i}" x="{pad_l+i*step:.1f}" '
                     f'y="{pad_t}" width="{step:.1f}" height="{ch}" '
                     f'fill="transparent"/>')

    return (f'<svg viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Daily pageviews">{"".join(parts)}</svg>')


def table_html(title, headers, rows, bar_col=1):
    max_v = max((r[bar_col] for r in rows), default=0) or 1
    body = []
    for r in rows:
        cells = [f'<td class="name">{html.escape(str(r[0]))}</td>']
        for v in r[1:]:
            cells.append(f'<td class="num">{v:,}</td>')
        pct = 100 * r[bar_col] / max_v
        cells.append(f'<td class="barcell"><span class="rowbar" '
                     f'style="width:{pct:.0f}%"></span></td>')
        body.append("<tr>" + "".join(cells) + "</tr>")
    head = "".join(f"<th>{h}</th>" for h in headers) + "<th></th>"
    return (f'<section class="panel"><h2>{title}</h2>'
            f'<table><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></section>')


def render(data, days, ips, demo):
    series = fill_days(data["daily"], days)
    tooltip_data = json.dumps(
        [{"d": d.strftime("%a %b %-d"), "v": v, "u": u} for d, v, u in series])
    generated = dt.datetime.now().strftime("%B %-d, %Y at %-I:%M %p")
    ip_note = (f"{len(ips)} configured IP{'s' if len(ips) != 1 else ''} excluded"
               if ips else "no IP exclusions configured")
    demo_banner = ('<p class="demo">Demo data — run without --demo for live '
                   'numbers.</p>' if demo else '')

    tiles = f"""
    <div class="tiles">
      <div class="tile"><p class="tile-label">Pageviews · {days}d</p>
        <p class="tile-value">{data['views_total']:,}</p></div>
      <div class="tile"><p class="tile-label">Unique visitors · {days}d</p>
        <p class="tile-value">{data['visitors_total']:,}</p></div>
      <div class="tile"><p class="tile-label">Waitlist signups · {days}d</p>
        <p class="tile-value">{data['signups'][0]:,}</p>
        <p class="tile-sub">{data['signups'][1]:,} all-time</p></div>
      <div class="tile"><p class="tile-label">Founding-athlete CTA · {days}d</p>
        <p class="tile-value">{data['cta'][0]:,}</p>
        <p class="tile-sub">{data['cta'][1]:,} all-time</p></div>
    </div>"""

    pages_tbl = table_html(f"Top pages · last {days} days",
                           ["Page", "Views", "Visitors"], data["pages"])
    sources_tbl = table_html(f"Traffic sources · last {days} days",
                             ["Source", "Views", "Visitors"], data["sources"])

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Justus · site traffic</title>
<style>
  :root {{
    --bg: #faf9f7; --surface: #ffffff; --ink: #1a1a1a; --ink-2: #6b6b6b;
    --ink-3: #9c9c9c; --border: #e8e8e8; --green: #5c8a5c; --mark: {MARK};
    color-scheme: light;
  }}
  body {{ margin: 0; background: var(--bg); color: var(--ink);
    font: 16px/1.5 -apple-system, BlinkMacSystemFont, 'SF Pro Text',
    'Segoe UI', Roboto, sans-serif; -webkit-font-smoothing: antialiased; }}
  .shell {{ max-width: 1020px; margin: 0 auto; padding: 40px 28px 72px; }}
  header h1 {{ font-family: Georgia, serif; color: var(--green);
    font-size: 30px; margin: 0; letter-spacing: -0.4px; }}
  header h1 .dot {{ color: var(--ink); }}
  header .meta {{ color: var(--ink-3); font-size: 13px; margin: 6px 0 0; }}
  .demo {{ display: inline-block; background: #F5EFE2; border: 1px solid
    #E4D9BF; border-radius: 8px; padding: 4px 10px; font-size: 13px;
    color: #7A6A45; margin-top: 12px; }}
  .tiles {{ display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 12px; margin: 32px 0 12px; }}
  .tile {{ background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 16px 18px; }}
  .tile-label {{ margin: 0 0 4px; font-size: 11px; font-weight: 500;
    letter-spacing: 0.8px; text-transform: uppercase; color: var(--ink-2); }}
  .tile-value {{ margin: 0; font-size: 30px; font-weight: 650;
    letter-spacing: -0.5px; font-variant-numeric: tabular-nums; }}
  .tile-sub {{ margin: 2px 0 0; font-size: 12.5px; color: var(--ink-3); }}
  .panel {{ background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 20px 22px 18px; margin-top: 14px; }}
  .panel h2 {{ margin: 0 0 14px; font-size: 15px; font-weight: 600;
    letter-spacing: -0.1px; }}
  svg {{ display: block; width: 100%; height: auto; }}
  .bar {{ fill: var(--mark); }}
  .bar.hot {{ fill: {MARK_HOVER}; }}
  .axis {{ font: 11px -apple-system, sans-serif; fill: var(--ink-3); }}
  .peak {{ font: 600 11px -apple-system, sans-serif; fill: var(--ink-2); }}
  .grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  th {{ text-align: left; font-size: 11px; font-weight: 500; letter-spacing:
    0.6px; text-transform: uppercase; color: var(--ink-3); padding: 0 8px 8px 0;
    border-bottom: 1px solid var(--border); }}
  td {{ padding: 7px 8px 7px 0; border-bottom: 1px solid #F1EFEA;
    vertical-align: middle; }}
  tr:last-child td {{ border-bottom: 0; }}
  td.name {{ max-width: 240px; overflow: hidden; text-overflow: ellipsis;
    white-space: nowrap; color: var(--ink); }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums;
    color: var(--ink-2); width: 64px; }}
  td.barcell {{ width: 90px; padding-left: 10px; }}
  .rowbar {{ display: block; height: 6px; border-radius: 3px;
    background: var(--mark); min-width: 2px; }}
  #tip {{ position: fixed; pointer-events: none; background: var(--ink);
    color: #fff; font-size: 12.5px; line-height: 1.45; padding: 7px 10px;
    border-radius: 8px; opacity: 0; transition: opacity 100ms ease;
    z-index: 10; white-space: nowrap; }}
  footer {{ margin-top: 28px; color: var(--ink-3); font-size: 12.5px;
    line-height: 1.6; }}
  @media (max-width: 880px) {{
    .tiles {{ grid-template-columns: 1fr 1fr; }}
    .grid2 {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<div class="shell">
  <header>
    <h1>Justus<span class="dot">.</span> <span style="color:var(--ink);
      font-family:-apple-system,sans-serif;font-size:20px;font-weight:600;">
      site traffic</span></h1>
    <p class="meta">Generated {generated} · last {days} days ·
      host {LIVE_HOST} only · {ip_note}</p>
    {demo_banner}
  </header>

  {tiles}

  <section class="panel">
    <h2>Daily pageviews · last {days} days</h2>
    {bar_chart_svg(series)}
  </section>

  <div class="grid2">
    {pages_tbl}
    {sources_tbl}
  </div>

  <footer>
    Counts exclude non-{LIVE_HOST} hosts (localhost, previews), browsers
    opted out via <code>?internal=1</code>, and the configured IP list in
    <code>scripts/dashboard/config.local.json</code>. Waitlist signups are
    the <code>waitlist_submitted</code> events captured on form submit —
    directionally accurate; LaunchList remains the source of truth for the
    actual list. Founding-athlete applications arrive via Slack + Airtable
    and aren't counted here (only CTA clicks are).
  </footer>
</div>
<div id="tip"></div>
<script>
  var DATA = {tooltip_data};
  var tip = document.getElementById('tip');
  var bars = document.querySelectorAll('.bar');
  document.querySelectorAll('.hit').forEach(function (hit) {{
    hit.addEventListener('mousemove', function (e) {{
      var i = +hit.dataset.i, d = DATA[i];
      if (!d) return;
      tip.innerHTML = '<strong>' + d.d + '</strong><br>' + d.v +
        ' views · ' + d.u + ' visitors';
      var x = Math.min(e.clientX + 14, window.innerWidth - tip.offsetWidth - 8);
      tip.style.left = x + 'px';
      tip.style.top = (e.clientY - 10 - tip.offsetHeight) + 'px';
      tip.style.opacity = 1;
      bars.forEach(function (b) {{
        b.classList.toggle('hot', b.dataset.i === hit.dataset.i);
      }});
    }});
    hit.addEventListener('mouseleave', function () {{
      tip.style.opacity = 0;
      bars.forEach(function (b) {{ b.classList.remove('hot'); }});
    }});
  }});
</script>
</body>
</html>"""


# ── main ──────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--demo", action="store_true",
                    help="render with sample data (no API key needed)")
    ap.add_argument("--out", default=str(HERE / "out" / "site-dashboard.html"))
    args = ap.parse_args()

    ips = load_excluded_ips()
    if args.demo:
        data = demo_data(args.days)
    else:
        key = resolve_api_key()
        project_id = discover_project_id(key)
        data = fetch_data(key, project_id, args.days, ips)

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(data, args.days, ips, args.demo))
    print(out)


if __name__ == "__main__":
    main()
