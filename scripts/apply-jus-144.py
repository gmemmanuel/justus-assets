from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-07-07"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def insert_before_once(text: str, marker: str, insertion: str, path: str) -> str:
    if insertion.strip() in text:
        return text
    count = text.count(marker)
    if count != 1:
        raise RuntimeError(f"Expected exactly one marker in {path}: {marker!r}; found {count}")
    return text.replace(marker, insertion + marker, 1)


def sanitize_pricing(text: str) -> str:
    # The research-preview site intentionally avoids publishing exact prices.
    text = re.sub(
        r'<tr><th scope="row">(?:Price|Pricing)</th>.*?</tr>',
        '<tr><th scope="row">Pricing</th><td>Free and paid options vary</td><td class="justus">Research preview access is about half the standard rate</td></tr>',
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'\$\d+(?:\.\d+)?(?:\s*(?:–|-|to)\s*\$?\d+(?:\.\d+)?)?(?:\s*/\s*(?:mo|month))?',
        'paid pricing',
        text,
    )
    text = re.sub(r'\bper month\b', 'on a recurring plan', text, flags=re.IGNORECASE)
    text = re.sub(r'/mo\b', ' monthly', text, flags=re.IGNORECASE)
    return text


HOME_CSS = """

      /* ─── Event-athlete callout ─── */
      .event-athlete {
        max-width: 820px;
        margin: 0 auto 120px;
        padding: 56px 60px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 28px;
        text-align: left;
      }
      .event-athlete .event-kicker {
        margin: 0 0 14px;
        color: var(--success);
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1.2px;
        text-transform: uppercase;
      }
      .event-athlete h2 {
        margin: 0 0 18px;
        font-size: clamp(32px, 5vw, 48px);
        line-height: 1.08;
        letter-spacing: -1.2px;
      }
      .event-athlete h2 em {
        color: var(--success);
        font-family: var(--font-logo);
        font-weight: var(--fw-semibold);
      }
      .event-athlete > p {
        max-width: 680px;
        margin: 0 0 30px;
        color: var(--fg-2);
        font-size: 18px;
        line-height: 1.65;
      }
      .event-athlete-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin: 0 0 32px;
      }
      .event-athlete-card {
        padding: 20px;
        background: var(--surface-accent);
        border-radius: 16px;
      }
      .event-athlete-card strong {
        display: block;
        margin-bottom: 7px;
        font-size: 15px;
      }
      .event-athlete-card span {
        color: var(--fg-2);
        font-size: 14px;
        line-height: 1.5;
      }
      .event-athlete-link {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: var(--fg-1);
        font-weight: 600;
        text-decoration: none;
        border-bottom: 1px solid var(--success);
        padding-bottom: 3px;
      }
      .event-athlete-link:hover { color: var(--success); }
      @media (max-width: 720px) {
        .event-athlete {
          margin-bottom: 88px;
          padding: 38px 26px;
          border-radius: 22px;
        }
        .event-athlete-grid { grid-template-columns: 1fr; }
      }
"""

HOME_SECTION = """
      <!-- ────────── Training for something ────────── -->
      <section class="event-athlete" id="training-for-something">
        <p class="event-kicker">Training for something?</p>
        <h2>Your race has a date. Your plan should know <em>what happened this week</em>.</h2>
        <p>
          A fall marathon, a first half, a triathlon, a distance swim: the plan is only useful
          while it still fits your real life. Justus keeps the block private, reads the training
          data already on your watch, and reshapes the weeks ahead when travel, illness, soreness,
          or one missed long session changes the math.
        </p>
        <div class="event-athlete-grid">
          <div class="event-athlete-card"><strong>The date stays visible</strong><span>Your goal event anchors the block, even when individual weeks move.</span></div>
          <div class="event-athlete-card"><strong>Your watch is part of the conversation</strong><span>The coach can respond to what you actually did, not only what the plan prescribed.</span></div>
          <div class="event-athlete-card"><strong>Strength fits around the sport</strong><span>Running, lifting, swimming, mobility, and recovery are coordinated instead of competing.</span></div>
        </div>
        <a class="event-athlete-link" href="/founding-athletes/">Apply for the fall-race founding cohort <span aria-hidden="true">→</span></a>
      </section>

"""

CHATBOT_SECTIONS = {
    "vs/chatgpt/index.html": ("ChatGPT", "ChatGPT"),
    "vs/claude/index.html": ("Claude", "Claude"),
    "vs/gemini/index.html": ("Gemini", "Gemini"),
}

LIGHT_SECTIONS = {
    "vs/fitbod/index.html": """
      <section class="dive">
        <h3>The hybrid-athlete question: <span class="italic">where does strength fit in the race block?</span></h3>
        <p>Fitbod is useful when the lifting session is the main event. The harder problem for a runner, cyclist, swimmer, or triathlete is deciding how much strength belongs beside intervals, long sessions, and recovery. Justus treats lifting as part of the same event plan, so a hard lower-body day does not accidentally compete with the workout that matters most that week.</p>
      </section>

""",
    "vs/caliber/index.html": """
      <section class="dive">
        <h3>For athletes who lift <span class="italic">inside an endurance block</span></h3>
        <p>Caliber's strength focus can be a good fit when strength is the primary goal. An athlete preparing for a marathon, triathlon, ride, or distance swim needs a different kind of coordination: strength has to support the event, move around key sessions, and scale down when fatigue rises. Justus keeps those decisions inside one plan rather than asking you to reconcile separate coaching systems.</p>
      </section>

""",
    "guides/best-strength-training-app/index.html": """
      <section class="dive">
        <h3>Training for a race? Judge the strength app by <span class="italic">what it protects</span>.</h3>
        <p>For a hybrid athlete, the best strength plan is not the one that maximizes gym volume in isolation. It is the one that preserves the long run, quality ride, swim progression, or event-specific session while still building useful strength. That is why a coordinated coach can be a better fit than a standalone lifting generator during a race block.</p>
      </section>

""",
    "guides/what-is-an-ai-fitness-coach/index.html": """
      <section class="dive">
        <h3>A concrete test: <span class="italic">can it coach an event block?</span></h3>
        <p>Ask what happens in week six of a marathon, half-marathon, triathlon, or distance-swim plan after you miss the long session and your watch shows a harder-than-expected week. A real AI coach should remember the event date, understand what was completed, protect the purpose of the block, and adjust the next weeks without rebuilding the relationship from scratch.</p>
      </section>

""",
    "guides/ai-vs-human-personal-trainer/index.html": """
      <section class="dive">
        <h3>Event training makes the tradeoff <span class="italic">especially clear</span>.</h3>
        <p>A strong human coach brings judgment, reassurance, and the ability to see nuance that data misses. A purpose-built AI coach can be available every day, read the watch data continuously, and revise the plan as soon as a week goes sideways. For an amateur athlete with a real race date, the best choice depends on whether you need high-touch human interpretation or affordable, persistent adaptation between every session.</p>
      </section>

""",
}


def edit_existing_pages() -> None:
    home_path = "index.html"
    home = read(home_path)
    home = insert_before_once(home, "    </style>", HOME_CSS, home_path)
    home = insert_before_once(home, "      <!-- ────────── Why Justus ────────── -->", HOME_SECTION, home_path)
    write(home_path, sanitize_pricing(home))

    for path, (product, label) in CHATBOT_SECTIONS.items():
        text = read(path)
        section = f"""
      <section class="dive">
        <h3>The week-six problem in a real <span class="italic">marathon block</span></h3>
        <p>You asked {product} to build a marathon plan. By week six, it does not reliably know which long run you completed, what your watch recorded, or how the missed Tuesday session changes the next three weeks. You paste the history again, and the plan is effectively rebuilt from the latest conversation.</p>
        <p>That is the gap between a smart chatbot and a coach that holds the block. Justus keeps the race date, the plan, your completed training, and your strength work in one persistent system, then adapts the weeks ahead without asking you to become the record keeper.</p>
      </section>

"""
        text = insert_before_once(text, "      <section class=\"faq-section\"", section, path)
        write(path, sanitize_pricing(text))

    for path, section in LIGHT_SECTIONS.items():
        text = read(path)
        text = insert_before_once(text, "      <section class=\"faq-section\"", section, path)
        write(path, sanitize_pricing(text))


MARATHON_PAGE = r'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Best marathon training app in 2026: an honest guide — Justus</title>
    <meta name="description" content="Compare the best marathon training apps in 2026, including Runna, Garmin Coach, TrainingPeaks, Nike Run Club, ChatGPT, and Justus. Find the right app for a plan that adapts when training changes." />
    <link rel="canonical" href="https://justus.health/guides/marathon-training-app/" />
    <meta property="og:title" content="Best marathon training app in 2026: an honest guide" />
    <meta property="og:description" content="An honest comparison of marathon training apps, from fixed plans to coaching that adapts when the block goes sideways." />
    <meta property="og:url" content="https://justus.health/guides/marathon-training-app/" />
    <meta property="og:type" content="article" />
    <meta property="og:image" content="https://justus.health/splash-icon.png" />
    <meta name="twitter:card" content="summary_large_image" />
    <link rel="icon" type="image/svg+xml" href="/bimi-logo.svg" />
    <link rel="apple-touch-icon" href="/splash-icon.png" />
    <link rel="stylesheet" href="/aiso.css" />
    <script src="https://getlaunchlist.com/js/widget-diy.js" defer></script>
    <script>window.PAGE_SLUG = 'marathon-training-app';</script>
    <script src="/aiso-init.js"></script>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
        {"@type":"Question","name":"What is the best app to train for a marathon?","acceptedAnswer":{"@type":"Answer","text":"The best app depends on the job. Nike Run Club is strong for a free guided plan, Garmin Coach is convenient for Garmin users, Runna offers polished running-first programming, TrainingPeaks gives experienced athletes control, and a purpose-built coach such as Justus is designed to adapt the full block around completed workouts, watch data, missed weeks, and strength training."}},
        {"@type":"Question","name":"Can a marathon training app adjust when I miss a week?","acceptedAnswer":{"@type":"Answer","text":"Some can, but the depth varies. A fixed plan may simply move or skip sessions. A coaching system should consider the race date, recent training load, the purpose of the missed sessions, and the time remaining before deciding what to preserve and what to let go."}},
        {"@type":"Question","name":"Is ChatGPT good for marathon training?","acceptedAnswer":{"@type":"Answer","text":"ChatGPT can draft a sensible starting plan and explain training concepts. It becomes cumbersome for ongoing coaching because you must maintain the history, paste in workout data, and remind it what changed. It is best for a self-directed athlete who is comfortable being the plan manager."}},
        {"@type":"Question","name":"Should marathon runners strength train?","acceptedAnswer":{"@type":"Answer","text":"Many runners benefit from strength work, but it has to fit around the running that drives marathon preparation. The useful question is not whether strength belongs in the plan, but how much belongs in each phase and where it sits relative to long runs and quality sessions."}},
        {"@type":"Question","name":"What makes Justus different from a standard marathon plan app?","acceptedAnswer":{"@type":"Answer","text":"Justus is conversation-driven and multimodal. It keeps the event date, training plan, completed workouts, wearable data, strength work, and recovery context together so the block can change without starting over."}}
      ]
    }
    </script>
  </head>
  <body>
    <nav class="nav" id="site-nav">
      <div class="nav-inner">
        <a href="/" class="mark">Justus</a>
        <span class="stamp">Research preview · 2026</span>
        <div class="nav-links">
          <a href="/#why">Why Justus</a>
          <a href="#faq">FAQ</a>
          <a href="/#get-early-access">Waitlist</a>
        </div>
      </div>
    </nav>

    <main class="shell">
      <section class="hero">
        <p class="eyebrow">Guide · Marathon training apps</p>
        <h1>The best marathon training app is the one that still works when <span class="italic">the block goes sideways</span>.</h1>
        <p class="lede">A marathon plan can look excellent on day one and be wrong by week six. This guide compares the main options honestly: fixed plans, running-first subscriptions, athlete dashboards, free guided programs, chatbot self-coaching, and a coach built to keep adapting.</p>
      </section>

      <section class="answer" aria-label="Quick answer">
        <p class="label">Quick answer</p>
        <ul>
          <li><strong>Best free guided option:</strong> Nike Run Club, especially for runners who want audio guidance and a straightforward plan.</li>
          <li><strong>Best for Garmin-native convenience:</strong> Garmin Coach, when your watch ecosystem matters more than deep customization.</li>
          <li><strong>Best polished running-first experience:</strong> Runna, for athletes who want a structured plan and are mostly focused on running.</li>
          <li><strong>Best for experienced athletes who want control:</strong> TrainingPeaks, particularly when you already understand training structure or work with a human coach.</li>
          <li><strong>Best for self-directed experimentation:</strong> ChatGPT or Claude, if you are willing to maintain the context and manage the plan yourself.</li>
          <li><strong>Best for conversation-driven adaptation across running and strength:</strong> Justus, for athletes who want the coach to hold the block, read the watch data, and adjust around real life.</li>
        </ul>
      </section>

      <section class="section">
        <h2>Who this guide is <span class="italic">actually for</span>.</h2>
        <p>You have a race date, a watch, and enough experience to know that a calendar full of workouts is not the same thing as coaching.</p>
        <div class="who-grid">
          <div class="who-card">
            <h3>A standard plan may be enough if</h3>
            <p class="who-sub">You want structure, not a relationship</p>
            <ul>
              <li>Your schedule is predictable and you rarely miss training</li>
              <li>Running is your only meaningful training priority</li>
              <li>You are comfortable deciding how to adjust the plan yourself</li>
              <li>You mainly need workouts placed on a calendar</li>
            </ul>
          </div>
          <div class="who-card justus">
            <h3>A persistent coach may fit if</h3>
            <p class="who-sub">You want the plan to survive real life</p>
            <ul>
              <li>You need the race date to remain the anchor after a disrupted week</li>
              <li>You want completed workouts and watch data to shape what comes next</li>
              <li>You lift, swim, ride, or play a sport alongside running</li>
              <li>You want to explain what happened once, in a conversation, and move on</li>
            </ul>
          </div>
        </div>
      </section>

      <section class="section">
        <h2>Marathon training apps, <span class="italic">compared by the job they do</span>.</h2>
        <p>No single app wins every category. The important question is what you expect the app to own.</p>
        <div class="compare">
          <table>
            <thead><tr><th>Option</th><th>Best at</th><th>Tradeoff</th></tr></thead>
            <tbody>
              <tr><th scope="row">Nike Run Club</th><td>Accessible guided plans and audio runs</td><td>Limited personalization once the plan is underway</td></tr>
              <tr><th scope="row">Garmin Coach</th><td>Watch-native scheduling and simple adaptation</td><td>Lives inside one ecosystem and offers limited conversational context</td></tr>
              <tr><th scope="row">Runna</th><td>Polished running-first programming</td><td>Can feel rigid when life or cross-training changes the block</td></tr>
              <tr><th scope="row">TrainingPeaks</th><td>Detailed planning, metrics, and coach collaboration</td><td>Powerful but management-heavy; the athlete or coach still interprets the data</td></tr>
              <tr><th scope="row">ChatGPT or Claude</th><td>Drafting plans and answering one-off questions</td><td>You maintain the history, move the workouts, and re-supply the context</td></tr>
              <tr><th scope="row">Justus</th><td>Persistent, conversational adaptation across running, strength, and recovery</td><td>Still in research preview and opening to athletes in small cohorts</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="dive">
        <h3>Runna: <span class="italic">polished and running-first</span></h3>
        <p>Runna is a strong choice for a runner who wants a modern interface, clear sessions, and a program that feels more supported than a downloaded PDF. Its focus is also its limitation: athletes who combine serious strength work, another sport, or frequent schedule changes may find themselves negotiating with the plan rather than being coached through the whole picture.</p>
      </section>

      <section class="dive">
        <h3>Garmin Coach: <span class="italic">convenient inside the watch ecosystem</span></h3>
        <p>Garmin Coach reduces friction. Workouts appear where you already train, and the watch captures the result. It is a practical option for runners who want a recognizable plan without adding another complex system. The adaptation is narrower than a coach who can discuss travel, soreness, strength work, confidence, or the reason a session went badly.</p>
      </section>

      <section class="dive">
        <h3>TrainingPeaks: <span class="italic">control for people who know what to do with it</span></h3>
        <p>TrainingPeaks is excellent infrastructure for serious planning. It exposes the calendar, metrics, workout detail, and coach-athlete workflow. It does not remove the need for interpretation. That is a strength for experienced athletes and human coaches, and a burden for someone who wants the system to make and explain the adjustment.</p>
      </section>

      <section class="dive">
        <h3>Nike Run Club: <span class="italic">a generous place to start</span></h3>
        <p>Nike Run Club remains a sensible starting point for a first marathon, especially when cost and guided audio matter. The tradeoff is continuity: the plan does not build a deep model of your history or coordinate the rest of your training life. It guides the run well; it is not trying to become a longitudinal coach.</p>
      </section>

      <section class="dive">
        <h3>ChatGPT or Claude: <span class="italic">smart advice, manual plumbing</span></h3>
        <p>A general chatbot can create a credible 16-week plan in minutes. By week six, you are usually pasting in completed mileage, explaining the missed long run, reminding it about your race date, and asking for a revised table. The model can reason about the problem, but you are the one maintaining the training record and keeping each conversation attached to reality.</p>
      </section>

      <section class="dive">
        <h3>The Justus angle: <span class="italic">the conversation holds the block</span></h3>
        <p>Justus is designed around the part that begins after the plan is written. The event date stays in the system. Completed workouts and wearable data stay attached to the athlete. You can say, “I missed last week, my calf is tight, and I can run Tuesday, Thursday, and Sunday,” and the coach can reshape the block without treating you like a new prompt.</p>
        <p>It also coordinates strength alongside the running plan. That matters because the right lifting dose in a base phase is not necessarily the right dose in a peak week, and the hardest lower-body session should not land by accident beside the most important run.</p>
      </section>

      <section class="faq-section" id="faq">
        <h2>Common questions <span class="italic">about marathon training apps</span>.</h2>
        <div class="faq-list">
          <details class="faq-item" open>
            <summary class="faq-q"><span>What is the best app to train for a marathon?</span><span class="faq-icon" aria-hidden="true"></span></summary>
            <div class="faq-a-wrap"><div class="faq-a-inner"><div class="faq-a"><p>The best app depends on the job. Nike Run Club is strong for a free guided plan, Garmin Coach is convenient for Garmin users, Runna offers polished running-first programming, TrainingPeaks gives experienced athletes control, and Justus is designed for persistent adaptation across running and strength.</p></div></div></div>
          </details>
          <details class="faq-item">
            <summary class="faq-q"><span>Can a marathon training app adjust when I miss a week?</span><span class="faq-icon" aria-hidden="true"></span></summary>
            <div class="faq-a-wrap"><div class="faq-a-inner"><div class="faq-a"><p>Some can, but the depth varies. A useful adjustment considers the race date, recent load, the purpose of the missed sessions, and how much time remains. Simply pushing every workout back a week can create a worse plan.</p></div></div></div>
          </details>
          <details class="faq-item">
            <summary class="faq-q"><span>Is ChatGPT good for marathon training?</span><span class="faq-icon" aria-hidden="true"></span></summary>
            <div class="faq-a-wrap"><div class="faq-a-inner"><div class="faq-a"><p>It is good at drafting a plan and answering questions. It is less convenient as an ongoing coach because you maintain the history, paste in data, and manage the plan between conversations.</p></div></div></div>
          </details>
          <details class="faq-item">
            <summary class="faq-q"><span>Should marathon runners strength train?</span><span class="faq-icon" aria-hidden="true"></span></summary>
            <div class="faq-a-wrap"><div class="faq-a-inner"><div class="faq-a"><p>Strength can be useful, but it should support the running block. The volume and placement should change across phases so it does not undermine long runs, quality sessions, or recovery.</p></div></div></div>
          </details>
          <details class="faq-item">
            <summary class="faq-q"><span>What makes Justus different from a standard marathon plan app?</span><span class="faq-icon" aria-hidden="true"></span></summary>
            <div class="faq-a-wrap"><div class="faq-a-inner"><div class="faq-a"><p>Justus keeps the event date, plan, completed workouts, watch data, strength work, and ongoing conversation together. The goal is not only to generate the plan, but to keep coaching it when the athlete's real life changes.</p></div></div></div>
          </details>
        </div>
      </section>

      <section class="closer">
        <div class="word-small">Justus<span class="dot">.</span></div>
        <div class="tag">Your private AI fitness coach.</div>
        <form class="form launchlist-form waitlist-form" action="https://getlaunchlist.com/s/VfMDfO" method="post" data-form-location="marathon-guide-closer" novalidate>
          <input type="email" name="email" placeholder="your@email.com" required autocomplete="email" aria-label="Email address" />
          <input type="hidden" name="utm_source" /><input type="hidden" name="utm_medium" /><input type="hidden" name="utm_campaign" /><input type="hidden" name="utm_content" /><input type="hidden" name="utm_term" /><input type="hidden" name="referrer" />
          <button type="submit">Join the waitlist</button>
        </form>
        <p class="form-error" data-form-error></p>
      </section>

      <footer class="site-footer"><span><a href="/">Home</a><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a><a href="mailto:hello@justus.health">hello@justus.health</a></span></footer>
    </main>
    <script src="/aiso.js"></script>
  </body>
</html>
'''

FOUNDING_PAGE = r'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Founding Athletes: train your fall event with Justus</title>
    <meta name="description" content="Apply to the Justus Founding Athletes cohort for fall 2026. Selected athletes receive free research-preview access through their training block and help shape a private AI fitness coach." />
    <link rel="canonical" href="https://justus.health/founding-athletes/" />
    <meta property="og:title" content="Founding Athletes: train your fall event with Justus" />
    <meta property="og:description" content="A small founding cohort for athletes training toward a real event. Free research-preview access, direct founder contact, and a voice in how the coach develops." />
    <meta property="og:url" content="https://justus.health/founding-athletes/" />
    <meta property="og:type" content="website" />
    <meta property="og:image" content="https://justus.health/splash-icon.png" />
    <meta name="twitter:card" content="summary_large_image" />
    <link rel="icon" type="image/svg+xml" href="/bimi-logo.svg" />
    <link rel="apple-touch-icon" href="/splash-icon.png" />
    <link rel="stylesheet" href="/aiso.css" />
    <script>window.PAGE_SLUG = 'founding-athletes';</script>
    <script src="/aiso-init.js"></script>
    <style>
      .cohort-note { max-width: 720px; margin: 28px auto 0; text-align: center; color: var(--fg-2); }
      .application-actions { display: flex; justify-content: center; margin-top: 30px; }
      .application-button { display: inline-flex; align-items: center; justify-content: center; min-height: 50px; padding: 0 24px; border-radius: 999px; background: var(--fg-1); color: white; font-weight: 600; text-decoration: none; }
      .application-button:hover { opacity: .86; }
      .embed-placeholder { margin: 30px 0 0; padding: 42px 28px; border: 1px dashed var(--fg-3); border-radius: 18px; background: var(--surface-accent); text-align: center; }
      .embed-placeholder strong { display: block; margin-bottom: 8px; font-size: 18px; }
      .embed-placeholder p { margin: 0 auto; max-width: 560px; color: var(--fg-2); }
      .ask-list { margin-top: 24px; }
    </style>
  </head>
  <body>
    <nav class="nav" id="site-nav">
      <div class="nav-inner">
        <a href="/" class="mark">Justus</a>
        <span class="stamp">Founding cohort · Fall 2026</span>
        <div class="nav-links"><a href="/#why">Why Justus</a><a href="#application">Apply</a><a href="/guides/marathon-training-app/">Marathon guide</a></div>
      </div>
    </nav>

    <main class="shell">
      <section class="hero">
        <p class="eyebrow">Founding Athletes · Fall 2026</p>
        <h1>Train for something real. Help shape the coach that <span class="italic">gets you there</span>.</h1>
        <p class="lede">Justus is inviting a small cohort of amateur athletes with a real event on the calendar: fall marathons and half-marathons, triathlons, distance swims, rides, and other meaningful finish lines.</p>
        <div class="application-actions"><a class="application-button" href="#application" data-application-cta="hero">Apply for the founding cohort</a></div>
        <p class="cohort-note">This is not a mass beta program. We are selecting athletes whose training can teach us where a private, adaptive coach is most useful.</p>
      </section>

      <section class="answer" aria-label="What founding athletes receive">
        <p class="label">What founding athletes receive</p>
        <ul>
          <li><strong>Free access through your training block.</strong> Use the Justus research preview from onboarding through your event.</li>
          <li><strong>A direct line to the founder.</strong> You will talk with Gideon about what is working, what is confusing, and what the coach should do differently.</li>
          <li><strong>A plan that can move.</strong> The goal is to test coaching that remembers the event, reads your training data, and adapts when a week does not go to plan.</li>
          <li><strong>Real influence on the product.</strong> Your feedback will shape the coaching experience before the broader public launch.</li>
          <li><strong>Private by design.</strong> No feed, followers, leaderboards, or public training profile.</li>
        </ul>
      </section>

      <section class="section">
        <h2>Who we are looking for <span class="italic">right now</span>.</h2>
        <p>The strongest fit is an amateur athlete who owns a watch, has a meaningful event date, and has already felt the limits of either a rigid plan or a chatbot that forgets the training context.</p>
        <div class="who-grid">
          <div class="who-card">
            <h3>You may be a strong fit if</h3>
            <p class="who-sub">The finish line matters, but life is not perfectly predictable</p>
            <ul>
              <li>You are training for an event in the coming months</li>
              <li>You use Apple Watch, Garmin, COROS, Suunto, Polar, Fitbit, or another training device</li>
              <li>You have tried an app such as Runna or built plans with ChatGPT, Claude, or Gemini</li>
              <li>You combine running, strength, swimming, cycling, mobility, or another sport</li>
              <li>You can give candid feedback during the block</li>
            </ul>
          </div>
          <div class="who-card justus">
            <h3>This is probably not the right cohort if</h3>
            <p class="who-sub">You only want a finished app with no research contact</p>
            <ul>
              <li>You do not have a current training goal or event date</li>
              <li>You need medical diagnosis, injury treatment, or emergency guidance</li>
              <li>You want a social network, public competition, or follower features</li>
              <li>You do not want to discuss your experience with the founder</li>
            </ul>
          </div>
        </div>
      </section>

      <section class="dive">
        <h3>Why call this a <span class="italic">founding cohort</span>?</h3>
        <p>Because the work is more consequential than testing whether buttons function. Founding athletes help define what good coaching feels like when a plan meets missed weeks, travel, family demands, fatigue, strength work, and uncertainty before a race. We are looking for a small number of people who want to train well and leave the product better than they found it.</p>
      </section>

      <section class="section" id="application">
        <h2>Apply to become a <span class="italic">Founding Athlete</span>.</h2>
        <p>Applications are intentionally short. We want enough context to understand your event and how you train today.</p>
        <div class="ask-list answer">
          <p class="label">What we ask</p>
          <ul>
            <li>Your race or event and its date</li>
            <li>Your watch or training device</li>
            <li>What you currently use to plan your training</li>
            <li>A short answer to: “Tell us about your training.”</li>
          </ul>
        </div>

        <!-- TODO(JUS-144): Replace this placeholder with the Airtable shared-form iframe once Gideon creates the form. Preserve the surrounding #application section and data tracking attributes. -->
        <div class="embed-placeholder" data-airtable-embed-placeholder>
          <strong>Airtable application form goes here</strong>
          <p>Paste the Airtable shared-form embed code in this block. The location, mobile spacing, and analytics hooks are ready.</p>
        </div>
      </section>

      <section class="closer">
        <div class="word-small">Justus<span class="dot">.</span></div>
        <div class="tag">A private coach for the block you are actually living.</div>
        <a class="application-button" href="#application" data-application-cta="closer">Go to the application</a>
      </section>

      <footer class="site-footer"><span><a href="/">Home</a><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a><a href="mailto:hello@justus.health">hello@justus.health</a></span></footer>
    </main>

    <script src="/aiso.js"></script>
    <script>
      (function () {
        function captureApplicationClick(location) {
          try {
            if (!window.posthog) return;
            var params = new URLSearchParams(window.location.search);
            window.posthog.capture('founding_athlete_application_clicked', {
              page_type: 'aiso',
              page_slug: 'founding-athletes',
              cta_location: location || 'unknown',
              utm_source: params.get('utm_source') || null,
              utm_medium: params.get('utm_medium') || null,
              utm_campaign: params.get('utm_campaign') || null,
              utm_content: params.get('utm_content') || null,
              utm_term: params.get('utm_term') || null,
              referrer: document.referrer || null
            });
          } catch (e) {}
        }
        document.querySelectorAll('[data-application-cta]').forEach(function (cta) {
          cta.addEventListener('click', function () { captureApplicationClick(cta.dataset.applicationCta); });
        });
      })();
    </script>
  </body>
</html>
'''


def create_new_pages() -> None:
    write("guides/marathon-training-app/index.html", sanitize_pricing(MARATHON_PAGE))
    write("founding-athletes/index.html", sanitize_pricing(FOUNDING_PAGE))


def update_discovery_files() -> None:
    sitemap_path = "sitemap.xml"
    sitemap = read(sitemap_path)
    additions = f'''  <url>\n    <loc>https://justus.health/guides/marathon-training-app/</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.9</priority>\n  </url>\n  <url>\n    <loc>https://justus.health/founding-athletes/</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n'''
    sitemap = insert_before_once(sitemap, "</urlset>", additions, sitemap_path)
    write(sitemap_path, sitemap)

    llms_path = "llms.txt"
    llms = read(llms_path)
    llms = insert_before_once(
        llms,
        "- [Privacy](https://justus.health/privacy/): Privacy policy.",
        "- [Founding Athletes](https://justus.health/founding-athletes/): Application page for the fall-event founding cohort.\n",
        llms_path,
    )
    llms = insert_before_once(
        llms,
        "## Technical context for AI agents",
        "- [Best marathon training app in 2026](https://justus.health/guides/marathon-training-app/): Honest comparison of Runna, Garmin Coach, TrainingPeaks, Nike Run Club, chatbot self-coaching, and Justus.\n\n",
        llms_path,
    )
    write(llms_path, llms)


def validate() -> None:
    changed = [
        "index.html",
        *CHATBOT_SECTIONS.keys(),
        *LIGHT_SECTIONS.keys(),
        "guides/marathon-training-app/index.html",
        "founding-athletes/index.html",
        "sitemap.xml",
        "llms.txt",
    ]
    forbidden = re.compile(r'\$8|\$15|\$\d|per month|/mo', re.IGNORECASE)
    for path in changed:
        text = read(path)
        match = forbidden.search(text)
        if match:
            raise RuntimeError(f"Pricing leak in {path}: {match.group(0)!r}")

    required = {
        "index.html": ["/founding-athletes/", "Training for something?"],
        "guides/marathon-training-app/index.html": ["Runna", "Garmin Coach", "TrainingPeaks", "Nike Run Club", "ChatGPT", "<details class=\"faq-item\""],
        "founding-athletes/index.html": ["TODO(JUS-144)", "data-airtable-embed-placeholder", "founding_athlete_application_clicked", "page_slug: 'founding-athletes'"],
        "sitemap.xml": ["/guides/marathon-training-app/", "/founding-athletes/"],
        "llms.txt": ["/guides/marathon-training-app/", "/founding-athletes/"],
    }
    for path, needles in required.items():
        text = read(path)
        for needle in needles:
            if needle not in text:
                raise RuntimeError(f"Missing {needle!r} in {path}")

    beta = ROOT / "beta/index.html"
    if not beta.exists():
        raise RuntimeError("beta/index.html is missing")

    # Verify local root-relative links used by the two new pages.
    for path in ["guides/marathon-training-app/index.html", "founding-athletes/index.html"]:
        text = read(path)
        for href in re.findall(r'href="(/[^"]*)"', text):
            clean = href.split('#', 1)[0]
            if not clean or clean == "/":
                continue
            candidate = ROOT / clean.lstrip("/")
            if clean.endswith("/"):
                candidate = candidate / "index.html"
            if not candidate.exists():
                raise RuntimeError(f"Broken internal link in {path}: {href}")


if __name__ == "__main__":
    edit_existing_pages()
    create_new_pages()
    update_discovery_files()
    validate()
    print("JUS-144 edits applied and validated")
