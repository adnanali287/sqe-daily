'use strict';
const analyticsToken = window.SQE_CONFIG?.cloudflareAnalyticsToken;
if (analyticsToken && /^[a-f0-9]{32}$/i.test(analyticsToken)) {
  const beacon = document.createElement('script');
  beacon.type = 'module';
  beacon.src = 'https://static.cloudflareinsights.com/beacon.min.js';
  beacon.dataset.cfBeacon = JSON.stringify({ token: analyticsToken });
  document.head.append(beacon);
}
const filters = document.querySelector('.archive-filters');
const signupState = new URLSearchParams(location.search).get('subscription');
if (!document.getElementById('question') && document.getElementById('email-status') && ['pending', 'confirmed'].includes(signupState)) {
  const status = document.getElementById('email-status');
  status.hidden = false;
  status.textContent = signupState === 'pending' ? 'Check your inbox to confirm your subscription.' : 'Your subscription is confirmed. Thanks for joining SQE Daily.';
  history.replaceState(null, '', `${location.pathname}#daily-email`);
}
if (filters) {
  filters.hidden = false;
  filters.addEventListener('change', () => {
    let visible = 0;
    document.querySelectorAll('.archive-list li').forEach(item => {
      item.hidden = Boolean((document.getElementById('subject-filter').value && item.dataset.subject !== document.getElementById('subject-filter').value) || (document.getElementById('flk-filter').value && item.dataset.flk !== document.getElementById('flk-filter').value));
      if (!item.hidden) visible++;
    });
    document.getElementById('archive-empty').hidden = visible > 0;
  });
}
