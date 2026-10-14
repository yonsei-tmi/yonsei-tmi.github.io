/* Shared journal renderer: Home and Journal read the same ordered data. */
(function (root) {
  'use strict';
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function safeUrl(url) {
    try { const parsed = new URL(url); return ['https:', 'http:'].includes(parsed.protocol) ? parsed.href : ''; }
    catch { return ''; }
  }
  function ordered(records) {
    // Within the same year, preserve the journal's editorial order (newest first).
    return records.map((paper, index) => ({paper, index})).sort((a, b) => {
      const year = value => /^\d{4}$/.test(String(value)) ? Number(value) : 0;
      return year(b.paper.year) - year(a.paper.year) || a.index - b.index;
    }).map(({paper}) => paper);
  }
  function publication(paper, number = "") {
    const prefix = number ? '<span class="publication-number">[' + escape(number) + ']</span>' : "";
    let venue = escape(paper.venue);
    for (const label of ["Editor's Choice", 'Oral Presentation']) {
      venue = venue.replaceAll(escape(label), '<span class="publication-distinction">' + escape(label) + '</span>');
    }
    const url = safeUrl(paper.url);
    const title = url ? '<a class="publication-title-link" href="' + escape(url) + '" target="_blank" rel="noopener noreferrer">' + escape(paper.title) + '</a>' : escape(paper.title);
    const otherLinks = (paper.links || []).map(link => {
      const url = safeUrl(link.url);
      return url ? '<a href="' + escape(url) + '">' + escape(link.text) + '</a>' : '';
    }).filter(Boolean).join(' ');
    return '<article class="publication"><h3 class="numbered-publication-title">' + prefix + '<span class="publication-title-text">' + title + '</span></h3><p>' + escape(paper.authors) + '</p><p class="venue">' + venue + '</p>' + (otherLinks ? '<p class="paper-links">' + otherLinks + '</p>' : '') + '</article>';
  }
  function news(paper) {
    const date = /^\d{4}-(?:0[1-9]|1[0-2])(?:-\d{2})?$/.test(paper.news_date || '') ? paper.news_date : '';
    const months = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.'];
    const dateMarkup = date ? '<time datetime="' + date + '">' + months[Number(date.slice(5, 7)) - 1] + ' ' + date.slice(0, 4) + '</time>' : '<span aria-label="News date not provided">—</span>';
    if (Array.isArray(paper.segments)) {
      const body = paper.segments.map(segment => {
        let text = escape(segment.text);
        if (segment.bold) text = '<strong>' + text + '</strong>';
        if (segment.color === 'red') text = '<span class="news-award">' + text + '</span>';
        const url = safeUrl(segment.url);
        if (url) text = '<a href="' + escape(url) + '" target="_blank" rel="noopener noreferrer">' + text + '</a>';
        return text;
      }).join('');
      return '<article class="news-item"><div class="news-date">' + dateMarkup + '</div><p>' + body + '</p></article>';
    }
    const venue = paper.journal_name || paper.venue.split(',')[0];
    let title = '<strong>' + escape(paper.title) + '</strong>';
    const url = safeUrl(paper.url);
    if (url && paper.title !== 'Low-Dose CT Denoising Using a Diffusion Prior via Score Distillation Sampling') {
      title = '<a class="news-paper-link" href="' + escape(url) + '" target="_blank" rel="noopener noreferrer">' + title + '</a>';
    }
    return '<article class="news-item"><div class="news-date">' + dateMarkup + '</div><p>The paper &quot;' + title + '&quot; is accepted to <strong>' + escape(venue) + '</strong>.</p></article>';
  }
  function recent(records, additionalNews = []) {
    const rank = paper => paper.news_added_at || (paper.news_date ? paper.news_date.slice(0, 7) + '-01T00:00:00+09:00' : '');
    return ordered([...records, ...additionalNews]).sort((a, b) => rank(b).localeCompare(rank(a))).slice(0, 5).map(news).join('');
  }
  function journal(records) {
    const papers = ordered(records);
    const years = [...new Set(papers.map(p => p.year))];
    let number = papers.length;
    const id = year => 'year-' + String(year).replace(/[^a-zA-Z0-9_-]/g, '-');
    return '<nav class="year-nav" aria-label="Publication years">' + years.map(year => '<a href="#' + id(year) + '">' + escape(year) + '</a>').join('') + '</nav><div>' + years.map(year => '<section class="year-group" id="' + id(year) + '"><h2>' + escape(year) + '</h2>' + papers.filter(p => p.year === year).map(p => publication(p, 'J' + (number--))).join('') + '</section>').join('') + '</div>';
  }
  const api = {ordered, publication, news, recent, journal};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.TMIPublications = api;
})(typeof window !== 'undefined' ? window : globalThis);
