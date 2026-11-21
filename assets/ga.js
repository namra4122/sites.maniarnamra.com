/* Google Analytics 4 for sites.maniarnamra.com — the only place the
 * measurement ID lives. Pages include it with:
 *   <script async src="/assets/ga.js"></script>
 * (.github/scripts/inject-ga.py adds that line to new pages automatically.)
 *
 * Same GA4 property and web stream as maniarnamra.com. gtag's default
 * cookie_domain "auto" puts _ga on .maniarnamra.com, so visitors keep one
 * client ID across both sites without any cross-domain linker.
 *
 * Consent Mode v2: analytics_storage is denied by default in the EEA, UK and
 * Switzerland and granted elsewhere; ad storage is denied everywhere (no ads).
 * The visitor's choice is stored in a ga_consent cookie on .maniarnamra.com,
 * so a choice made on either site applies to both. Reopen the banner with any
 * element carrying [data-consent-open], or window.siteConsent.open().
 *
 * No dependencies, no build step. Colours come from the page's CSS tokens
 * (--bg, --fg, --muted, --line, --accent) with light/dark fallbacks. */
(() => {
  'use strict';
  const GA_ID = 'G-4H49QFHPQK';
  const CONSENT_COOKIE = 'ga_consent';
  const CONSENT_REQUIRED_REGIONS = [
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU',
    'IS', 'IE', 'IT', 'LV', 'LI', 'LT', 'LU', 'MT', 'NL', 'NO', 'PL', 'PT', 'RO',
    'SK', 'SI', 'ES', 'SE', 'GB', 'CH',
  ];

  const w = window;
  const d = document;
  if (w.siteConsent) return; // included twice

  // Only measure the real site, never file://, localhost previews or forks.
  const host = location.hostname;
  const PARENT = 'maniarnamra.com';
  const isProd = host === PARENT || host.endsWith('.' + PARENT);
  const forceDebug = /[?&]ga_debug=1\b/.test(location.search);
  if (!isProd && !forceDebug) return;

  const readConsent = () => {
    const m = d.cookie.match(/(?:^|;\s*)ga_consent=(granted|denied)/);
    return m ? m[1] : null;
  };
  const writeConsent = (v) => {
    const domain = isProd ? '; Domain=.' + PARENT : '';
    const secure = location.protocol === 'https:' ? '; Secure' : '';
    d.cookie = `${CONSENT_COOKIE}=${v}; Path=/; Max-Age=31536000; SameSite=Lax${domain}${secure}`;
  };
  const clearGaCookies = () => {
    const parts = host.split('.');
    const domains = ['', host];
    for (let i = 1; i < parts.length - 1; i++) domains.push('.' + parts.slice(i).join('.'));
    d.cookie.split(';').forEach((c) => {
      const name = c.split('=')[0].trim();
      if (name !== '_ga' && name.indexOf('_ga_') !== 0) return;
      domains.forEach((dom) => {
        d.cookie = `${name}=; Max-Age=0; Path=/${dom ? '; Domain=' + dom : ''}`;
      });
    });
  };

  // ── gtag bootstrap (order matters: consent defaults before config) ──
  w.dataLayer = w.dataLayer || [];
  function gtag() { w.dataLayer.push(arguments); }
  w.gtag = w.gtag || gtag;
  const denied = { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' };
  gtag('consent', 'default', Object.assign({ analytics_storage: 'denied', region: CONSENT_REQUIRED_REGIONS, wait_for_update: 500 }, denied));
  gtag('consent', 'default', Object.assign({ analytics_storage: 'granted' }, denied));
  const stored = readConsent();
  if (stored) gtag('consent', 'update', { analytics_storage: stored });
  gtag('js', new Date());
  gtag('config', GA_ID, forceDebug ? { debug_mode: true } : {});

  const s = d.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
  d.head.appendChild(s);

  // ── consent banner (shadow DOM so page CSS can't break it, or vice versa) ──
  let hostEl = null;
  const close = () => { if (hostEl) { hostEl.remove(); hostEl = null; } };
  const choose = (v) => {
    writeConsent(v);
    gtag('consent', 'update', { analytics_storage: v });
    if (v === 'denied') clearGaCookies();
    close();
  };
  const open = () => {
    if (hostEl) return;
    hostEl = d.createElement('div');
    hostEl.setAttribute('data-ga-consent', '');
    const root = hostEl.attachShadow({ mode: 'open' });
    root.innerHTML = `<style>
:host{all:initial}
.b{position:fixed;z-index:2147483646;left:1rem;right:1rem;bottom:1rem;margin:0 auto;max-width:26rem;box-sizing:border-box;padding:.9rem 1rem;
  font:.875rem/1.5 system-ui,-apple-system,'Segoe UI',sans-serif;color:var(--fg,#111);background:var(--bg,#fff);
  border:1px solid var(--line,#ccc);border-radius:.375rem;box-shadow:0 .5rem 2rem rgba(0,0,0,.18)}
@media (min-width:40rem){.b{left:auto;margin:0}}
@media (prefers-color-scheme:dark){.b{color:var(--fg,#eee);background:var(--bg,#161616);border-color:var(--line,#333)}}
p{margin:0;color:var(--muted,inherit)}
.r{display:flex;justify-content:flex-end;gap:.5rem;margin-top:.75rem}
button{font:inherit;cursor:pointer;padding:.3rem .8rem;border-radius:.25rem;border:1px solid var(--line,#999);background:transparent;color:inherit}
button.a{background:var(--accent,#111);border-color:var(--accent,#111);color:var(--bg,#fff)}
@media (prefers-color-scheme:dark){button.a{background:var(--accent,#eee);border-color:var(--accent,#eee);color:var(--bg,#111)}}
button:focus-visible{outline:2px solid var(--accent,#2563eb);outline-offset:2px}
</style><div class="b" role="region" aria-label="Cookie consent"><p>I use Google Analytics cookies to see which pages get read. No ads, no tracking across other sites.</p>
<div class="r"><button type="button" data-v="denied">Decline</button><button type="button" class="a" data-v="granted">Accept</button></div></div>`;
    root.addEventListener('click', (e) => {
      const v = e.target && e.target.getAttribute && e.target.getAttribute('data-v');
      if (v) choose(v);
    });
    d.body.appendChild(hostEl);
  };

  w.siteConsent = { open, get: readConsent };
  d.addEventListener('click', (e) => {
    const t = e.target && e.target.closest && e.target.closest('[data-consent-open]');
    if (t) { e.preventDefault(); open(); }
  });
  const ready = () => { if (!readConsent()) open(); };
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', ready);
  else ready();
})();
