from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def replace_all(path, replacements):
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    for old, new in replacements:
        if old not in text:
            raise RuntimeError(f"Expected pricing fragment not found in {path}: {old[:90]!r}")
        text = text.replace(old, new)
    target.write_text(text, encoding="utf-8")


replace_all(
    "guides/ai-vs-human-personal-trainer/index.html",
    [
        (
            "For most people: yes. The economics are very different from a human trainer — paid pricing a month vs paid pricing an hour — and the AI is available every day, holds your full history, and adapts the plan in real time.",
            "For most people: yes. The economics are very different from a human trainer: AI coaching is generally sold as a low recurring subscription, while human coaching is usually billed by the session. The AI is available every day, holds your full history, and adapts the plan in real time.",
        ),
        (
            "A human personal trainer typically costs paid pricing per session in the US, with most people seeing them 1-3 times a week. That's paid pricing,400 on a recurring plan. An AI personal trainer typically costs paid pricing a month, with no per-session pricing. The order of magnitude is different enough that the comparison isn't really apples-to-apples.",
            "Human personal training is usually billed per session and becomes a significant recurring expense when used weekly. AI personal training is generally sold as a much lower recurring subscription with no per-session fee. The cost structures are different enough that the comparison isn't really apples-to-apples.",
        ),
        (
            "<li><strong>A human personal trainer</strong> is best for in-person form correction, motivation, the relationship, and post-injury work. You see them 1&ndash;3 times a week and they cost paid pricing&ndash;paid pricing per session.</li>",
            "<li><strong>A human personal trainer</strong> is best for in-person form correction, motivation, the relationship, and post-injury work. You see them 1&ndash;3 times a week and pay for each session.</li>",
        ),
        (
            "<li><strong>An AI personal trainer</strong> is best for daily availability, cost, persistent memory, and real-time adaptation. You can talk to it any time, and it typically costs paid pricing&ndash;paid pricing a month.</li>",
            "<li><strong>An AI personal trainer</strong> is best for daily availability, cost, persistent memory, and real-time adaptation. You can talk to it any time through a low recurring subscription.</li>",
        ),
        (
            "<li><strong>The economics are different by an order of magnitude.</strong> A weekly PT is paid pricing&ndash;paid pricingnth. An AI coach is paid pricing&ndash;paid pricingnth.</li>",
            "<li><strong>The economics are fundamentally different.</strong> Weekly human coaching is a substantial recurring expense. AI coaching is usually priced like a software subscription.</li>",
        ),
        (
            "<li>You can afford paid pricing+/month for the relationship</li>",
            "<li>You can afford an ongoing in-person coaching relationship</li>",
        ),
        (
            "<tr><th scope=\"row\">Cost</th><td>paid pricing&ndash;paid pricing/session · paid pricing&ndash;paid pricing,400 monthly</td><td class=\"justus\">paid pricing&ndash;paid pricingnth, all-in</td></tr>",
            "<tr><th scope=\"row\">Cost</th><td>Premium per-session pricing</td><td class=\"justus\">Research preview access is about half the standard rate</td></tr>",
        ),
        (
            "<p>Third, <strong>cost</strong>. The order of magnitude isn't subtle. A PT is paid pricing&ndash;paid pricing,400/month. An AI coach is paid pricing&ndash;paid pricingnth. That's a different category.</p>",
            "<p>Third, <strong>cost</strong>. Human training is priced by the session and becomes a substantial recurring expense when used weekly. AI coaching is usually priced like a software subscription. That's a different category.</p>",
        ),
        (
            "For most people: yes. The economics are very different from a human trainer &mdash; paid pricing a month vs paid pricing an hour &mdash; and the AI is available every day, holds your full history, and adapts the plan in real time.",
            "For most people: yes. The economics are very different from a human trainer: AI coaching is generally sold as a low recurring subscription, while human coaching is usually billed by the session. The AI is available every day, holds your full history, and adapts the plan in real time.",
        ),
        (
            "<p>A human personal trainer typically costs paid pricing per session in the US, with most people seeing them 1&ndash;3 times a week. That's paid pricing,400 on a recurring plan.</p>\n              <p>An AI personal trainer typically costs paid pricing a month, with no per-session pricing. <em>The order of magnitude is different enough that the comparison isn't really apples-to-apples.</em></p>",
            "<p>Human personal training is usually billed per session and becomes a significant recurring expense when used weekly.</p>\n              <p>AI personal training is generally sold as a much lower recurring subscription with no per-session fee. <em>The cost structures are different enough that the comparison isn't really apples-to-apples.</em></p>",
        ),
    ],
)

replace_all(
    "vs/fitbod/index.html",
    [
        (
            "Fitbod is about paid pricingnth or paid pricing/year. Justus pricing isn't final, but the research preview is intentionally low-cost for early users.",
            "Fitbod offers paid monthly and annual plans. Justus pricing isn't final, but research preview access is about half the standard rate.",
        ),
    ],
)

replace_all(
    "guides/best-strength-training-app/index.html",
    [
        ("Around paid pricingnth.", "Paid monthly and annual plans."),
        ("AI tier is free; premium human coaching runs into the hundreds on a recurring plan.", "AI tier is free; premium human coaching uses high-touch coaching pricing."),
        ("Free tier; ~paid pricingnth Pro.", "Free tier; paid Pro plan."),
        ("Free tier; ~paid pricing&ndash;paid pricingnth Pro.", "Free tier; paid Pro plan."),
    ],
)

changed = [
    "index.html",
    "vs/chatgpt/index.html",
    "vs/claude/index.html",
    "vs/gemini/index.html",
    "vs/fitbod/index.html",
    "vs/caliber/index.html",
    "guides/best-strength-training-app/index.html",
    "guides/what-is-an-ai-fitness-coach/index.html",
    "guides/ai-vs-human-personal-trainer/index.html",
    "guides/marathon-training-app/index.html",
    "founding-athletes/index.html",
    "sitemap.xml",
    "llms.txt",
]

for path in changed:
    text = (ROOT / path).read_text(encoding="utf-8")
    for pattern in [r"paid pricing", r"pricingnth", r"\$\d", r"\$8", r"\$15", r"/mo\b", r"per month"]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raise RuntimeError(f"Pricing cleanup failed in {path}: {match.group(0)!r}")

print("JUS-144 pricing copy cleaned and validated")
