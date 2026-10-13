const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const render = require('../docs/publications.js');
const papers = JSON.parse(fs.readFileSync(path.join(__dirname, '../docs/content.json'), 'utf8')).journal;
const original = JSON.stringify(papers);
const fixture = {title: 'New paper <test>', authors: 'Test Author', venue: "Test journal, Editor's Choice", year: '2027', news_date: '2026-09-29', links: [], url: 'https://example.org/paper'};
// An added year wins even if an editor appends the record; both views use it.
const olderPapers = papers.map(p => ({...p, news_date: '2025-01', news_added_at: undefined}));
const changed = [...olderPapers, fixture];
const recent = render.recent(changed);
const journal = render.journal(changed);
assert.equal((recent.match(/<article /g) || []).length, 5);
assert.ok(recent.startsWith('<article class="news-item">'));
assert.ok(recent.includes('<strong>New paper &lt;test&gt;</strong>'));
assert.ok(journal.includes(render.publication(fixture, 'J' + changed.length)));
assert.ok(recent.includes('<time datetime="2026-09-29">Sep. 2026</time>'));
assert.ok(recent.includes('is accepted to <strong>Test journal</strong>.'));
assert.ok(render.news({...fixture, news_date: undefined}).includes('News date not provided'));
assert.ok(!render.news({...fixture, news_date: undefined}).includes('<time'));
assert.ok(render.publication(fixture).includes('publication-distinction'));
assert.equal(render.ordered([{...fixture, title:'First'}, {...fixture, title:'Second'}])[0].title, 'First');
assert.ok(!render.publication({...fixture, url:'javascript:alert(1)'}).includes('href='));
assert.equal(JSON.stringify(papers), original);
assert.equal((render.journal(papers).match(/class="publication-title-link"/g)||[]).length, papers.filter(p=>p.url).length);
console.log('PASS: additions update both views, latest five, stable ordering, links, escaping and distinctions.');

const newlyRegistered = {...fixture, title: 'Newly registered older-year paper', year: '2020', news_date: '2026-10', news_added_at: '2026-10-01T01:00:00+09:00'};
const registrationNews = render.recent([...olderPapers, newlyRegistered]);
assert.ok(registrationNews.includes('Oct. 2026'));
assert.ok(registrationNews.indexOf(newlyRegistered.title) < registrationNews.indexOf(papers[0].title));
assert.equal((registrationNews.match(/class="news-item"/g)||[]).length, 5);
console.log('PASS: registration order controls recent news.');

const numbers = [...render.journal(changed).matchAll(/<h3>\[J(\d+)\] /g)].map(m => Number(m[1]));
assert.deepEqual(numbers, changed.map((_,i)=>changed.length-i));
console.log("PASS: journal numbering stays continuous across years and additions.");

const custom = {news_date:'2026-10', segments:[{text:'Award <test>',bold:true,color:'red',url:'https://example.org/award'}]};
const combined = render.recent(olderPapers,[custom]);
assert.equal((combined.match(/class="news-item"/g)||[]).length,5);
assert.ok(combined.includes('news-award'));
assert.ok(combined.includes('Award &lt;test&gt;'));
assert.ok(combined.includes('href="https://example.org/award"'));
assert.equal((render.recent([], [custom]).match(/class="news-item"/g)||[]).length,1);
console.log('PASS: custom linked announcements merge with journals within the five-item limit.');

assert.match(render.news(fixture), /<a(?: class="news-paper-link")? href="https:\/\/example\.org\/paper" target="_blank" rel="noopener noreferrer"><strong>New paper &lt;test&gt;<\/strong><\/a>/);
assert.ok(!render.news({...fixture, url: 'javascript:alert(1)'}).includes('href='));
assert.ok(!render.news({...fixture, url: undefined}).includes('href='));
assert.ok(!render.news({...fixture, title: 'Low-Dose CT Denoising Using a Diffusion Prior via Score Distillation Sampling'}).includes('href='));
console.log('PASS: news titles link safely, preserving the specified exclusion.');

assert.ok(render.publication(fixture).includes('>New paper &lt;test&gt;</a>'));
assert.ok(!render.publication(fixture).includes('<span>Link</span>'));
