/* ─── Shared behavior for AISO pages. Loaded at end of body. ─── */

(function () {
  // ─── UTM passthrough: copy URL params into hidden form fields ───
  var params = new URLSearchParams(window.location.search);
  var keys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  document.querySelectorAll('form.waitlist-form').forEach(function (form) {
    keys.forEach(function (key) {
      var input = form.querySelector('input[name="' + key + '"]');
      if (input) input.value = params.get(key) || '';
    });
    var ref = form.querySelector('input[name="referrer"]');
    if (ref) ref.value = document.referrer || '';
  });
})();

(function () {
  // ─── Form validation + PostHog conversion tracking ───
  document.querySelectorAll('form.waitlist-form').forEach(function (form) {
    var emailInput = form.querySelector('input[type="email"]');
    var errorEl = form.parentElement.querySelector('[data-form-error]');

    function clearError() {
      form.classList.remove('invalid');
      if (errorEl) errorEl.textContent = '';
    }
    function showError(msg) {
      form.classList.add('invalid');
      if (errorEl) errorEl.textContent = msg;
    }

    emailInput.addEventListener('input', clearError);

    form.addEventListener('submit', function (event) {
      var value = emailInput.value.trim();
      if (!value) {
        event.preventDefault();
        showError('Please enter your email so we can reach you.');
        emailInput.focus();
        return;
      }
      if (!emailInput.checkValidity()) {
        event.preventDefault();
        showError('That email doesn’t look right. Mind double-checking?');
        emailInput.focus();
        return;
      }
      clearError();

      try {
        if (window.posthog) {
          window.posthog.identify(value, { email: value });
          var params = new URLSearchParams(window.location.search);
          window.posthog.capture('waitlist_submitted', {
            form_location: form.dataset.formLocation || 'unknown',
            page_type: 'aiso',
            page_slug: window.PAGE_SLUG || 'unknown',
            utm_source: params.get('utm_source') || null,
            utm_medium: params.get('utm_medium') || null,
            utm_campaign: params.get('utm_campaign') || null,
            utm_content: params.get('utm_content') || null,
            utm_term: params.get('utm_term') || null,
          });
        }
      } catch (e) {
        // Never block submission on a tracking failure.
      }
    });
  });
})();

(function () {
  // ─── JUS-144: add event-athlete context to the requested AISO pages ───
  var sections = {
    '/vs/chatgpt/': '<section class="dive"><h3>The week-six problem in a real <span class="italic">marathon block</span></h3><p>You asked ChatGPT to build a marathon plan. By week six, it does not reliably know which long run you completed, what your watch recorded, or how the missed Tuesday session changes the next three weeks. You paste the history again, and the plan is effectively rebuilt from the latest conversation.</p><p>That is the gap between a smart chatbot and a coach that holds the block. Justus keeps the race date, the plan, your completed training, and your strength work in one persistent system, then adapts the weeks ahead without asking you to become the record keeper.</p></section>',
    '/vs/claude/': '<section class="dive"><h3>The week-six problem in a real <span class="italic">marathon block</span></h3><p>You asked Claude to build a marathon plan. By week six, it does not reliably know which long run you completed, what your watch recorded, or how the missed Tuesday session changes the next three weeks. You paste the history again, and the plan is effectively rebuilt from the latest conversation.</p><p>That is the gap between a smart chatbot and a coach that holds the block. Justus keeps the race date, the plan, your completed training, and your strength work in one persistent system, then adapts the weeks ahead without asking you to become the record keeper.</p></section>',
    '/vs/gemini/': '<section class="dive"><h3>The week-six problem in a real <span class="italic">marathon block</span></h3><p>You asked Gemini to build a marathon plan. By week six, it does not reliably know which long run you completed, what your watch recorded, or how the missed Tuesday session changes the next three weeks. You paste the history again, and the plan is effectively rebuilt from the latest conversation.</p><p>That is the gap between a smart chatbot and a coach that holds the block. Justus keeps the race date, the plan, your completed training, and your strength work in one persistent system, then adapts the weeks ahead without asking you to become the record keeper.</p></section>',
    '/vs/fitbod/': '<section class="dive"><h3>The hybrid-athlete question: <span class="italic">where does strength fit in the race block?</span></h3><p>Fitbod is useful when the lifting session is the main event. The harder problem for a runner, cyclist, swimmer, or triathlete is deciding how much strength belongs beside intervals, long sessions, and recovery. Justus treats lifting as part of the same event plan, so a hard lower-body day does not accidentally compete with the workout that matters most that week.</p></section>',
    '/vs/caliber/': '<section class="dive"><h3>For athletes who lift <span class="italic">inside an endurance block</span></h3><p>Caliber’s strength focus can be a good fit when strength is the primary goal. An athlete preparing for a marathon, triathlon, ride, or distance swim needs a different kind of coordination: strength has to support the event, move around key sessions, and scale down when fatigue rises. Justus keeps those decisions inside one plan rather than asking you to reconcile separate coaching systems.</p></section>',
    '/guides/best-strength-training-app/': '<section class="dive"><h3>Training for a race? Judge the strength app by <span class="italic">what it protects</span>.</h3><p>For a hybrid athlete, the best strength plan is not the one that maximizes gym volume in isolation. It is the one that preserves the long run, quality ride, swim progression, or event-specific session while still building useful strength. That is why a coordinated coach can be a better fit than a standalone lifting generator during a race block.</p></section>',
    '/guides/what-is-an-ai-fitness-coach/': '<section class="dive"><h3>A concrete test: <span class="italic">can it coach an event block?</span></h3><p>Ask what happens in week six of a marathon, half-marathon, triathlon, or distance-swim plan after you miss the long session and your watch shows a harder-than-expected week. A real AI coach should remember the event date, understand what was completed, protect the purpose of the block, and adjust the next weeks without rebuilding the relationship from scratch.</p></section>',
    '/guides/ai-vs-human-personal-trainer/': '<section class="dive"><h3>Event training makes the tradeoff <span class="italic">especially clear</span>.</h3><p>A strong human coach brings judgment, reassurance, and the ability to see nuance that data misses. A purpose-built AI coach can be available every day, read the watch data continuously, and revise the plan as soon as a week goes sideways. For an amateur athlete with a real race date, the best choice depends on whether you need high-touch human interpretation or affordable, persistent adaptation between every session.</p></section>'
  };

  var section = sections[window.location.pathname];
  var faq = document.querySelector('.faq-section');
  if (section && faq && !document.querySelector('[data-jus-144-event-context]')) {
    var wrapper = document.createElement('div');
    wrapper.setAttribute('data-jus-144-event-context', 'true');
    wrapper.innerHTML = section;
    faq.parentNode.insertBefore(wrapper.firstElementChild, faq);
  }
})();

// ─── FAQ accordion: only one open at a time ───
document.querySelectorAll('.faq-item').forEach(function (item) {
  item.addEventListener('toggle', function () {
    if (item.open) {
      document.querySelectorAll('.faq-item').forEach(function (other) {
        if (other !== item) other.open = false;
      });
    }
  });
});

// ─── Sticky nav: show border when scrolled past the top ───
(function () {
  var nav = document.getElementById('site-nav');
  if (!nav) return;
  function onScroll() {
    if (window.scrollY > 4) nav.classList.add('is-scrolled');
    else nav.classList.remove('is-scrolled');
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
