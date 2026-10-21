# Academic website

## Repository selection

- Active project: `ebeame/ebeame.github.io`, default branch `master`, last existing commit `17e88fc` (5 May 2026, UTC+8).
- Earlier project: `ebeame/ebeame_pre.github.io`, last existing commit `869d8db` (12 April 2026, UTC+8); contains only a README.
- Publication branch: `publish-academic-homepage`; the local drafting history is retained on `improve-academic-homepage`.

## Content

- `site/data/profile.json`: affiliation, education, honors, teaching, peer review and talks.
- `site/data/publications.json`: 19 journal articles, 2 conference papers and 1 book chapter. Set `selected: true` to feature a paper on the homepage.
- `scripts/build_academic_site.py`: page structure and standard-library static generator.
- `site/assets/research/`: three original ImageGen concept illustrations used by the Research cards.
- `site/data/research-image-prompts-v2.json`: current prompt set, generation tool, source papers and original figure references; the earlier prompt set is retained for reference.
- `site/assets/academic.css`: typography and responsive layout.
- `site/assets/academic.js`: mobile navigation, publication search and filters.
- `images/research/ciliavine.png`: research illustration from the author's CUHK-Shenzhen school news article; the visible caption links to the paper DOI, with the original image source recorded below.

The content was transcribed from the author's September 2026 CV, located through the PostDoc project's other conversations. Degree fields were retained from the existing academic homepage. The Google Scholar URL was supplied by the author. The homepage includes all first-author and co-first-author papers identified in the CV (8 journal articles and 1 conference paper). The original CV PDF is not deployed. Its telephone number is not included in the public website.

Primary research sources:

- [CiliaVine: CUHK-Shenzhen research news](https://sse.cuhk.edu.cn/en/article/2370)
- [CiliaVine paper](https://doi.org/10.1126/sciadv.aeg3333)
- [Blood flow regulation paper](https://doi.org/10.1038/s41551-026-01771-y)
- [Swarm autonomy paper](https://doi.org/10.1002/adma.202312956)

No photograph was available in the existing repository: `images/profile.png` is the template silhouette, so it is not used. The Research card images were generated with the built-in ImageGen tool and depict, respectively, a four-legged water-strider-inspired magnetoelastic jumping robot (Advanced Science, 2023, DOI 10.1002/advs.202207493), the guidewire-mounted CiliaVine system (Science Advances, 2026, DOI 10.1126/sciadv.aeg3333), and magnetic nanoparticle swarms for vascular network exploration and reconstruction (Nature Machine Intelligence, 2025, DOI 10.1038/s42256-025-01012-y). All original illustrations are explicitly conceptual and do not represent experimental results.

## Build and preview

Requires Python 3.9 or newer; no pip, npm, Ruby, Jekyll or third-party dependencies.

```bash
python3 scripts/build_academic_site.py
python3 scripts/check_academic_site.py
python3 -m http.server 8765 --bind 127.0.0.1 --directory dist
```

The site is written to `dist/`, which is generated and ignored by Git. Only this folder is published. The original AcademicPages layout, sample content and files are retained in the repository but are excluded from the published output.

The generated public routes are `/`, `/publications/` and `/talks/`. No CV page, CV download or CV print action is published; previous CV and resume routes redirect to the homepage. Common previous routes redirect to the corresponding new page. Citations can be expanded in the publication list or downloaded individually and as one `.bib` file. Articles without a verified DOI use a title search on Google Scholar.

## GitHub Pages

The `.github/workflows/academic-pages.yml` workflow builds and validates the site, uploads `dist/`, and deploys it with GitHub Pages. It runs on pushes to `master` and supports manual dispatch.

For the first deployment, set the repository's **Settings → Pages → Build and deployment → Source** to **GitHub Actions**. Merge this branch into `master` or run the workflow manually on this branch after the source is set. The production address is `https://ebeame.github.io/`.

This URL identifies the intended destination; deployment is confirmed only after the workflow succeeds. Do not publish the repository root as a static artifact: it contains the retained template sources.

## Verification

`scripts/check_academic_site.py` validates all generated local links, anchors, canonical URLs, image descriptions, publication coverage, citation files, and absence of known template placeholders and the CV telephone number.

Browser checks performed locally: responsive navigation, publication text search, empty search state, 2026 year filter (4 results), and BibTeX expansion. The original source CV and repository were used as the content references. External publisher availability is outside the local link checker.

## Pending publication detail

The author asked to update the homepage GitHub link after publication. Retain the existing genuine GitHub profile URL until a final deployment address is confirmed; then update the link and its label to match the destination.

## Research illustrations, second version

The Research cards now use `magnetic-strider-v2.png`, `ciliavine-system-v2.png` and `vascular-microswarm-v2.png`. These were redrawn with built-in ImageGen using the actual Figure 1 of each published paper as image input. The strider reference was retrieved from the official PMC open dataset; the CiliaVine and swarm references were rendered from the author’s locally stored published PDFs. Previous artwork is retained in the source repository. Website output includes only the second version. The new scientific schematics use contained sizing to preserve mechanisms and labels on mobile.

The homepage hero illustration, its caption and paper link, and the introductory IROS award banner were removed at the author’s request. The hero now uses a text-only single-column layout. The Research section heading is “Magnetic Miniature Robots”. The awards section and the three research images remain.
