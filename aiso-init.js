/* ─── PostHog init for AISO pages.
 * Loaded synchronously in <head>. Each page declares
 *   <script>window.PAGE_SLUG = 'vs-strava';</script>
 * BEFORE this file so the slug is available to register + capture.
 * ─── */

!function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init Ee Ms Os capture We calculateEventProperties Ls register register_once register_for_session unregister unregister_for_session js getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSurveysLoaded onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey canRenderSurveyAsync identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty Ds Fs createPersonProfile Is Ps opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing Cs debug ks getPageViewId captureTraceFeedback captureTraceMetric".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);

posthog.init('phc_pbMi5H1xZJmtZDDOw3plQzjBzs4dt8ohf1nY54Nl9N8', {
  api_host: 'https://us.i.posthog.com',
  person_profiles: 'identified_only',
  capture_pageview: false,
  capture_pageleave: true,
});

/* ─── Internal opt-out: visit any page once with ?internal=1 to stop
 * counting this browser (founder/testing devices). ?internal=0 re-enables. ─── */
(function () {
  try {
    var flag = new URLSearchParams(window.location.search).get('internal');
    if (flag === '1') localStorage.setItem('justus_internal', '1');
    if (flag === '0') {
      localStorage.removeItem('justus_internal');
      posthog.opt_in_capturing();
    }
    if (localStorage.getItem('justus_internal') === '1') {
      posthog.opt_out_capturing();
    }
  } catch (e) {}
})();

window.addEventListener('load', function () {
  try {
    posthog.register({
      page_type: 'aiso',
      page_slug: window.PAGE_SLUG || 'unknown',
    });
    posthog.capture('$pageview');
  } catch (e) {}
});
