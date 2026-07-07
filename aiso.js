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
