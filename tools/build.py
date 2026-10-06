import pathlib,json,html,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'
D=json.loads((OUT/'content.json').read_text(encoding='utf-8'))
E=html.escape
NAV=[('Home','index.html'),('Research','research.html'),('People','people.html'),('Publications','journal.html'),('Patents','patents.html'),('Join Us','join.html')]
def page(filename,title,content,active,sub='',source=None):
    nav=''.join(f'<a href="{url}"'+(' aria-current="page"' if name==active else '')+f'>{name}</a>' for name,url in NAV)
    head='' if filename=='index.html' else f'<div class="page-heading"><h1>{title}</h1>'+ (f'<p>{sub}</p>' if sub else '')+'</div>'
    output=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} | TMI Lab · Yonsei University</title><meta name="description" content="Translational Medical Intelligence Lab at Yonsei University. Medical imaging, trustworthy AI, computational imaging, and clinical translation."><meta name="theme-color" content="#14319C"><link rel="icon" type="image/svg+xml" href="favicon.svg"><link rel="stylesheet" href="style.css"><script src="publications.js" defer></script><script src="site.js" defer></script></head><body><a class="skip" href="#main">Skip to main content</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="index.html" aria-label="TMI Lab home"><img src="assets/tmi-logo-intelligence.png" alt="TMI"><span class="university-brand"><img class="university-logo" src="assets/yonsei-wordmark.svg" alt="Yonsei University" width="148" height="44"></span></a><button class="menu-toggle" type="button" aria-label="Open navigation" aria-controls="navigation" aria-expanded="false">☰</button><nav id="navigation" class="nav" aria-label="Main navigation">{nav}</nav></div></header><main id="main" class="wrap">{head}{content}</main><footer class="site-footer"><div class="wrap"><div class="footer-grid"><div><h3>TMI Lab</h3><p>Translational Medical Intelligence Laboratory<br>Department of Artificial Intelligence · Yonsei University</p><a href="mailto:jongdukbaek@yonsei.ac.kr">jongdukbaek@yonsei.ac.kr</a></div></div><p class="copyright">© 2026 TMI Lab, Yonsei University.</p></div></footer></body></html>'''
    output=output.replace('href="style.css"','href="style.css?v=20261006-join-centered"').replace('src="publications.js"','src="publications.js?v=20261002-news-hover"').replace('src="site.js"','src="site.js?v=20260930-news-five"')
    if filename == "index.html":
        output = output.replace('<main id="main" class="wrap">', '<main id="main" class="home-main">')
    (OUT/filename).write_text(output,encoding='utf-8')
def tabs(items,current):return '<nav class="subnav" aria-label="Section navigation">'+''.join(f'<a href="{f}"'+(' aria-current="page"' if f==current else '')+f'>{name}</a>' for name,f in items)+'</nav>'
PEOPLE=[('Professor','people.html'),('Researchers','researchers.html'),('Alumni','alumni.html')]
PUBS=[('Journal','journal.html'),('Conference','conference.html')]
areas=[('Real-world imaging systems','We study medical images as outputs of physical acquisition systems.',['Imaging physics & geometry','Scanners, protocols & dose','Artifacts & acquisition variability','Real patient data']),('Clinical intelligence under image quality variation','We develop restoration and diagnostic AI that is robust in the real world.',['Artifact reduction & restoration','Image quality assessment','Uncertainty modeling','Downstream task performance']),('Evidence-driven translation','We bridge AI development and real clinical impact.',['Foundation data infrastructure','Task-based & reader-aligned evaluation','Clinical workflow integration','MVP, IP, and startup-driven translation'])]
def area_grid(images=False):
    out='<div class="approach">'
    for n,(title,desc,points) in enumerate(areas):
        image=f'<img class="research-visual" src="{D["images"]["home"][n]}" alt="{E(title)}" loading="lazy">' if images else ''
        out+=f'<article>{image}<span class="number">0{n+1}</span><h3>{title}</h3><p>{desc}</p><ul class="bullets">'+''.join(f'<li>{E(p)}</li>' for p in points)+'</ul></article>'
    return out+'</div>'
def publication(p, number=""):
    prefix=f"[{E(number)}] " if number else ""
    venue=E(p['venue'])
    for label in ["Editor's Choice", 'Oral Presentation']:
        venue=venue.replace(E(label), '<span class="publication-distinction">'+E(label)+'</span>')
    clip='<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m21.4 11.6-9.2 9.2a6 6 0 0 1-8.5-8.5l10-10a4 4 0 0 1 5.7 5.7l-10 10a2 2 0 0 1-2.8-2.8l9.2-9.2"/></svg>'
    paper_link=f' <a class="publication-link" href="{E(p["url"],quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="Open paper: {E(p["title"],quote=True)}">{clip}<span>Link</span></a>' if p.get('url') else ''
    links=' '.join(f'<a href="{E(a["url"],quote=True)}">{E(a["text"])}</a>' for a in p['links'])
    return f'<article class="publication"><h3>{prefix}{E(p["title"])}{paper_link}</h3><p>{E(p["authors"])}</p><p class="venue">{venue}</p>'+ (f'<p class="paper-links">{links}</p>' if links else '')+'</article>'
def news(p):
    date=p.get('news_date','')
    months=['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.']
    date_markup=f'<time datetime="{date}">{months[int(date[5:7])-1]} {date[:4]}</time>' if re.fullmatch(r'\d{4}-(?:0[1-9]|1[0-2])(?:-\d{2})?',date) else '<span aria-label="News date not provided">—</span>'
    if 'segments' in p:
        parts=[]
        for segment in p['segments']:
            text=E(segment['text'])
            if segment.get('bold'): text='<strong>'+text+'</strong>'
            if segment.get('color')=='red': text='<span class="news-award">'+text+'</span>'
            url=segment.get('url','')
            if re.match(r'^https?://',url): text='<a href="'+E(url,quote=True)+'" target="_blank" rel="noopener noreferrer">'+text+'</a>'
            parts.append(text)
        return f'<article class="news-item"><div class="news-date">{date_markup}</div><p>'+''.join(parts)+'</p></article>'
    venue=p.get('journal_name') or p['venue'].split(',')[0]
    title='<strong>'+E(p['title'])+'</strong>'
    url=p.get('url') or ''
    if re.match(r'^https?://',url) and p['title'] != 'Low-Dose CT Denoising Using a Diffusion Prior via Score Distillation Sampling':
        title='<a class="news-paper-link" href="'+E(url,quote=True)+'" target="_blank" rel="noopener noreferrer">'+title+'</a>'
    return f'<article class="news-item"><div class="news-date">{date_markup}</div><p>The paper &quot;{title}&quot; is accepted to <strong>{E(venue)}</strong>.</p></article>'

home='''<section class="hero"><h1>Translational Medical <em>Intelligence</em> Lab</h1><p class="subtitle">From medical imaging AI to Translational Medical Intelligence</p></section><section class="intro"><div class="intro-copy"><p>Welcome to <strong class="intro-highlight">Translational Medical Intelligence (TMI)</strong> Lab at <strong class="intro-highlight">Yonsei University</strong>. <strong class="intro-highlight">We focus on multiple aspects of biomedical imaging</strong>—ranging from data acquisition to image reconstruction, enhancement, and quality assessment. Our research spans areas such as <strong class="intro-highlight">medical physics, computational imaging,</strong> and <strong class="intro-highlight">machine learning</strong> to advance imaging technologies for healthcare and broader scientific applications.</p></div><div class="lab-mark"><img src="assets/tmi-logo-intelligence.png" alt="TMI — Translational Medical Intelligence" width="1984" height="800"></div></section>'''
home_featured = next(p for p in D['journal'] if p['title'] == 'Low-Dose CT Denoising Using a Diffusion Prior via Score Distillation Sampling')
home_featured_tags = ''.join('<li>#' + E(tag) + '</li>' for tag in ['LDCT', 'Image denoising', 'Diffusion prior', 'Score distillation sampling'])
home_featured_card = f'<article class="research-paper-card home-featured-paper"><div class="research-paper-visual"><img src="assets/researchareas_figure.png" alt="Framework for {E(home_featured["title"], quote=True)}" loading="lazy" width="968" height="547"></div><div class="research-paper-info"><p class="research-paper-venue">{E(home_featured["venue"])}</p><h3>{E(home_featured["title"])}</h3><p class="research-paper-authors">{E(home_featured["authors"])}</p><ul class="research-paper-tags" aria-label="Research keywords">{home_featured_tags}</ul></div></article>'
home+='<section class="section" aria-labelledby="research-areas-title"><div class="section-heading"><h2 id="research-areas-title">Research Areas</h2><a href="research.html">Explore our research</a></div><div class="home-research-layout"><p class="home-research-summary">Our recent work includes <strong>deep learning-based image enhancement</strong>, <strong>dental imaging</strong>, <strong>novel X-ray imaging system</strong>, and <strong>task-specific image quality evaluation</strong>. We build on recent advances to address practical challenges in medical imaging. Our goal is to develop methods that can be applied in clinical practice, with an emphasis on diagnostic image quality.</p>'+home_featured_card+'</div></section>'
home+='<section class="section"><div class="section-heading"><h2>Recent News</h2><a href="journal.html">All publications</a></div>'+'<div class="news-list" data-recent-news>'+''.join(news(p) for p in sorted(sorted(D['journal']+D.get('news',[]),key=lambda p:int(p.get('year','0')) if p.get('year','0').isdigit() else 0,reverse=True),key=lambda p:p.get('news_added_at') or (p.get('news_date','')[:7]+'-01T00:00:00+09:00' if p.get('news_date') else ''),reverse=True)[:5])+'</div></section>'
home+='''<section class="section contact"><div><h2>Contact</h2><h3>Translational Medical Intelligence Lab</h3><p>Department of Artificial Intelligence<br>Yonsei University</p><a href="mailto:jongdukbaek@yonsei.ac.kr">jongdukbaek@yonsei.ac.kr</a></div><div><h2>Join TMI</h2><p><br>We value strong fundamentals, curiosity, and a collaborative attitude.</p><a class="button" href="join.html">Join our research</a></div></section>'''
page('index.html','Home',home,'Home')
def research_paper_card(spec):
    paper = dict(spec)
    if spec.get('source_kind'):
        matches = [p for p in D[spec['source_kind']] if (spec.get('source_url') and p.get('url') == spec['source_url']) or p['title'] == spec['source_title']]
        if len(matches) != 1:
            print('Skipping unavailable Research paper: ' + spec['source_title'])
            return ''
        paper = {**matches[0], **spec}
    title = E(paper['title'])
    url = paper.get('url', '')
    is_conference = paper.get('source_kind') == 'conference'
    if re.match(r'^https?://', url) and (not is_conference or spec.get('url')):
        title = f'<a href="{E(url, quote=True)}" target="_blank" rel="noopener noreferrer">{title}</a>'
    image = paper.get('image', '')
    visual = f'<img src="{E(image, quote=True)}" alt="{E(paper["title"], quote=True)}" loading="lazy">' if image else '<div class="research-paper-placeholder" aria-hidden="true"></div>'
    visual = '' if is_conference else f'<div class="research-paper-visual">{visual}</div>'
    card_class = 'research-paper-card research-paper-text-only' if is_conference else 'research-paper-card'
    authors = f'<p class="research-paper-authors">{E(paper["authors"])}</p>' if paper.get('authors') else ''
    tags = ''.join('<li>#' + E(tag) + '</li>' for tag in paper.get('tags', []))
    return f'<article class="{card_class}">{visual}<div class="research-paper-info"><p class="research-paper-venue">{E(paper["venue"])}</p><h4>{title}</h4>{authors}<ul class="research-paper-tags" aria-label="Research keywords">{tags}</ul></div></article>'

research_data = json.loads((OUT/'research.json').read_text(encoding='utf-8'))
research = '<div class="research-topics">'
for n, topic in enumerate(research_data['topics'], 1):
    tasks = ''.join('<li>' + E(task) + '</li>' for task in topic['tasks'])
    cards = ''.join(research_paper_card(p) for p in topic['papers'])
    selected = '<h3 class="research-label">Selected papers</h3><div class="research-paper-list">' + cards + '</div>' if cards else ''
    topic_id = E(topic['id'], quote=True)
    research += f'<section class="research-topic" id="{topic_id}" aria-labelledby="{topic_id}-title"><div class="research-topic-heading"><span class="research-topic-number">{n:02}</span><h2 id="{topic_id}-title">{E(topic["title"])}</h2></div><p class="research-topic-description">{E(topic["description"])}</p><h3 class="research-label">Research tasks</h3><ul class="research-task-list">{tasks}</ul>{selected}</section>'
research += '</div>'
page('research.html', 'Research', research, 'Research')
bio=D['professor']['bio']
experience=D['professor']['experience']
education=D['professor']['education']
profile=tabs(PEOPLE,'people.html')+f'''<section class="profile"><img src="{D['images']['professor'][0]}" alt="Jongduk Baek"><div><p class="eyebrow">Professor</p><h2>Jongduk Baek, Ph.D.</h2><p class="role">Professor &amp; Chair</p><p>Department of Artificial Intelligence, Yonsei University</p><p>{E(bio)}</p><div class="profile-links"><a class="scholar-link" href="https://scholar.google.com/citations?user=Cj0ntKwAAAAJ&amp;hl=ko" target="_blank" rel="noopener noreferrer" aria-label="Google Scholar (opens in a new tab)"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M2 9l10-5 10 5-10 5-10-5Z"/><path d="M6 11v6c3 3 9 3 12 0v-6M22 9v6"/></svg><span>Google Scholar</span></a><a class="scholar-link" href="mailto:jongdukbaek@yonsei.ac.kr" aria-label="Mail: jongdukbaek@yonsei.ac.kr" title="jongdukbaek@yonsei.ac.kr"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/></svg><span>Mail</span></a><a class="scholar-link" href="tel:+82221235737" aria-label="Phone: +82-02-2123-5737" title="+82-02-2123-5737"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.12.96.36 1.9.7 2.79a2 2 0 0 1-.45 2.11L8.09 9.89a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.89.34 1.83.58 2.79.7A2 2 0 0 1 22 16.92z"/></svg><span>Phone</span></a></div></div></section><section class="section career-section"><h2>Experience</h2><ul class="affiliations">'''+''.join(f'<li><strong>{E(a["dates"])}</strong> : {E(a["description"])}</li>' for a in experience)+'</ul></section>'
profile+='<section class="section career-section"><h2>Education</h2><ul class="affiliations">'+''.join(f'<li><strong>{E(a["dates"])} : {E(a["description"])}</strong><br>'+'<br>'.join(E(x) for x in a["details"])+'</li>' for a in education)+'</ul></section>'
page('people.html','Professor',profile,'People',sub='')
def career_text(text):
    return E(text)

def person(p):
    photo=f'<img src="{p["image"]}" alt="{E(p["name"])}" loading="lazy">' if p['image'] else '<div class="portrait-fallback" aria-hidden="true">'+''.join(w[0] for w in p['name'].split())+'</div>'
    email=''.join(f'<p class="member-email"><a href="mailto:{E(t)}">{E(t)}</a></p>' for t in p['details'] if '@' in t)
    parts=email
    if 'appointment' in p:
        parts+='<p class="member-appointment">'+career_text(p['appointment'])+'</p>'
        parts+='<ul class="member-background">'+''.join('<li>'+career_text(t)+'</li>' for t in p['background'])+'</ul>'
    for n,t in enumerate(p['details']):
        if '@' in t or (n==0 and t=='Staff'):
            continue
        researcher='group' in p
        if researcher and n==0:
            continue
        text=f'<a href="mailto:{E(t)}">{E(t)}</a>' if '@' in t else E(t)
        if researcher and n==1:
            text='<strong class="interest-label">Interest:</strong> '+text
        parts+='<p class="'+('role' if n==0 else '')+'">'+text+'</p>'
    links=''
    if p.get('scholar_url'):
        links+=f'<a class="scholar-link" href="{E(p["scholar_url"],quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="Google Scholar for {E(p["name"],quote=True)} (opens in a new tab)"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M2 9l10-5 10 5-10 5-10-5Z"/><path d="M6 11v6c3 3 9 3 12 0v-6M22 9v6"/></svg><span>Google Scholar</span></a>'
    if p.get('website_url'):
        links+=f'<a class="scholar-link" href="{E(p["website_url"],quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="Website for {E(p["name"],quote=True)} (opens in a new tab)"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18M5 6h14M5 18h14"/></svg><span>Website</span></a>'
    if links:
        parts+='<div class="member-scholar">'+links+'</div>'
    return f'<article class="person">{photo}<div><h3>{E(p["name"])}</h3>{parts}</div></article>'
for key,title,desc in [('researchers','Researchers',''),('alumni','Alumni','')]:
    members=[p for p in D[key] if p['details'][0]!='Staff'];staff=[p for p in D[key] if p['details'][0]=='Staff']
    content=tabs(PEOPLE,key+'.html')
    if key=='researchers':
        for group in ['Research Associate','Postdoc','Ph.D. Students','M.S./Ph.D. Students','M.S. Students']:
            group_title={'Research Associate':'Research Associates','Postdoc':'Postdocs'}.get(group,group)
            content+=f'<section class="researcher-group"><h2 class="member-group-title">{E(group_title)}</h2><div class="people-grid">'+''.join(person(p) for p in members if p['group']==group)+'</div></section>'
    else:
        content+='<div class="people-grid">'+''.join(person(p) for p in members)+'</div>'
    if staff:content+='<h2 class="member-group-title">Staff</h2><div class="people-grid">'+''.join(person(p) for p in staff)+'</div>'
    page(key+'.html',title,content,'People',sub=desc)
for key,title,desc in [('journal','Journal',''),('conference','Conference','')]:
    years=list(dict.fromkeys(p['year'] for p in D[key]))
    content=tabs(PUBS,key+'.html').replace('class="subnav"','class="subnav publication-tabs"')+'<div class="pub-layout"><nav class="year-nav" aria-label="Publication years">'+''.join(f'<a href="#year-{y.replace(" ","-")}">{y}</a>' for y in years)+'</nav><div>'
    labels={id(p): ('J' if key=='journal' else 'C')+str(len(D[key])-i+1) for i,p in enumerate((p for year in years for p in D[key] if p['year']==year),1)}
    for year in years:content+=f'<section class="year-group" id="year-{year.replace(" ","-")}"><h2>{year}</h2>'+''.join(publication(p,labels[id(p)]) for p in D[key] if p['year']==year)+'</section>'
    if key=='journal':content=content.replace('<div class="pub-layout">','<div class="pub-layout" data-journal-publications>')
    page(key+'.html',title,content+'</div></div>','Publications',sub=desc)
page('patents.html','Patents','<div class="pub-layout patent-layout"><div class="patent-gutter" aria-hidden="true"></div><section>'+''.join(publication(p,'P'+str(len(D['patents'])-i+1)) for i,p in enumerate(D['patents'],1))+'</section></div>','Patents',sub='')
join='''<p class="join-intro">We work at the intersection of artificial intelligence, imaging physics, and clinical translation.</p>'''
join+='<section class="section"><p class="join-recruitment">We are looking for highly <strong class="motivation-highlight">self-motivated</strong> students who are interested in developing <strong class="motivation-highlight">advanced AI progress</strong><br>for medical imaging and its application.</p><div class="join-contact"><h2>Join TMI and work on the next generation of AI.</h2><p>Please contact <a href="mailto:jongdukbaek@yonsei.ac.kr">jongdukbaek@yonsei.ac.kr</a>.</p></div></section>'
join+='<section class="section location" aria-labelledby="location-heading"><h2 id="location-heading">Location</h2><div class="location-content"><div class="location-info"><h3>Translational Medical Intelligence Lab</h3><p lang="ko"><strong>주소:</strong> 서울특별시 서대문구 연세로 50, 공학원 440호</p><p><strong>Address:</strong> Room 440, Gonghakwon, Yonsei University,<br>50 Yonsei-ro, Seodaemun-gu, Seoul, Republic of Korea</p><a class="button" href="https://www.google.com/maps/search/?api=1&amp;query=%EC%97%B0%EC%84%B8%EB%8C%80%ED%95%99%EA%B5%90%20%EA%B3%B5%ED%95%99%EC%9B%90%20%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C%20%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC%20%EC%97%B0%EC%84%B8%EB%A1%9C%2050" target="_blank" rel="noopener noreferrer">View on Google Maps ↗</a></div><div class="location-map"><iframe title="Map to Yonsei University Gonghakwon" src="https://www.google.com/maps/embed?pb=!1m5!3m3!1m2!1s0x357c9913cd31e10d%3A0x2e862a8b6ba600ad!2z7Jew7IS464yA7ZWZ6rWQIOqzte2VmeybkA!5e0!3m2!1sko!2skr!4v1790727317773!5m2!1sko!2skr" width="100%" height="300" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div></div></section>'
page('join.html','Join TMI',join,'Join Us',sub='')
(OUT/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#14319C"/><text x="24" y="31" text-anchor="middle" font-family="Arial,sans-serif" font-weight="bold" font-size="21" fill="white">TMI</text></svg>',encoding='utf-8')
(OUT/'.nojekyll').touch()
print('Built 9 static pages.')
