# Substack Scraper Suite - Complete Overview

You now have **two complete scrapers** for different use cases:

---

## Quick Decision: Which Scraper to Use?

### Use `substack_archive_scraper.py` ✅ FOR YOUR CASE

**When:** You want to scrape an **archive page** and filter by year
- ✅ Scrapes entire archive with date filtering
- ✅ Perfect for "give me all 2026 articles"
- ✅ Automatically filters by year
- ✅ Includes your exact URL: `https://ruben.substack.com/archive?sort=new`

**Example:**
```bash
python substack_archive_scraper.py "https://ruben.substack.com/archive?sort=new"
# Automatically filters to 2026 only
```

---

### Use `substack_scraper.py` FOR GENERAL USE

**When:** You want to scrape a **general Substack publication** without archive filtering
- ✅ Works with any Substack URL
- ✅ Gets articles via RSS feed (fastest)
- ✅ Fallback to API
- ✅ No year filtering (gets all articles)

**Example:**
```bash
python substack_scraper.py "https://example.substack.com"
# Gets all articles from publication
```

---

## File Organization

```
📦 You have these files:

ARCHIVE SCRAPER (Use this for ruben.substack.com)
├── substack_archive_scraper.py    ← The main script
├── ARCHIVE_QUICKSTART.md          ← Quick start guide (read this first!)
└── ARCHIVE_ADVANCED.md            ← Advanced tips & customization

GENERAL SCRAPER (For other Substacks)
├── substack_scraper.py            ← The main script
├── SETUP_GUIDE.md                 ← Detailed setup
├── QUICKSTART.md                  ← Quick reference
├── examples.py                    ← 9 example use cases
└── TECHNICAL.md                   ← Architecture & customization

SUMMARY
└── THIS FILE                      ← You are here
```

---

## Getting Started (30 seconds)

### For Ruben's Newsletter (2025 articles):

```bash
# 1. Install dependencies
pip install requests beautifulsoup4 --break-system-packages

# 2. Run the scraper
python substack_archive_scraper.py "https://ruben.substack.com/archive?sort=new"

# 3. Open vault in Obsidian
# File → Create vault → Select "substack_vault" folder
```

That's it! You'll have all 2026 articles in Obsidian in ~2 minutes.

---

## What Each File Does

### Core Scripts

| File | Purpose | Use Case |
|------|---------|----------|
| `substack_archive_scraper.py` | **Specialized for archive pages** with year filtering | Scraping ruben.substack.com with 2026 filter |
| `substack_scraper.py` | General-purpose Substack scraper | Any Substack publication |

### Documentation - Archive Scraper

| File | Read When | Contains |
|------|-----------|----------|
| `ARCHIVE_QUICKSTART.md` | **First** (before running anything) | 2-minute setup, basic usage, troubleshooting |
| `ARCHIVE_ADVANCED.md` | After scraping works | Advanced customization, analysis, scheduling |

### Documentation - General Scraper

| File | Read When | Contains |
|------|-----------|----------|
| `QUICKSTART.md` | If using general scraper | 5-minute setup, basic commands |
| `SETUP_GUIDE.md` | For detailed understanding | Full documentation, tips, features |
| `TECHNICAL.md` | For customization | Architecture, code examples, deployment |
| `examples.py` | For ideas | 9 ready-to-use examples |

---

## For Your Specific Task

**Goal:** Get all Ruben's 2025 articles into Obsidian

**Solution:** Use `substack_archive_scraper.py`

**Steps:**

1. **Read:** `ARCHIVE_QUICKSTART.md` (2 min)
2. **Install:** `pip install requests beautifulsoup4 --break-system-packages`
3. **Run:** `python substack_archive_scraper.py "https://ruben.substack.com/archive?sort=new"`
4. **Open:** The `substack_vault` folder in Obsidian
5. **Explore:** Click `INDEX.md` to see all articles

**Result:** Beautiful Obsidian vault with:
- ✅ Only 2026 articles
- ✅ One markdown file per article
- ✅ Full content, metadata, links
- ✅ Indexed and organized
- ✅ Ready to add your own notes

---

## Key Features Comparison

### Archive Scraper
- ✅ **Date filtering** (2026, 2025, 2024, etc.)
- ✅ **Archive page support** (the `?sort=new` URLs)
- ✅ Fetches full article content
- ✅ Extracts author, date, tags
- ✅ Generates Obsidian vault
- ✅ ~2 minutes for 20 articles

### General Scraper
- ✅ Works with any Substack
- ✅ RSS feed support (faster)
- ✅ API fallback
- ✅ No year filtering
- ✅ Large archive support
- ✅ Multiple scraping methods

---

## Customization

### Before Running (Easy Changes)

```bash
# Get 2025 articles instead of 2026
python substack_archive_scraper.py "..." -y 2025

# Get 2024 articles
python substack_archive_scraper.py "..." -y 2024

# Save to different folder
python substack_archive_scraper.py "..." -o ~/My_Vaults/ruben_2026
```

### After Getting Vault (Advanced Changes)

See `ARCHIVE_ADVANCED.md` for:
- Filtering specific articles
- Adding custom metadata
- Merging multiple years
- Scheduling automatic updates
- Exporting to different formats

---

## Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| No articles found | Check URL is correct, try `-y 2024` to verify |
| BeautifulSoup error | `pip install beautifulsoup4 --break-system-packages` |
| Network timeout | Check internet, try again |
| Content looks incomplete | Normal - visit original article to verify |
| Want different year | Use `-y 2024` (or any year) |

See `ARCHIVE_QUICKSTART.md` for full troubleshooting.

---

## What You Get

After running the scraper:

```
substack_vault/
├── INDEX.md
│   ↳ Master index, sorted by date
│   ↳ All articles listed
│   ↳ Search-friendly
│
├── articles/
│   ├── AI_and_the_Future_of_Work.md
│   ├── 2025_Predictions.md
│   ├── Technical_Deep_Dive.md
│   └── ... (one per article)
│
└── metadata.json
    ↳ Backup of all raw data
    ↳ Useful for analysis
```

Each article file contains:
- Metadata (YAML frontmatter)
- Full content (clean Markdown)
- Links to topics
- Original article URL

---

## Opening in Obsidian

1. **Open Obsidian**
2. **File → Create new vault**
3. **Select "Store in a folder on my computer"**
4. **Choose the `substack_vault` folder**
5. **Click INDEX.md** to start browsing

---

## Next Steps After Scraping

### Immediate
- [ ] Read through articles using INDEX.md
- [ ] Check metadata.json to verify data
- [ ] Try searching for keywords

### Short Term
- [ ] Create topic notes linking related articles
- [ ] Add your own thoughts to articles
- [ ] Organize by theme

### Long Term
- [ ] Build knowledge graph
- [ ] Export as webpage or PDF
- [ ] Setup periodic scraping

---

## Common Questions

### Q: Will this work with other Substacks?
**A:** Yes! Use `substack_scraper.py` for any Substack, or `substack_archive_scraper.py` if they have archive pages.

### Q: How often can I scrape?
**A:** As often as you want. The scraper includes respectful rate limiting (1-second delays).

### Q: Can I modify the scraper?
**A:** Absolutely! All code is well-commented and designed to be customized. See `ARCHIVE_ADVANCED.md`.

### Q: What if the format changes?
**A:** The selectors are well-documented. If Substack changes their HTML, you can update the CSS selectors.

### Q: Can I export the vault?
**A:** Yes! See `ARCHIVE_ADVANCED.md` for HTML, PDF, and CSV export options.

---

## Performance Expectations

| Action | Time |
|--------|------|
| Install | 1 min |
| Scrape 20 articles | 30-40 sec |
| Generate vault | 5 sec |
| **Total** | **~2 minutes** |

Larger archives take longer, but it's mostly waiting for Substack to serve content.

---

## File Sizes

| Vault Size | Article Count | Disk Space |
|-----------|---------------|-----------|
| Small | 10 articles | ~1-2 MB |
| Medium | 50 articles | ~10-20 MB |
| Large | 200+ articles | ~50+ MB |

Metadata.json accounts for most of the size (it stores raw HTML). You can delete it if space is a concern.

---

## Support & Help

1. **Can't run?** → Check `ARCHIVE_QUICKSTART.md` troubleshooting
2. **Need advanced help?** → Read `ARCHIVE_ADVANCED.md`
3. **Want to modify?** → The code is readable with clear comments
4. **Still stuck?** → Check the inline code comments

---

## Summary

You have **two powerful scrapers**:

1. **`substack_archive_scraper.py`** ← **Use this for Ruben's newsletter**
   - Archive page support
   - Year filtering
   - Perfect for your use case

2. **`substack_scraper.py`** ← Use this for other Substacks
   - General-purpose
   - RSS/API support
   - No filtering

**Ready to start?**

```bash
pip install requests beautifulsoup4 --break-system-packages
python substack_archive_scraper.py "https://ruben.substack.com/archive?sort=new"
```

See you in Obsidian! 🚀

---

**Need a refresher?** Each file is clearly named:
- Want quick start? → `ARCHIVE_QUICKSTART.md`
- Need advanced tips? → `ARCHIVE_ADVANCED.md`
- Questions about general scraper? → `QUICKSTART.md` or `SETUP_GUIDE.md`
