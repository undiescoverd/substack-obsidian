# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Python scraper suite that converts Substack newsletters into Obsidian vaults (markdown files with YAML frontmatter and `[[wiki-links]]`).

## Key Commands

```bash
# Install dependencies
pip install -r requirements.txt --break-system-packages

# Run archive scraper (primary code path)
python3 substack_archive_scraper.py "https://example.substack.com/archive?sort=new"
python3 substack_archive_scraper.py "https://example.substack.com/archive" -y 2025
python3 substack_archive_scraper.py "https://example.substack.com/archive" --start-date 2025-01-01 --end-date 2025-12-31 -o ./my_vault

# Scrape with paid content access (cookie from browser DevTools → substack.sid)
python3 substack_archive_scraper.py "https://example.substack.com/archive" --cookie YOUR_SID_VALUE
# Or via environment variable:
SUBSTACK_COOKIE=YOUR_SID_VALUE python3 substack_archive_scraper.py "https://example.substack.com/archive"

# Run general scraper (secondary, no date filtering)
python3 substack_scraper.py "https://example.substack.com" -o ./vault --full-content

# Run Streamlit UI
streamlit run scraper_ui.py

# No test suite exists — verify manually by re-scraping and inspecting output files
```

## Architecture

Two independent scrapers share no code:

- **`substack_archive_scraper.py`** — Primary scraper. `SubstackArchiveScraper` class with API-first fetch (paginated `/api/v1/archive`), HTML fallback, year/date-range filtering, and author-subfolder organization. HTML-to-markdown uses a 3-phase pipeline: `_preprocess_html()` (BeautifulSoup DOM cleanup) → `SubstackMarkdownConverter` (markdownify with custom handlers for figures/captions/images/code) → `_postprocess_markdown()` (wiki-link restoration, whitespace normalization).

- **`substack_scraper.py`** — General-purpose scraper. RSS-first with API fallback, no date filtering, flat file structure, regex-based HTML conversion. Not the primary code path — left unchanged during recent improvements.

- **`scraper_ui.py`** — Streamlit UI wrapping the archive scraper. Handles URL normalization (including `substack.com/@username` reader URLs), date pickers, progress logging, and zip download.

## Data Flow

`URL → API fetch (paginated) → filter by year/date → fetch article HTML → preprocess DOM → markdownify → postprocess → write .md files + metadata.json`

Output vault structure: `substack_vault/articles/{Author_Name}/{Article_Title}.md`

Each article has YAML frontmatter (title, subtitle, author, date, url, tags) and internal Substack cross-references converted to `[[wiki-links]]` via slug matching.

## Key Patterns

- **Wiki-links**: Internal Substack `/p/slug` links are converted to `[[slug]]` when the slug exists in the current scrape's article set. The archive scraper uses a null-byte placeholder (`\x00WIKI[slug]\x00`) during preprocessing to survive the markdownify pass.
- **Rate limiting**: 0.5s between API pages, 1s between article fetches.
- **Date normalization**: `normalize_date()` handles ISO datetimes, `YYYY-MM-DD`, and natural date strings (`Jan 15, 2025`).
- **Widget removal**: Substack injects subscription/share widgets that produce orphan text — these are decomposed in preprocessing and stripped in postprocessing as belt-and-suspenders.
- **Authentication**: Paid/subscriber-only content requires a `substack.sid` session cookie. Pass via `--cookie` CLI arg or `SUBSTACK_COOKIE` env var. The cookie is set on `.substack.com` domain and propagates to all requests via the session cookie jar — no per-request changes needed.

## Obsidian Compatibility — Critical Rules

The output markdown must be valid for Obsidian's renderer. Violations here break image rendering and document display:

- **Escape `$$` sequences**: Obsidian treats `$$` as LaTeX display math. If `$$` appears in article text (e.g. `$$$`) without a closing `$$`, it corrupts ALL rendering after it — images show as raw `![]()` text instead of loading. The postprocessor escapes `$$+` to `\$\$+` via regex.
- **Strip CDN signature tokens**: Substack injects `$s_!...!,` tokens into `substackcdn.com` image URLs. These are unnecessary (CDN serves images without them) and make URLs ugly. Stripped in `_preprocess_html()`.
- **Unwrap image link wrappers**: Substack wraps images in `<a href="substackcdn..."><div class="image2-inset"><img></div></a>`. Without unwrapping, markdownify produces nested `[![](img)](link)` which is noisy. Preprocessing removes `div.image2-inset`, `div.image-link-expand`, and unwraps `<a>` tags linking to `substackcdn.com/image`.
- **Images on single lines**: `![](url)` MUST be on one unbroken line — if the `![]` and `(url)` are split across lines, Obsidian renders raw text instead of an image. The custom `convert_img()` in `SubstackMarkdownConverter` handles this.
- **Single article mode**: URLs with `/p/` are detected as single articles. The UI auto-hides date pickers and the scraper skips archive pagination.
