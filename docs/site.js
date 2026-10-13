const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('.nav');

{
  const topButton = document.createElement('button');
  topButton.type = 'button';
  topButton.className = 'back-to-top';
  topButton.setAttribute('aria-label', 'Back to top');
  topButton.title = 'Back to top';
  topButton.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 10 6-6 6 6M12 4v16"/></svg><span>TOP</span>';
  topButton.addEventListener('click', () => {
    document.querySelector('.brand')?.focus({preventScroll: true});
    window.scrollTo({top: 0, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
  });
  const updateTopButton = () => { topButton.hidden = window.scrollY <= 0; };
  updateTopButton();
  document.body.append(topButton);
  window.addEventListener('scroll', updateTopButton, {passive: true});
  window.addEventListener('pageshow', updateTopButton);
}
toggle?.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  nav.classList.toggle('open', open);
});

// Progressive enhancement: file:// and failed requests retain the static content.
const recentNews = document.querySelector('[data-recent-news]');
const journalPublications = document.querySelector('[data-journal-publications]');
if ((recentNews || journalPublications) && location.protocol !== 'file:') {
  fetch('content.json', {cache: 'no-store'})
    .then(response => {
      if (!response.ok) throw new Error('Journal data unavailable');
      return response.json();
    })
    .then(data => {
      if (!Array.isArray(data.journal) || !data.journal.every(paper =>
        paper && ['title', 'authors', 'venue', 'year'].every(key => typeof paper[key] === 'string'))) {
        throw new Error('Invalid journal data');
      }
      if (recentNews) recentNews.innerHTML = TMIPublications.recent(data.journal, Array.isArray(data.news) ? data.news : []);
      if (journalPublications) journalPublications.innerHTML = TMIPublications.journal(data.journal);
      if (location.hash.startsWith('#year-')) {
        document.getElementById(location.hash.slice(1))?.scrollIntoView();
      }
    })
    .catch(() => { /* Keep the complete pre-rendered publication list. */ });
}
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && nav?.classList.contains('open')) {
    nav.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open navigation');
    toggle.focus();
  }
});

// Keep direct contact links when JavaScript is unavailable.
const contactLinks = document.querySelectorAll('.profile-links a[href^="mailto:"], .profile-links a[href^="tel:"]');
const contactControls = [];
function closeContacts(except) {
  contactControls.forEach(({trigger, panel}) => {
    if (panel !== except) {
      panel.hidden = true;
      trigger.setAttribute('aria-expanded', 'false');
    }
  });
}
contactLinks.forEach((link, index) => {
  const isMail = link.protocol === 'mailto:';
  const value = isMail ? link.getAttribute('href').slice(7) : link.title;
  const wrapper = document.createElement('span');
  wrapper.className = 'contact-control';
  const trigger = document.createElement('button');
  trigger.type = 'button';
  trigger.className = 'scholar-link contact-trigger';
  trigger.innerHTML = link.innerHTML;
  trigger.title = value;
  trigger.setAttribute('aria-expanded', 'false');
  trigger.setAttribute('aria-controls', `contact-options-${index}`);
  const panel = document.createElement('span');
  panel.id = `contact-options-${index}`;
  panel.className = 'contact-options';
  panel.hidden = true;
  panel.setAttribute('role', 'group');
  panel.setAttribute('aria-label', isMail ? 'Email options' : 'Phone options');
  const copy = document.createElement('button');
  copy.type = 'button';
  copy.className = 'contact-action';
  copy.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="8" y="8" width="12" height="13" rx="2"/><path d="M5 16H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v1"/></svg><span>Copy</span>';
  const copyLabel = copy.querySelector('span');
  copyLabel.setAttribute('aria-live', 'polite');
  copy.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(value);
      copyLabel.textContent = 'Copied!';
    } catch {
      copyLabel.textContent = 'Try again';
    }
  });
  const action = link.cloneNode(true);
  action.className = 'contact-action';
  action.querySelector('span').textContent = isMail ? 'Open Mail' : 'Call';
  action.setAttribute('aria-label', isMail ? 'Open Mail' : 'Call');
  action.addEventListener('click', () => closeContacts());
  panel.append(copy, action);
  wrapper.append(trigger, panel);
  link.replaceWith(wrapper);
  contactControls.push({trigger, panel});
  trigger.addEventListener('click', () => {
    const opening = panel.hidden;
    closeContacts();
    panel.hidden = !opening;
    trigger.setAttribute('aria-expanded', String(opening));
    copyLabel.textContent = 'Copy';
  });
  wrapper.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      closeContacts();
      trigger.focus();
    }
  });
  wrapper.addEventListener('focusout', event => {
    if (!wrapper.contains(event.relatedTarget)) closeContacts();
  });
});
document.addEventListener('click', event => {
  if (!event.target.closest('.contact-control')) closeContacts();
});

// Independent page controls for the two latest papers.
document.querySelectorAll('[data-paper-pages]').forEach(card => {
  const pages = JSON.parse(card.dataset.paperPages);
  const image = card.querySelector('.latest-paper-viewer img');
  const previous = card.querySelector('.paper-prev');
  const next = card.querySelector('.paper-next');
  const count = card.querySelector('.paper-page-count');
  let page = 0;
  function showPage(index) {
    page = Math.max(0, Math.min(pages.length - 1, index));
    image.src = pages[page];
    image.alt = `${card.getAttribute('aria-label')} - page ${page + 1}`;
    count.textContent = `${page + 1} / ${pages.length}`;
    previous.disabled = page === 0;
    next.disabled = page === pages.length - 1;
  }
  previous.addEventListener('click', () => showPage(page - 1));
  next.addEventListener('click', () => showPage(page + 1));
});
