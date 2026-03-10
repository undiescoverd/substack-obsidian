# Substack → Obsidian Knowledge Base Generator

A complete solution to scrape Substack publications and automatically create a structured Obsidian vault with all content.

## What It Does

- **Scrapes** all articles from a Substack publication (using RSS feed or API)
- **Converts** HTML content to clean Markdown
- **Generates** individual article notes with metadata
- **Creates** an indexed knowledge base ready for Obsidian
- **Preserves** publication info, dates, authors, and tags
- **Supports** inter-note linking with Obsidian's `[[wiki-link]]` syntax

## Installation

### 1. Install Python Dependencies

```bash
# Core requirements
pip install requests --break-system-packages

# Recommended (for better HTML parsing)
pip install feedparser beautifulsoup4 --break-system-packages

# Optional (for better HTML to Markdown conversion)
pip install html2text --break-system-packages
```

### 2. Get the Script

Download or copy `substack_scraper.py` to your computer.

## Quick Start

### Basic Usage

```bash
python substack_scraper.py https://example.substack.com
```

This creates a folder called `substack_vault` with all articles.

### Custom Output Directory

```bash
python substack_scraper.py https://example.substack.com -o ~/my_vaults/newsletter
```

### Fetch Full Content (slower but more complete)

```bash
python substack_scraper.py https://example.substack.com --full-content
```

## How It Works

### Step 1: Scraping
The script tries multiple methods in order:
1. **RSS Feed** (fastest, most reliable) - scrapes the public RSS feed
2. **API** (fallback) - uses Substack's API endpoints

### Step 2: Content Processing
- Extracts title, author, date, content, and tags
- Converts HTML to Markdown
- Cleans up formatting

### Step 3: File Generation
Creates a structured vault:
```
substack_vault/
├── INDEX.md                 (Main entry point)
├── metadata.json            (All article data)
└── articles/
    ├── Article_Title_1.md
    ├── Article_Title_2.md
    └── ...
```

### Step 4: Obsidian Integration
Each article includes:
- **Frontmatter** with metadata (YAML)
- **Clean markdown content**
- **Backlinks** to related topics and tags
- **Source link** to original article

## File Structure & Format

### Example Article File

```markdown
---
title: How to Build Better Systems
subtitle: A practical guide
author: Jane Doe
date: 2024-01-15
url: https://example.substack.com/p/article-slug
tags: ["systems", "engineering", "productivity"]
---

## How to Build Better Systems

*A practical guide*

**Published:** 2024-01-15
**Author:** Jane Doe

**Source:** [How to Build Better Systems](https://example.substack.com/p/article-slug)

---

# Article content here...

## Related Topics

- [[systems]]
- [[engineering]]
- [[productivity]]
```

### INDEX.md

Central hub with:
- Publication metadata
- List of recent articles
- Complete article index with dates
- Quick navigation

### metadata.json

Raw data export containing:
- All article information
- Timestamps
- Original URLs
- Useful for processing, backup, or analysis

## Using in Obsidian

### Step 1: Create Vault

1. Open Obsidian
2. Click "Create new vault"
3. Choose "Store in a folder on my computer"
4. Navigate to your `substack_vault` folder
5. Name your vault (e.g., "Newsletter Knowledge Base")
6. Click "Create"

### Step 2: Explore

1. Obsidian opens with the vault loaded
2. Click on `INDEX.md` in the left sidebar
3. Browse articles using the links
4. Click any `[[wiki-link]]` to jump to related notes

### Step 3: Enhance

Now you can:
- **Add notes** to topics you want to explore deeper
- **Create new links** between concepts
- **Use tags** for searching and filtering
- **Export or publish** your notes later
- **Set up periodic updates** (see below)

## Advanced Usage

### Automating Updates

Create a script to periodically update your vault:

```bash
#!/bin/bash
# update_vault.sh

PUBLICATION="https://example.substack.com"
VAULT_DIR="$HOME/Obsidian Vaults/Newsletter"

cd "$VAULT_DIR"
python substack_scraper.py "$PUBLICATION" -o .

# Optionally sync to your preferred cloud storage
# cp -r articles ~/Dropbox/MyVault/
```

Run with cron:
```bash
0 9 * * * /path/to/update_vault.sh  # Daily at 9 AM
```

### Processing JSON Metadata

The `metadata.json` file contains all article data. Process it with Python:

```python
import json

with open('substack_vault/metadata.json') as f:
    data = json.load(f)

for article in data['articles']:
    print(f"{article['title']} - {article['date']}")
    # Process further...
```

### Custom Markdown Generation

Modify the `create_markdown_file()` method to customize output format:

```python
def create_markdown_file(self, article: Dict) -> str:
    # Add your custom formatting here
    # For example: different frontmatter, custom sections, etc.
    pass
```

### Batch Processing Multiple Publications

```python
from substack_scraper import SubstackScraper

publications = [
    "https://publication1.substack.com",
    "https://publication2.substack.com",
    "https://publication3.substack.com",
]

for pub in publications:
    scraper = SubstackScraper(pub, f"./vaults/{pub.split('.')[0]}")
    scraper.scrape()
    scraper.generate()
    print(f"✓ Completed {pub}")
```

## Troubleshooting

### "No articles found"

**Problem:** The scraper couldn't retrieve articles.

**Solutions:**
1. Check the URL format (should be `https://name.substack.com`)
2. Verify the Substack publication is public
3. Check your internet connection
4. Try with `--full-content` flag
5. Verify the publication has published articles

### "Failed to create file: [Error]"

**Problem:** Issue writing markdown files.

**Solutions:**
1. Ensure the output directory is writable
2. Check disk space
3. Verify no special characters in article titles
4. Run with a different output directory

### HTML content looks wrong

**Problem:** Markdown content is malformed.

**Solutions:**
1. Install `html2text` for better conversion: `pip install html2text`
2. Some formatting may not convert perfectly - you can manually fix in Obsidian
3. Use the source URL in the article to verify original formatting

### Rate limiting

**Problem:** Requests are failing with 429 errors.

**Solutions:**
1. Add delays between requests (script already includes some)
2. Don't use `--full-content` flag (slower but respects rate limits better)
3. Scrape during off-peak hours
4. Respect Substack's terms of service

## Tips & Best Practices

### For Large Publications

- Don't try to scrape 10,000+ articles at once - Substack may rate limit
- Scrape in batches or focus on date ranges
- Use `metadata.json` to track what you've already scraped

### For Regular Updates

- Keep a backup of your current vault
- Run updates during off-hours
- Version control your vault (push to GitHub private repo)

### Organizing Your Vault

After scraping, enhance with:

```
substack_vault/
├── INDEX.md
├── articles/
├── topics/              # Create this
│   ├── Systems.md
│   ├── Engineering.md
│   └── ...
├── reading-list/        # Create this
│   └── To Read.md
└── metadata.json
```

### Search in Obsidian

Use Obsidian's search features:
- `Ctrl+Shift+F` / `Cmd+Shift+F` to search all files
- Use tags: `#tag-name`
- Filter by date: look at article metadata
- Create saved searches for frequent queries

## API Reference

### SubstackScraper Class

```python
from substack_scraper import SubstackScraper

# Initialize
scraper = SubstackScraper(
    publication_url="https://example.substack.com",
    output_dir="./my_vault"
)

# Scrape articles
articles = scraper.scrape()

# Generate files
scraper.generate()

# Access articles
for article in scraper.articles:
    print(article['title'], article['date'])
```

### Methods

- `scrape()` - Fetch all articles
- `generate()` - Create markdown files
- `scrape_via_rss()` - Use RSS feed
- `scrape_via_api()` - Use Substack API
- `create_markdown_file(article)` - Generate single file
- `generate_index()` - Create INDEX.md
- `save_metadata()` - Save JSON metadata

## Limitations

- **Public content only** - Can only scrape publicly available articles
- **No paywalled content** - Paid-only articles won't be included
- **Formatting** - Some complex HTML formatting may not convert perfectly
- **Images** - Links to images are preserved, images themselves not downloaded (can be customized)
- **Rate limiting** - Substack may rate limit aggressive scraping

## Terms of Service

Before scraping:
- ✓ Respect Substack's Terms of Service
- ✓ Only archive content you have permission to use
- ✓ Consider reaching out to authors if scraping large amounts
- ✓ Use for personal knowledge management only
- ✓ Give credit to original authors

## Customization Examples

### Add Images to Notes

Modify `create_markdown_file()` to download images:

```python
def download_image(url, article_dir):
    response = requests.get(url)
    filename = url.split('/')[-1]
    path = article_dir / filename
    with open(path, 'wb') as f:
        f.write(response.content)
    return f"![image]({filename})"
```

### Change Frontmatter Format

```python
frontmatter = f"""# {article['title']}

author:: {article['author']}
date:: {article['date']}
source:: {article['url']}
type:: article
"""
```

### Filter Articles by Date

```python
from datetime import datetime, timedelta

scraper = SubstackScraper(url, output_dir)
scraper.scrape()

# Only keep articles from last 90 days
cutoff = datetime.now() - timedelta(days=90)
scraper.articles = [
    a for a in scraper.articles 
    if datetime.fromisoformat(a['date']) > cutoff
]

scraper.generate()
```

## Support & Contributing

Found a bug or have suggestions? The script is modular and extensible:

1. **Add new scraping methods** - Extend `scrape_via_*()` methods
2. **Change output format** - Modify markdown generation
3. **Add new features** - Extend the class with new methods
4. **Submit improvements** - Share customizations with others

## License

Use freely for personal knowledge management and learning.

---

**Questions?** Check the code comments or modify to suit your needs!
