# Archive Scraper - Advanced Tips & Troubleshooting

## How the Archive Scraper Works

```
┌─────────────────────────────────────┐
│   Substack Archive Page             │
│   (https://...com/archive?sort=new) │
└────────────────┬────────────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │  Parse HTML        │
        │  Find article      │
        │  links on page     │
        └────────┬───────────┘
                 │
                 ▼
     ┌───────────────────────────┐
     │  For each article:        │
     │  - Fetch full content     │
     │  - Extract date           │
     │  - Extract author         │
     │  - Extract metadata       │
     └────────────┬──────────────┘
                  │
                  ▼
      ┌──────────────────────────┐
      │  Filter by year (2025)   │
      │  Keep only matching      │
      │  articles                │
      └────────────┬─────────────┘
                   │
                   ▼
      ┌─────────────────────────────┐
      │  Generate Markdown files    │
      │  Create INDEX.md            │
      │  Save metadata.json         │
      └─────────────────────────────┘
                   │
                   ▼
          ┌────────────────┐
          │  Obsidian Vault│
          │  Ready to use! │
          └────────────────┘
```

## Performance & Rate Limiting

### How Fast Does It Scrape?

- Archive page: **~1 second**
- Per article fetch: **~1-2 seconds** (includes respectful 1-second delay)
- 20 articles: **~20-40 seconds total**

The 1-second delay between requests is **intentional** - it's respectful to Substack's servers.

### Adjusting Speed (Be Careful!)

To make it faster, you can reduce the delay:

```python
# In substack_archive_scraper.py, find this line:
time.sleep(1)  # Respectful rate limiting

# Change to:
time.sleep(0.5)  # 500ms delay instead
```

**Caution:** Reducing delays too much may:
- Get you rate limited (429 errors)
- Be less respectful to Substack's infrastructure
- Risk IP bans

**Recommendation:** Keep it at 1 second or higher.

---

## Common Issues & Solutions

### Issue: "Connection timed out"

**Cause:** Network issue or Substack server temporarily down

**Solutions:**
1. Try again in a few minutes
2. Check your internet connection
3. Try a different network (if behind corporate firewall)

### Issue: "No articles from 2025 found"

**Cause:** Date parsing might have failed

**Debug:**
1. Check `metadata.json` - look at the `date` field
2. Run with `-y 2024` to see if you get results
3. Check if dates are in unexpected format

**Solution:**
```python
# In substack_archive_scraper.py, modify the date parsing:

# Find this section:
for fmt in ['%B %d, %Y', '%b %d, %Y', '%Y-%m-%dT%H:%M:%S']:

# Add more date formats if needed:
for fmt in [
    '%B %d, %Y',           # January 15, 2025
    '%b %d, %Y',           # Jan 15, 2025
    '%Y-%m-%dT%H:%M:%S',   # 2025-01-15T10:30:00
    '%m/%d/%Y',            # 01/15/2025
    '%d-%m-%Y',            # 15-01-2025
]:
```

### Issue: "Content looks incomplete or garbled"

**Cause:** HTML to Markdown conversion might be missing some elements

**Debug:**
1. Check `metadata.json` - view raw HTML content
2. Visit the original article URL to compare
3. Check specific article markdown file

**Solution:**
```python
# Install better HTML-to-Markdown converter:
pip install html2text --break-system-packages

# Then modify substack_archive_scraper.py:
import html2text

def html_to_markdown(self, html_content: str) -> str:
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0  # Don't wrap text
    return h.handle(html_content)
```

### Issue: "BeautifulSoup can't find articles"

**Cause:** HTML structure changed or article links are in unexpected location

**Debug:**
1. Visit the archive URL in browser
2. Right-click → "Inspect" → Find article link
3. Check what CSS class/selector it uses

**Solution:**
```python
# Modify the article link selector in parse_archive_page():

# Current (works for most cases):
article_elements = soup.find_all('a', {'href': re.compile(r'/p/[a-zA-Z0-9-]+')})

# If that doesn't work, try:
article_elements = soup.find_all('a', {'class': 'some-class-name'})

# Or search by text content:
article_elements = [
    a for a in soup.find_all('a') 
    if '/p/' in a.get('href', '')
]
```

---

## Customization Examples

### 1. Skip Certain Articles

```python
# In scrape() method, after fetching articles:

# Filter out articles with certain words in title
exclude_keywords = ['announcement', 'housekeeping', 'off-topic']
self.articles = [
    a for a in self.articles
    if not any(kw.lower() in a['title'].lower() for kw in exclude_keywords)
]

print(f"Filtered to {len(self.articles)} articles")
```

### 2. Only Get Articles from Specific Month

```python
# In scrape() method, after fetching articles:

from datetime import datetime

# Only articles from January 2025
self.articles = [
    a for a in self.articles
    if a.get('date') and a['date'].startswith('2025-01')
]
```

### 3. Add Custom Metadata

```python
# In fetch_article_details(), after extracting article info:

# Add word count
word_count = len(article['content'].split())
article['word_count'] = word_count

# Add estimated reading time
reading_time_minutes = max(1, word_count // 200)
article['reading_time'] = f"{reading_time_minutes} min read"

# Add AI relevance score (example)
ai_keywords = ['ai', 'machine learning', 'llm', 'neural', 'model']
title_lower = article['title'].lower()
article['ai_score'] = sum(1 for kw in ai_keywords if kw in title_lower)
```

### 4. Save Articles by Category

```python
# Group articles by theme in INDEX.md

def generate_index(self):
    """Generate index organized by theme."""
    
    # Categorize articles
    categories = {
        'AI & ML': [],
        'Business': [],
        'Technology': [],
        'Other': []
    }
    
    for article in self.articles:
        title_lower = article['title'].lower()
        if any(word in title_lower for word in ['ai', 'ml', 'machine', 'neural']):
            categories['AI & ML'].append(article)
        elif any(word in title_lower for word in ['business', 'startup', 'market']):
            categories['Business'].append(article)
        elif any(word in title_lower for word in ['tech', 'software', 'code']):
            categories['Technology'].append(article)
        else:
            categories['Other'].append(article)
    
    # Generate index with categories
    index = "# Articles by Category\n\n"
    
    for category, articles in categories.items():
        if articles:
            index += f"## {category} ({len(articles)})\n\n"
            for article in articles:
                safe_title = self.sanitize_filename(article['title'])
                index += f"- [[{safe_title}]] - {article['date']}\n"
            index += "\n"
    
    with open(self.index_file, 'w') as f:
        f.write(index)
```

### 5. Extract Key Insights from Each Article

```python
# In create_markdown_file(), before the "Topics" section:

# Extract quotes/highlights
import re

def extract_blockquotes(html):
    """Extract all blockquotes from HTML."""
    pattern = r'<blockquote[^>]*>(.*?)</blockquote>'
    matches = re.findall(pattern, html, re.DOTALL)
    return [re.sub(r'<[^>]+>', '', m).strip() for m in matches[:3]]

blockquotes = extract_blockquotes(article.get('content', ''))

if blockquotes:
    full_content += "\n\n## Key Quotes\n\n"
    for i, quote in enumerate(blockquotes, 1):
        full_content += f"{i}. > {quote}\n\n"
```

---

## Analyzing Your Scraped Data

### Using metadata.json

```python
import json
from collections import Counter

# Load metadata
with open('substack_vault/metadata.json') as f:
    data = json.load(f)

articles = data['articles']

# Statistics
print(f"Total articles: {len(articles)}")

# Most common authors
authors = Counter(a['author'] for a in articles)
print(f"\nTop authors:")
for author, count in authors.most_common(5):
    print(f"  {author}: {count}")

# Article lengths
lengths = [len(a.get('content', '')) for a in articles]
print(f"\nAverage article length: {sum(lengths)//len(lengths)} characters")

# Most common tags
from itertools import chain
all_tags = list(chain.from_iterable(a.get('tags', []) for a in articles))
tags = Counter(all_tags)
print(f"\nMost common tags:")
for tag, count in tags.most_common(10):
    print(f"  {tag}: {count}")
```

---

## Scheduling Regular Updates

### Windows Task Scheduler

Create `update_substack.bat`:
```batch
@echo off
cd C:\path\to\vault\directory
python substack_archive_scraper.py "https://ruben.substack.com/archive?sort=new" -y 2025
pause
```

Then:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, weekly, etc.)
4. Set action to run the `.bat` file

### macOS/Linux Cron

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/vault && python3 substack_archive_scraper.py "https://ruben.substack.com/archive?sort=new" -y 2025
```

---

## Exporting Your Vault

### To HTML (for sharing)

```python
# Use Obsidian's built-in "Export" feature
# Or install markdown-to-html converters
pip install markdown --break-system-packages

# Then:
import markdown

for md_file in article_dir.glob("*.md"):
    with open(md_file) as f:
        html = markdown.markdown(f.read())
    with open(md_file.with_suffix('.html'), 'w') as f:
        f.write(html)
```

### To PDF

```bash
# Install wkhtmltopdf first, then use it with a Python wrapper
pip install pdfkit --break-system-packages

# Script to convert all to PDF
```

### To CSV (for analysis)

```python
import csv

with open('articles.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Title', 'Date', 'Author', 'Length', 'Tags', 'URL'])
    
    for article in articles:
        writer.writerow([
            article['title'],
            article['date'],
            article['author'],
            len(article.get('content', '')),
            '; '.join(article.get('tags', [])),
            article['url']
        ])
```

---

## Troubleshooting Network Issues

### Check Connection

```python
import requests

def test_connection():
    try:
        response = requests.get('https://ruben.substack.com', timeout=5)
        if response.status_code == 200:
            print("✓ Connection OK")
        else:
            print(f"✗ Got status {response.status_code}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")

test_connection()
```

### Using Proxy

If you need a proxy:

```python
# In __init__:
self.session.proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'http://proxy.example.com:8080',
}
```

### Retry Logic

```python
import time

def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Attempt {attempt+1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Failed after {max_retries} attempts: {e}")
                return None
```

---

## Merging Multiple Vaults

If you scrape different years, merge them:

```python
import shutil
from pathlib import Path

# Copy articles from multiple years into one vault
main_vault = Path('./combined_vault')
main_vault.mkdir(exist_ok=True)

for year_vault in ['./rubens_2025', './rubens_2024']:
    src_articles = Path(year_vault) / 'articles'
    dst_articles = main_vault / 'articles'
    dst_articles.mkdir(exist_ok=True)
    
    for file in src_articles.glob('*.md'):
        shutil.copy(file, dst_articles / file.name)

print(f"✓ Merged vaults into {main_vault}")
```

---

## Performance Profiling

```python
import time

class ProfiledScraper(SubstackArchiveScraper):
    def scrape(self):
        start = time.time()
        
        print("⏱️ Parsing archive page...")
        parse_start = time.time()
        html = self.fetch_archive_page()
        articles = self.parse_archive_page(html)
        print(f"   Done in {time.time() - parse_start:.2f}s")
        
        print("⏱️ Fetching article details...")
        fetch_start = time.time()
        for i, article in enumerate(articles):
            self.fetch_article_details(article)
        print(f"   Done in {time.time() - fetch_start:.2f}s")
        
        print("⏱️ Filtering by year...")
        filter_start = time.time()
        self.articles = self.filter_by_year(articles, self.year_filter)
        print(f"   Done in {time.time() - filter_start:.2f}s")
        
        print(f"\n⏱️ Total time: {time.time() - start:.2f}s")
        return self.articles
```

---

## Contributing Improvements

Found a bug or have an improvement? The script is modular:

1. **Add date format support** - Extend the format list in `fetch_article_details()`
2. **Improve HTML parsing** - Modify selectors in `parse_archive_page()`
3. **Add export formats** - Create new generation methods
4. **Fix encoding issues** - Improve the `html_to_markdown()` function

The code is designed to be hackable!

---

**Need help?** Check the main documentation files or read the inline code comments - they're extensive!
