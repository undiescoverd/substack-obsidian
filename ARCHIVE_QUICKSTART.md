# Scraping Ruben's Substack - 2026 Articles Only

## What This Does

This specialized scraper:
- ✅ Scrapes the Substack archive page
- ✅ Fetches all article details (content, dates, metadata)
- ✅ **Filters to only 2026 articles automatically**
- ✅ Creates a beautiful Obsidian vault
- ✅ Generates an indexed knowledge base

Perfect for capturing this year's content in one shot!

---

## Installation (2 minutes)

```bash
# Install required dependencies
pip install requests beautifulsoup4 --break-system-packages

# Verify installation
python -c "import requests, bs4; print('✓ Ready to go!')"
```

---

## Usage (1 command)

### Scrape Ruben's 2026 Articles

```bash
python substack_archive_scraper.py "https://ruben.substack.com/archive?sort=new"
```

That's it! It will:
1. Load the archive page
2. Find all articles
3. Fetch each article's content
4. **Filter to 2026 only**
5. Create a vault in `./substack_vault`

### Custom Output Location

```bash
python substack_archive_scraper.py "https://ruben.substack.com/archive?sort=new" -o ~/My_Vaults/rubens_2026
```

### Filter Different Year

```bash
# Get 2025 articles instead
python substack_archive_scraper.py "https://ruben.substack.com/archive?sort=new" -y 2025

# Get 2024 articles
python substack_archive_scraper.py "https://ruben.substack.com/archive?sort=new" -y 2024
```

---

## What You Get

```
substack_vault/
├── INDEX.md                    ← Start here (see all articles)
├── articles/
│   ├── Article_Title_1.md     ← Each article as a note
│   ├── Article_Title_2.md
│   └── ...                     ← One markdown file per article
└── metadata.json               ← Raw data (backup/analysis)
```

### Each Article Contains

```markdown
# Article Title

*Subtitle if available*

**Published:** 2025-01-15
**Author:** Author Name
**Read original:** [Link to Substack]

---

# Full article content here (clean Markdown)

## Topics
- #topic1
- #topic2
```

### INDEX.md Shows

```markdown
# ruben - 2025 Archive

**Total Articles:** 24

## Articles by Date (Newest First)

### Article Title 1
**2025-01-20**
> Optional subtitle

### Article Title 2
**2025-01-18**

...
```

---

## Opening in Obsidian

### First Time

1. Open **Obsidian**
2. Click **"Create new vault"**
3. Select **"Store in a folder on my computer"**
4. Choose the **`substack_vault`** folder that was created
5. Name it (e.g., "Rubens Newsletter")
6. Click **Create**

### Using Your Vault

- **Navigate** using the sidebar folder tree
- **Open INDEX.md** to see all articles chronologically
- **Click any file** to read the full article
- **Search** with `Ctrl+Shift+F` (Windows) or `Cmd+Shift+F` (Mac)
- **Use tags** like `#topic` to filter articles

---

## Troubleshooting

### "Failed to fetch archive page"
- Check the URL is correct: `https://ruben.substack.com/archive?sort=new`
- Verify you have internet connection
- Try again (might be temporary network issue)

### "No articles from 2025 found"
- The scraper filtered out articles from other years
- Try with `-y 2024` to get previous year's articles
- Or remove the year filter to see what was found

### "BeautifulSoup4 not found"
```bash
pip install beautifulsoup4 --break-system-packages
```

### Articles look incomplete
- Some styling may not convert perfectly HTML → Markdown
- Click the "Read original" link to see full formatting
- The content is preserved, just styling is minimal

---

## Advanced: Scrape Multiple Years

```python
#!/usr/bin/env python3
from substack_archive_scraper import SubstackArchiveScraper

url = "https://ruben.substack.com/archive?sort=new"

for year in [2026, 2025, 2024]:
    print(f"\nScraping {year}...")
    scraper = SubstackArchiveScraper(url, f"./rubens_{year}", year)
    scraper.scrape()
    scraper.generate()
```

Save as `scrape_multiple_years.py` and run:
```bash
python scrape_multiple_years.py
```

---

## Understanding the Output

### metadata.json

Contains all raw article data:
```json
{
  "archive_url": "https://ruben.substack.com/archive?sort=new",
  "publication_name": "ruben",
  "year_filter": 2026,
  "scraped_at": "2026-03-10T15:30:00",
  "total_articles": 24,
  "articles": [
    {
      "title": "Article Title",
      "date": "2026-01-20",
      "author": "Ruben",
      "url": "https://...",
      "content": "HTML content here",
      "tags": ["ai", "tech"]
    },
    ...
  ]
}
```

Use this for:
- Backup/archival
- Data analysis (stats, word counts, etc.)
- Re-importing into other tools
- Verifying article data

---

## Time Expectations

| Task | Time |
|------|------|
| Install dependencies | 1 minute |
| Scrape archive page | 30 seconds |
| Fetch 20 articles | 20-30 seconds (1 sec per article) |
| Generate markdown files | 5 seconds |
| **Total** | **~2 minutes** |

---

## Next Steps

Once you have the vault open in Obsidian:

1. **Read through the articles** using INDEX.md
2. **Create topic notes** linking related articles
3. **Add your own thoughts** to each article
4. **Organize by theme** (create folders for topics)
5. **Build a knowledge graph** by linking concepts

Example structure to add:
```
substack_vault/
├── articles/          (auto-generated)
├── topics/            (you create)
│   ├── AI & ML.md
│   ├── Technology.md
│   └── Future Trends.md
├── my-notes/          (you create)
│   └── Reading Notes.md
└── INDEX.md
```

---

## Pro Tips

💡 **Search effectively** - Use Obsidian's search (`Ctrl+Shift+F`) to find articles by keyword

💡 **Use tags** - Articles include tags (e.g., `#ai`), searchable in Obsidian

💡 **Create quick notes** - Right-click in sidebar → "New note" to capture ideas while reading

💡 **Link ideas** - Use `[[Article Name]]` to create connections between concepts

💡 **Export later** - If you want to share your notes, Obsidian can export to HTML, PDF, etc.

---

## Command Reference

```bash
# Basic usage
python substack_archive_scraper.py "ARCHIVE_URL"

# All options
python substack_archive_scraper.py "ARCHIVE_URL" \
  -y 2026 \                    # Year to filter (default: 2026)
  -o ./vault                   # Output directory (default: ./substack_vault)

# Help
python substack_archive_scraper.py -h
```

---

## Need to Scrape Again?

If you want to add more articles later:

```bash
# Option 1: Overwrite existing vault
python substack_archive_scraper.py "https://ruben.substack.com/archive?sort=new"

# Option 2: Create separate vault for new articles
python substack_archive_scraper.py "https://ruben.substack.com/archive?sort=new" -o ./rubens_2026_updated
```

---

**Ready?** Run:
```bash
python substack_archive_scraper.py "https://ruben.substack.com/archive?sort=new"
```

Your vault will be created in seconds! 🚀
