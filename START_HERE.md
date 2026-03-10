# 🚀 START HERE

Welcome! You have a complete Substack scraper suite ready to use.

## Your Goal
Get all Ruben's **2026 AI articles** into Obsidian

## Quick Path (3 minutes)

```bash
# 1. Install
pip install requests beautifulsoup4 --break-system-packages

# 2. Scrape Ruben's 2025 articles
python substack_archive_scraper.py "https://ruben.substack.com/archive?sort=new"

# 3. Open in Obsidian
# File → Create vault → Select the "substack_vault" folder
```

Done! ✅

## What You Have

| File | Purpose | Read When |
|------|---------|-----------|
| **substack_archive_scraper.py** | Main scraper for your task | After this file |
| **ARCHIVE_QUICKSTART.md** | Detailed setup guide | For full instructions |
| **README.md** | File overview & reference | For understanding the suite |
| **QUICK_REFERENCE.txt** | Cheat sheet | While scraping |
| **examples.py** | Code examples | For customization |

## What You Get

```
substack_vault/
├── INDEX.md              ← All articles by date
├── articles/             ← One file per article
│   ├── Article_1.md
│   ├── Article_2.md
│   └── ...
└── metadata.json         ← Backup data
```

Each article has:
- Full content (clean Markdown)
- Metadata (date, author, tags)
- Link to original

## Next Steps

1. **Read** `ARCHIVE_QUICKSTART.md` (5 min)
2. **Run** the command above (2 min)
3. **Enjoy** your vault in Obsidian!

## Troubleshooting

**"Module not found"**
```bash
pip install requests beautifulsoup4 --break-system-packages
```

**"Connection failed"**
- Check internet
- Try again in a moment

**"No articles found"**
- Check URL is: `https://ruben.substack.com/archive?sort=new`

## Have Questions?

- **Quick answers**: See `QUICK_REFERENCE.txt`
- **Full details**: Read `ARCHIVE_QUICKSTART.md`
- **Everything**: Check `README.md`

---

**Ready?** Run the scraper command above! 🎯
