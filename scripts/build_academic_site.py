#!/usr/bin/env python3
"""Build the public academic site with Python's standard library only."""
import html
import json
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'site'
OUT = ROOT / 'dist'
PROFILE = json.loads((SOURCE / 'data/profile.json').read_text())
PAPERS = json.loads((SOURCE / 'data/publications.json').read_text())
SITE_URL = 'https://ebeame.github.io'


def esc(value):
    return html.escape(str(value), quote=True)


def authors(value):
    return esc(value).replace('Yibin Wang', '<strong>Yibin Wang</strong>')


def bibtex(paper):
    kind = {'Journal': 'article', 'Conference': 'inproceedings', 'Book chapter': 'incollection'}[paper['type']]
    venue = 'journal' if kind == 'article' else 'booktitle'
    names = paper['authors'].replace('†', '').replace('*', '').split(', ')
    lines = [f'@{kind}{{{paper["id"]},', f'  title = {{{paper["title"]}}},',
             f'  author = {{{" and ".join(names)}}},', f'  {venue} = {{{paper["venue"]}}},',
             f'  year = {{{paper["year"]}}}']
    if paper.get('doi'):
        lines[-1] += ','
        lines.append(f'  doi = {{{paper["doi"]}}}')
    return '\n'.join(lines) + '\n}'


def paper_item(paper, filters=False, links=True):
    attrs = ''
    if filters:
        text = ' '.join(str(paper.get(k, '')) for k in ['title', 'authors', 'venue', 'year', 'highlight'])
        attrs = f' data-publication data-year="{paper["year"]}" data-type="{esc(paper["type"])}" data-search="{esc(text.lower())}"'
    url = 'https://doi.org/' + paper['doi'] if paper.get('doi') else 'https://scholar.google.com/scholar?q=' + quote(paper['title'])
    link_text = 'Paper ↗' if paper.get('doi') else 'Find on Scholar ↗'
    badge = f'<span class="pub-badge">{esc(paper["highlight"])}</span>' if 'Award' in paper.get('highlight', '') else ''
    actions = f'''<div class="pub-links"><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{link_text}</a>
      <details class="citation"><summary>BibTeX</summary><pre>{esc(bibtex(paper))}</pre><a href="/citations/{paper['id']}.bib" download>Download .bib ↓</a></details>{badge}</div>''' if links else ''
    return f'''<li class="publication"{attrs}><div class="pub-year">{paper['year']}</div><div>
      <h3 class="pub-title"><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(paper['title'])}</a></h3>
      <p class="pub-authors">{authors(paper['authors'])}</p>
      <p class="pub-meta"><span class="pub-venue">{esc(paper['venue'])}</span> · {esc(paper['details'])}</p>{actions}</div></li>'''


def navigation(page):
    items = [('About', '/#about', 'home'), ('Research', '/#research', ''), ('Publications', '/publications/', 'publications'), ('Talks', '/talks/', 'talks')]
    return ''.join(f'<a href="{url}"' + (' aria-current="page"' if key == page else '') + f'>{name}</a>' for name, url, key in items)


def shell(title, body, page='home', path='/', description=None):
    description = description or 'Yibin Wang · Research Associate at CUHK-Shenzhen. Bio-inspired magnetic micro- and nanorobots for biomedical applications.'
    structured = {'@context': 'https://schema.org', '@type': 'Person', 'name': PROFILE['name'], 'url': SITE_URL,
                  'jobTitle': PROFILE['role'], 'affiliation': {'@type': 'CollegeOrUniversity', 'name': PROFILE['institution']},
                  'sameAs': [PROFILE['scholar'], PROFILE['github']]}
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Yibin Wang</title><meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#176253"><link rel="canonical" href="{SITE_URL}{path}">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)} | Yibin Wang"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{SITE_URL}{path}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/academic.css">
<script type="application/ld+json">{json.dumps(structured)}</script><script src="/assets/academic.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="header-inner wrap"><a class="wordmark" href="/" aria-label="Yibin Wang home">Yibin Wang<span>.</span></a>
<button class="menu-toggle" aria-expanded="false" aria-controls="main-nav">Menu ☰</button><nav class="nav-links" id="main-nav" aria-label="Main navigation">{navigation(page)}<a class="nav-contact" href="/#contact">Contact ↗</a></nav></div></header>
<main id="main" class="wrap">{body}</main><div class="wrap"><section class="contact-band" id="contact" aria-labelledby="contact-title"><div><h2 id="contact-title">Let’s connect.</h2><p>Research, collaborations and academic enquiries.</p></div><a href="mailto:{PROFILE['email']}">{PROFILE['email']} ↗</a></section>
<footer class="site-footer"><span>© 2026 Yibin Wang · CUHK-Shenzhen</span><span>Last updated {PROFILE['updated']} · <a href="{PROFILE['github']}">GitHub ↗</a></span></footer></div></body></html>'''


def heading(number, title, link=''):
    return f'<div class="section-heading"><h2><span class="section-number">{number}</span>{title}</h2>{link}</div>'


def education():
    return ''.join(f'''<article class="education-entry"><div class="entry-meta">{esc(e['degree'])} · {esc(e['dates'])}</div><h3>{esc(e['institution'])}</h3><p>{esc(e['field'])}</p><p>{esc(e['detail'])}</p>''' +
                   (f'<p class="thesis">Thesis: {esc(e["thesis"])}</p>' if e.get('thesis') else '') + '</article>' for e in PROFILE['education'])


def awards():
    return ''.join(f'<article class="award"><time>{a["year"]}</time><div><h3>{esc(a["name"])}</h3><p>{esc(a["organization"])}</p></div></article>' for a in PROFILE['awards'])


def talks():
    return ''.join(f'<article class="talk"><time>{esc(t["date"])}</time><div><div class="status">{esc(t["status"])}</div><h2>{esc(t["title"])}</h2><p>{esc(t["event"])}</p><p>{esc(t["location"])}</p></div></article>' for t in PROFILE['talks'])


def home():
    body = f'''<section class="hero" id="about"><div><p class="eyebrow">Magnetic micro- and nanorobotics</p><h1>Yibin Wang</h1>
    <p class="role">Research Associate, Ph.D.</p><p class="affiliation">School of Science and Engineering<br>The Chinese University of Hong Kong, Shenzhen</p>
    <p class="intro">I develop <strong>bio-inspired magnetic micro- and nanorobots</strong> for biomedical applications.</p>
    <div class="hero-actions"><a class="button" href="#research">Explore my research <span>↘</span></a></div>
    <div class="profile-links"><a href="{PROFILE['scholar']}" target="_blank" rel="noopener noreferrer">Google Scholar ↗</a><a href="mailto:{PROFILE['email']}">Email ↗</a><a href="{PROFILE['github']}" target="_blank" rel="noopener noreferrer">GitHub ↗</a></div></div>
    </section>
    <section class="section" aria-labelledby="about-title"><h2 id="about-title" class="eyebrow">About me</h2><p class="home-bio">I am a Research Associate at <strong>The Chinese University of Hong Kong, Shenzhen</strong>, working with Prof. Jiangfan Yu. I received my Ph.D. in March 2026, following an M.S. from Carnegie Mellon University and a B.Eng. from Harbin Institute of Technology, Weihai.</p>
    <p class="home-bio">My research connects bio-inspired design, soft materials and magnetic actuation. I am interested in how miniature robots move, adapt and manipulate their surroundings, with applications in intravascular intervention, targeted delivery and image-guided therapy.</p></section>
    <section class="section" id="research">{heading('01 / RESEARCH', 'Magnetic Miniature Robots')}
    <p class="section-lead">From an individual soft structure to a coordinated swarm: designing motion and interaction at small scales.</p>
    <div class="research-grid"><article class="research-item"><div class="mini-art"><img src="/assets/research/magnetic-strider-v2.png" width="1610" height="977" loading="lazy" alt="Scientific schematic of the magnetic strider with four slender curved legs and a preload, take-off and flight sequence"></div><span class="research-tag">Structure & adaptation</span><h3>Bio-inspired<br>design</h3><p>Translating biological structures and motion into miniature robots with adaptive locomotion, targeted adhesion and shape-changing capabilities.</p><a class="text-link" href="https://doi.org/10.1002/advs.202207493">Magnetic strider ↗</a></article>
    <article class="research-item"><div class="mini-art"><img src="/assets/research/ciliavine-system-v2.png" width="1610" height="977" loading="lazy" alt="Scientific schematic of guidewire-mounted CiliaVine with flat helical cilia, open and closed configurations, and local flow regulation"></div><span class="research-tag">Intravascular applications</span><h3>Ciliated<br>robotic systems</h3><p>Magnetically actuated ciliated systems for intravascular flow regulation, targeted transport and biomedical manipulation.</p><a class="text-link" href="https://doi.org/10.1126/sciadv.aeg3333">Explore CiliaVine ↗</a></article>
    <article class="research-item"><div class="mini-art"><img src="/assets/research/vascular-microswarm-v2.png" width="1609" height="977" loading="lazy" alt="Scientific schematic of image-guided magnetic actuation and the injection, active exploration and vascular reconstruction workflow"></div><span class="research-tag">Collectives & navigation</span><h3>Magnetic<br>microrobot swarms</h3><p>Collective behavior for vascular network exploration, targeted delivery and biomedical manipulation.</p><a class="text-link" href="https://doi.org/10.1038/s42256-025-01012-y">Vascular exploration ↗</a></article></div>
    <p class="small-note">Schematic redrawings based on the linked publications.</p>
    <div class="featured-study"><div><span class="research-tag">Featured study · Science Advances, 2026</span><h3>CiliaVine: interacting<br>with biological flows.</h3><p>A ciliated soft millirobot integrates catheter delivery with magnetic actuation to enable particle transport, local clearance and surface enrichment.</p><a class="text-link" href="https://sse.cuhk.edu.cn/en/article/2370">Read the research story ↗</a></div><figure class="research-figure"><img src="/assets/ciliavine.png" width="554" height="221" loading="lazy" alt="CiliaVine research schematic showing catheter delivery, magnetic actuation and multimodal particle manipulation within a blood vessel"><figcaption><a href="https://doi.org/10.1126/sciadv.aeg3333">DOI: 10.1126/sciadv.aeg3333</a></figcaption></figure></div></section>
    <section class="section" id="publications">{heading('02 / PUBLICATIONS', 'Selected work', '<a href="/publications/">All publications →</a>')}
    <p class="section-lead">All first- and co-first-author publications.</p><ul class="pub-list">{''.join(paper_item(p) for p in PAPERS if p.get('selected'))}</ul><p class="small-note">† Equal contribution · * Corresponding author</p></section>
    <section class="section two-col"><div>{heading('03 / BACKGROUND', 'Education')}{education()}</div><div>{heading('04 / RECOGNITION', 'Honors & awards')}{awards()}</div></section>'''
    return shell('Magnetic micro- and nanorobotics', body)


def publications_page():
    years = sorted({p['year'] for p in PAPERS}, reverse=True)
    options = ''.join(f'<option value="{year}">{year}</option>' for year in years)
    body = f'''<header class="page-heading"><p class="eyebrow">Research output</p><h1>Publications</h1><p>Journal articles, conference papers and a book chapter on magnetic soft robotics, microrobot swarms and biomedical applications.</p><p class="small-note">† Equal contribution · * Corresponding author</p><a class="text-link" href="/citations/yibin-wang.bib" download>Download all citations (.bib) ↓</a></header>
    <section class="pub-page" aria-label="Publication list"><div class="filter-bar"><label class="search-wrap"><span class="skip">Search publications</span><input id="publication-search" type="search" placeholder="Search by title, author or journal…" aria-label="Search publications"></label><select id="year-filter" aria-label="Filter by year"><option value="">All years</option>{options}</select><select id="type-filter" aria-label="Filter by publication type"><option value="">All types</option><option>Journal</option><option>Conference</option><option>Book chapter</option></select></div>
    <p class="result-count" id="result-count" aria-live="polite">{len(PAPERS)} publications</p><ul class="pub-list">{''.join(paper_item(p, filters=True) for p in PAPERS)}</ul><p class="no-results" id="no-results" hidden>No publications match your search. Try another keyword or clear the filters.</p></section>'''
    return shell('Publications', body, 'publications', '/publications/')


def main():
    if len({p['id'] for p in PAPERS}) != len(PAPERS):
        raise ValueError('Publication IDs must be unique')
    for paper in PAPERS:
        for key in ['id', 'title', 'authors', 'year', 'type', 'venue', 'details']:
            if not paper.get(key):
                raise ValueError(f'Missing {key}: {paper}')
    # Only this generated directory is deployed; the original AcademicPages sources remain intact.
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(SOURCE / 'assets', OUT / 'assets', ignore=shutil.ignore_patterns(
        'magnetic-strider.png', 'ciliavine-system.png', 'vascular-microswarm.png'))
    shutil.copy2(ROOT / 'images/research/ciliavine.png', OUT / 'assets/ciliavine.png')
    pages = {'index.html': home(), 'publications/index.html': publications_page(),
             'talks/index.html': shell('Talks', '<header class="page-heading"><p class="eyebrow">Sharing research</p><h1>Talks & presentations</h1><p>Invited talks and conference presentations.</p></header><section class="pub-page">' + talks() + '</section>', 'talks', '/talks/')}
    for name, content in pages.items():
        target = OUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
    for alias, dest in {'about': '/', 'research': '/#research', 'portfolio': '/#research', 'teaching': '/#about', 'cv': '/#about', 'cv-json': '/#about', 'year-archive': '/', 'resume': '/#about'}.items():
        folder = OUT / alias
        folder.mkdir()
        (folder / 'index.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Yibin Wang</title><meta http-equiv="refresh" content="0;url={dest}"><link rel="canonical" href="{SITE_URL}{dest}"></head><body><a href="{dest}">Continue to Yibin Wang’s website</a></body></html>')
    citations = OUT / 'citations'
    citations.mkdir()
    for paper in PAPERS:
        (citations / f'{paper["id"]}.bib').write_text(bibtex(paper) + '\n')
    (citations / 'yibin-wang.bib').write_text('\n\n'.join(bibtex(p) for p in PAPERS) + '\n')
    (OUT / '.nojekyll').touch()
    (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')
    paths = ['/', '/publications/', '/talks/']
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{SITE_URL}{p}</loc></url>' for p in paths) + '</urlset>')
    (OUT / '404.html').write_text(shell('Page not found', '<section class="page-heading"><p class="eyebrow">404</p><h1>Page not found.</h1><p>This page may have moved.</p><a class="button" href="/">Back to home →</a></section>'))
    print(f'Built {len(pages)} pages and {len(PAPERS)} publications in {OUT}')


if __name__ == '__main__':
    main()
