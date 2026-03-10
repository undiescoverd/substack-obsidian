#!/usr/bin/env python3
"""
Example scripts for using the Substack scraper.
Copy and modify these for your needs.
"""

# ============================================================================
# EXAMPLE 1: Basic Usage
# ============================================================================

def example_basic():
    """Simplest way to scrape a publication."""
    from substack_scraper import SubstackScraper
    
    scraper = SubstackScraper(
        "https://example.substack.com",
        output_dir="./my_vault"
    )
    scraper.scrape()
    scraper.generate()


# ============================================================================
# EXAMPLE 2: Scrape Multiple Publications
# ============================================================================

def example_multiple_publications():
    """Scrape several Substack publications into separate vaults."""
    from substack_scraper import SubstackScraper
    
    publications = {
        "tech_news": "https://technewsletter.substack.com",
        "philosophy": "https://philosophy.substack.com",
        "business": "https://business.substack.com",
    }
    
    for name, url in publications.items():
        print(f"\n{'='*50}")
        print(f"Scraping: {name}")
        print(f"{'='*50}")
        
        scraper = SubstackScraper(url, output_dir=f"./vaults/{name}")
        articles = scraper.scrape()
        
        if articles:
            scraper.generate()
        else:
            print(f"No articles found for {name}")


# ============================================================================
# EXAMPLE 3: Filter Articles by Date Range
# ============================================================================

def example_date_filter():
    """Scrape only recent articles."""
    from substack_scraper import SubstackScraper
    from datetime import datetime, timedelta
    
    scraper = SubstackScraper("https://example.substack.com")
    scraper.scrape()
    
    # Keep only articles from last 6 months
    cutoff = datetime.now() - timedelta(days=180)
    original_count = len(scraper.articles)
    
    scraper.articles = [
        a for a in scraper.articles
        if a['date'] and datetime.fromisoformat(a['date'][:10]) > cutoff
    ]
    
    print(f"Filtered from {original_count} to {len(scraper.articles)} articles")
    scraper.generate()


# ============================================================================
# EXAMPLE 4: Incremental Updates
# ============================================================================

def example_incremental_update():
    """Update an existing vault with only new articles."""
    from substack_scraper import SubstackScraper
    import json
    from pathlib import Path
    
    vault_dir = Path("./my_vault")
    metadata_file = vault_dir / "metadata.json"
    
    # Load existing articles
    existing_urls = set()
    if metadata_file.exists():
        with open(metadata_file) as f:
            data = json.load(f)
            existing_urls = {a['url'] for a in data['articles']}
    
    # Scrape new articles
    scraper = SubstackScraper("https://example.substack.com", output_dir=vault_dir)
    scraper.scrape()
    
    # Filter to only new articles
    new_articles = [a for a in scraper.articles if a['url'] not in existing_urls]
    
    if new_articles:
        print(f"Found {len(new_articles)} new articles")
        scraper.articles = scraper.articles  # Generate all (will overwrite existing)
        scraper.generate()
    else:
        print("No new articles found")


# ============================================================================
# EXAMPLE 5: Analyze Scraped Content
# ============================================================================

def example_analyze_content():
    """Analyze article metadata without generating files."""
    from substack_scraper import SubstackScraper
    from collections import Counter
    import json
    
    scraper = SubstackScraper("https://example.substack.com")
    scraper.scrape()
    
    if not scraper.articles:
        print("No articles to analyze")
        return
    
    print(f"\n📊 Analysis Report")
    print(f"{'='*50}")
    
    # Basic stats
    print(f"Total Articles: {len(scraper.articles)}")
    
    # Date range
    dates = [a['date'][:10] for a in scraper.articles if a['date']]
    if dates:
        dates.sort()
        print(f"Date Range: {dates[0]} to {dates[-1]}")
    
    # Most common authors
    authors = Counter(a['author'] for a in scraper.articles if a['author'])
    print(f"\nTop Authors:")
    for author, count in authors.most_common(5):
        print(f"  {author}: {count} articles")
    
    # Tag analysis
    all_tags = []
    for a in scraper.articles:
        all_tags.extend(a.get('tags', []))
    
    tag_counts = Counter(all_tags)
    print(f"\nMost Common Tags:")
    for tag, count in tag_counts.most_common(10):
        print(f"  {tag}: {count}")
    
    # Content length analysis
    content_lengths = [len(a.get('content', '')) for a in scraper.articles]
    avg_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
    print(f"\nAverage Article Length: {avg_length:,.0f} characters")
    
    # Save analysis
    with open("analysis.json", "w") as f:
        json.dump({
            'total_articles': len(scraper.articles),
            'authors': dict(authors),
            'tags': dict(tag_counts),
            'avg_article_length': avg_length,
            'date_range': [dates[0], dates[-1]] if dates else None
        }, f, indent=2)
    
    print(f"\n✓ Analysis saved to analysis.json")


# ============================================================================
# EXAMPLE 6: Custom Markdown Generation
# ============================================================================

def example_custom_markdown():
    """Generate custom markdown format for your needs."""
    from substack_scraper import SubstackScraper
    from pathlib import Path
    
    class CustomSubstackScraper(SubstackScraper):
        """Extended scraper with custom markdown format."""
        
        def create_markdown_file(self, article):
            """Generate custom markdown format."""
            
            safe_title = self.sanitize_filename(article['title'])
            filepath = self.articles_dir / f"{safe_title}.md"
            
            # Custom format using Dataview plugin syntax
            content = f"""# {article['title']}

## Metadata
- **Publication Date:** {article['date'][:10]}
- **Author:** {article['author']}
- **Source URL:** {article['url']}
- **Content Type:** Article
- **Status:** Unprocessed

## Tags
{' '.join(f"#{tag}" for tag in article.get('tags', []))}

## Summary
{article.get('subtitle', '')}

## Content

{self.html_to_markdown(article.get('content', ''))}

## Reading Notes
- [ ] Read full article
- [ ] Extract key points
- [ ] Add personal insights
- [ ] Connect to existing notes

---

Generated by Substack Scraper
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return str(filepath)
    
    scraper = CustomSubstackScraper("https://example.substack.com")
    scraper.scrape()
    scraper.generate()


# ============================================================================
# EXAMPLE 7: Backup & Archive
# ============================================================================

def example_backup():
    """Create a backup of your vault."""
    from substack_scraper import SubstackScraper
    import shutil
    from datetime import datetime
    
    vault_dir = Path("./my_vault")
    
    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"./backups/vault_backup_{timestamp}")
    
    shutil.copytree(vault_dir, backup_dir)
    print(f"✓ Backup created: {backup_dir}")


# ============================================================================
# EXAMPLE 8: Export to Different Formats
# ============================================================================

def example_export_to_csv():
    """Export article metadata to CSV for spreadsheet analysis."""
    from substack_scraper import SubstackScraper
    import csv
    
    scraper = SubstackScraper("https://example.substack.com")
    scraper.scrape()
    
    with open("articles.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'title', 'date', 'author', 'url', 'tags', 'content_length'
        ])
        writer.writeheader()
        
        for article in scraper.articles:
            writer.writerow({
                'title': article['title'],
                'date': article.get('date', ''),
                'author': article.get('author', ''),
                'url': article['url'],
                'tags': '; '.join(article.get('tags', [])),
                'content_length': len(article.get('content', ''))
            })
    
    print("✓ Exported to articles.csv")


# ============================================================================
# EXAMPLE 9: Automated Cron Job (Linux/Mac)
# ============================================================================

def example_cron_script():
    """
    Save this as `update_vault.sh` and run with cron.
    
    Add to crontab with: crontab -e
    
    # Update vault daily at 9 AM
    0 9 * * * /path/to/update_vault.sh
    
    # Update vault every 6 hours
    0 */6 * * * /path/to/update_vault.sh
    """
    script = '''#!/bin/bash

# Configuration
PUBLICATION="https://example.substack.com"
VAULT_DIR="$HOME/Obsidian Vaults/Newsletter"
LOG_FILE="$VAULT_DIR/update.log"

# Log timestamp
echo "Update started: $(date)" >> "$LOG_FILE"

# Run scraper
cd "$VAULT_DIR"
python3 substack_scraper.py "$PUBLICATION" -o . >> "$LOG_FILE" 2>&1

# Log result
if [ $? -eq 0 ]; then
    echo "Update completed successfully" >> "$LOG_FILE"
else
    echo "Update failed" >> "$LOG_FILE"
fi

# Optional: Sync to cloud storage
# cp -r articles ~/Dropbox/MyVault/
'''
    
    with open("update_vault.sh", "w") as f:
        f.write(script)
    
    print("✓ Created update_vault.sh")
    print("To use: chmod +x update_vault.sh && crontab -e")


# ============================================================================
# MAIN: Choose which example to run
# ============================================================================

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    print("Substack Scraper - Example Scripts")
    print("=" * 50)
    print("\n1. Basic scraping")
    print("2. Multiple publications")
    print("3. Filter by date")
    print("4. Incremental updates")
    print("5. Analyze content")
    print("6. Custom markdown")
    print("7. Create backup")
    print("8. Export to CSV")
    print("9. Show cron script")
    
    choice = input("\nSelect example (1-9): ").strip()
    
    examples = {
        "1": example_basic,
        "2": example_multiple_publications,
        "3": example_date_filter,
        "4": example_incremental_update,
        "5": example_analyze_content,
        "6": example_custom_markdown,
        "7": example_backup,
        "8": example_export_to_csv,
        "9": example_cron_script,
    }
    
    if choice in examples:
        try:
            examples[choice]()
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Invalid choice")
