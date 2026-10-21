#!/usr/bin/env python3
"""Check the deployable output, links, metadata and CV publication coverage."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
issues = []


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids, self.fragments = [], set(), []
        self.h1 = self.papers = self.canonical = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:
                issues.append(f'Duplicate ID: {a["id"]}')
            self.ids.add(a['id'])
        if tag == 'h1':
            self.h1 += 1
        if 'data-publication' in a:
            self.papers += 1
        if a.get('rel') == 'canonical':
            self.canonical += 1
        for key in ['href', 'src']:
            if a.get(key):
                self.links.append(a[key])
        if tag == 'img' and not a.get('alt'):
            issues.append('Image missing alt text')


pages = {}
for file in OUT.rglob('*.html'):
    if re.fullmatch(r'google[0-9a-f]+\.html', file.name):
        if file.read_text().strip() != f'google-site-verification: {file.name}':
            issues.append(f'Invalid Google verification file: {file}')
        continue
    parser = Page()
    parser.feed(file.read_text())
    pages[file] = parser
    if parser.canonical != 1:
        issues.append(f'Expected one canonical URL: {file}')
    if file.relative_to(OUT).as_posix() in ['index.html', 'publications/index.html', 'talks/index.html'] and parser.h1 != 1:
        issues.append(f'Expected one h1: {file}')
    for placeholder in ['Your Sidebar Name', 'Red Brick University', 'none@example.org', 'Paper Title Number', 'GitHub University']:
        if placeholder in file.read_text():
            issues.append(f'Unexpected template/private content: {file}: {placeholder}')
    if re.search(r'(?<![\w])(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)', file.read_text()):
        issues.append(f'Unexpected personal telephone number: {file}')

for file, page in pages.items():
    for link in page.links:
        parts = urlsplit(link)
        if parts.scheme or parts.netloc:
            continue
        path = unquote(parts.path)
        target = (OUT / path.lstrip('/')) if path.startswith('/') else (file.parent / path if path else file)
        if target.is_dir():
            target = target / 'index.html'
        if not target.exists():
            issues.append(f'Broken local link in {file}: {link}')
        elif parts.fragment and target in pages and parts.fragment not in pages[target].ids:
            issues.append(f'Missing anchor in {file}: {link}')

papers = json.loads((ROOT / 'site/data/publications.json').read_text())
if pages[OUT / 'publications/index.html'].papers != len(papers):
    issues.append('Publication page does not contain the full publication list')
if sum(p['type'] == 'Journal' for p in papers) != 19:
    issues.append('Expected 19 journal articles from the September 2026 CV')
for paper in papers:
    if paper['title'] not in (OUT / 'publications/index.html').read_text():
        issues.append(f'Missing publication: {paper["id"]}')
    if not (OUT / f'citations/{paper["id"]}.bib').is_file():
        issues.append(f'Missing BibTeX: {paper["id"]}')

if issues:
    raise SystemExit('\n'.join(issues))
print(f'PASS: {len(pages)} HTML pages; local links and anchors; metadata; {len(papers)} CV publications and citations; no template placeholders.')
