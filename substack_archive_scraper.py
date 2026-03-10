#!/usr/bin/env python3
"""
Specialized Substack Archive Scraper with 2025 Filtering

Scrapes archive pages from Substack and filters articles from current year (2025).
Designed for ruben.substack.com but works with any Substack archive.
"""

import requests
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class SubstackArchiveScraper:
    """Scrapes Substack archive pages and creates Obsidian vault."""
    
    def __init__(self, archive_url: str, output_dir: str = "./substack_vault", 
                 year_filter: int = 2026):
        """
        Initialize the scraper.
        
        Args:
            archive_url: Full archive URL (e.g., "https://ruben.substack.com/archive?sort=new")
            output_dir: Directory to store generated markdown files
            year_filter: Year to filter articles (default: 2025)
        """
        self.archive_url = archive_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.year_filter = year_filter
        
        # Create subdirectories
        self.articles_dir = self.output_dir / "articles"
        self.articles_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.output_dir / "metadata.json"
        self.index_file = self.output_dir / "INDEX.md"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        
        self.articles = []
        
    def extract_publication_name(self) -> str:
        """Extract publication name from archive URL."""
        match = re.search(r'https?://([a-zA-Z0-9_-]+)\.substack\.com', self.archive_url)
        if match:
            return match.group(1)
        return "substack"

    def normalize_date(self, date_str: Optional[str]) -> str:
        """Normalize various date formats to YYYY-MM-DD. Returns 'Unknown' on failure."""
        if not date_str or date_str == 'Unknown':
            return 'Unknown'

        # Already YYYY-MM-DD
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str.strip()):
            return date_str.strip()

        # ISO datetime (e.g. "2025-10-15T14:30:00.000Z")
        if re.match(r'^\d{4}-\d{2}-\d{2}T', date_str):
            return date_str[:10]

        # Try common text formats
        for fmt in ('%B %d, %Y', '%b %d, %Y', '%B %d %Y', '%b %d %Y'):
            try:
                return datetime.strptime(date_str.strip(), fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue

        return 'Unknown'

    def fetch_archive_page(self) -> Optional[str]:
        """Fetch the archive page HTML."""
        try:
            print(f"Fetching archive page: {self.archive_url}")
            response = self.session.get(self.archive_url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Failed to fetch archive page: {e}")
            return None

    def fetch_articles_via_api(self) -> List[Dict]:
        """Fetch all articles via Substack's /api/v1/archive JSON endpoint with pagination."""
        pub_name = self.extract_publication_name()
        base_url = f"https://{pub_name}.substack.com/api/v1/archive"
        articles = []
        offset = 0
        limit = 12

        try:
            while True:
                params = {'sort': 'new', 'offset': offset, 'limit': limit}
                print(f"  API page offset={offset}...")
                response = self.session.get(base_url, params=params, timeout=15)
                response.raise_for_status()
                posts = response.json()

                if not posts:
                    break

                for post in posts:
                    canonical = post.get('canonical_url', '')
                    slug = post.get('slug', '')
                    if not canonical and slug:
                        canonical = f"https://{pub_name}.substack.com/p/{slug}"

                    authors = post.get('publishedBylines', [])
                    author = authors[0].get('name', 'Unknown') if authors else 'Unknown'

                    tags = [t.get('name', '') for t in post.get('postTags', [])]

                    articles.append({
                        'title': post.get('title', 'Untitled'),
                        'subtitle': post.get('subtitle', ''),
                        'url': canonical,
                        'slug': slug,
                        'date': self.normalize_date(post.get('post_date', '')),
                        'author': author,
                        'content': post.get('body_html', ''),
                        'tags': tags,
                    })

                offset += limit
                time.sleep(0.5)

        except Exception as e:
            print(f"  API fetch failed: {e}")
            if articles:
                print(f"  Returning {len(articles)} articles fetched before failure")
            return articles

        print(f"  API returned {len(articles)} total articles")
        return articles

    def parse_archive_page(self, html: str) -> List[Dict]:
        """Parse archive page HTML to extract article information."""
        articles = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all article links in archive
            # Substack uses various class names - try multiple selectors
            article_elements = soup.find_all('a', {'href': re.compile(r'/p/[a-zA-Z0-9-]+')})
            
            print(f"Found {len(article_elements)} article links")
            
            for element in article_elements:
                try:
                    # Get article title
                    title = element.get_text(strip=True)
                    if not title:
                        continue
                    
                    # Get article URL
                    href = element.get('href', '')
                    if not href.startswith('http'):
                        href = urljoin(self.archive_url, href)
                    
                    # Extract slug from URL
                    slug_match = re.search(r'/p/([a-zA-Z0-9-]+)', href)
                    slug = slug_match.group(1) if slug_match else ''
                    
                    article = {
                        'title': title,
                        'url': href,
                        'slug': slug,
                        'date': None,  # Will be fetched from individual article
                    }
                    
                    # Try to find date from parent elements
                    parent = element.parent
                    for _ in range(5):  # Look up 5 levels
                        if parent:
                            date_text = parent.get_text(strip=True)
                            date_match = re.search(r'(\w+\s+\d+,\s+\d{4})', date_text)
                            if date_match:
                                article['date'] = self.normalize_date(date_match.group(1))
                                break
                            parent = parent.parent
                    
                    articles.append(article)
                    
                except Exception as e:
                    print(f"Error parsing article element: {e}")
                    continue
            
        except Exception as e:
            print(f"Error parsing archive page: {e}")
            return articles
        
        return articles
    
    def fetch_article_details(self, article: Dict) -> Dict:
        """Fetch detailed article information from the article page."""
        try:
            print(f"  Fetching: {article['title'][:50]}...")
            response = self.session.get(article['url'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract date
            date_str = article.get('date')

            # Try <time datetime="..."> first
            time_elem = soup.find('time', {'datetime': True})
            if time_elem:
                date_str = time_elem['datetime']

            if not date_str or date_str == 'Unknown':
                # Fallback: parse "Month DD, YYYY" from page text
                page_text = soup.get_text()
                date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}', page_text)
                if date_match:
                    date_str = date_match.group(0)

            article['date'] = self.normalize_date(date_str)

            # Extract author - look for substack profile links
            author_link = soup.find('a', {'href': re.compile(r'substack\.com/@')})
            if author_link:
                author_text = author_link.get_text(strip=True)
                article['author'] = author_text if author_text else author_link['href'].split('@')[-1]
            else:
                article['author'] = 'Unknown'

            # Extract subtitle
            subtitle_elem = soup.find('h3', {'class': re.compile('.*subtitle.*')})
            if not subtitle_elem:
                subtitle_elem = soup.find('h2', {'class': re.compile('.*subtitle.*')})
            article['subtitle'] = subtitle_elem.get_text(strip=True) if subtitle_elem else ''

            # Extract content - Substack uses div.available-content > div.body.markup
            content_elem = soup.find('div', {'class': 'available-content'})
            if content_elem:
                body = content_elem.find('div', {'class': 'body'})
                if body:
                    content_elem = body
            if not content_elem:
                content_elem = soup.find('div', {'class': re.compile('.*post-content.*')})

            article['content'] = str(content_elem) if content_elem else ''

            # Extract tags/topics
            tag_elements = soup.find_all('a', {'href': re.compile(r'/search.*')})
            article['tags'] = [tag.get_text(strip=True) for tag in tag_elements[:5]]
            
            time.sleep(1)  # Respectful rate limiting
            return article
            
        except Exception as e:
            print(f"    Error fetching article details: {e}")
            return article
    
    def filter_by_year(self, articles: List[Dict], year: int) -> List[Dict]:
        """Filter articles to only those from specified year."""
        filtered = []
        for article in articles:
            date_str = article.get('date', '')
            if not date_str or date_str == 'Unknown':
                continue
            try:
                year_match = re.search(r'(\d{4})', date_str)
                if year_match and int(year_match.group(1)) == year:
                    filtered.append(article)
            except:
                continue
        return filtered

    def filter_by_date_range(self, articles: List[Dict], start_date, end_date) -> List[Dict]:
        """Filter articles between start_date and end_date (inclusive). Accepts date or str (YYYY-MM-DD)."""
        from datetime import date as date_type
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        filtered = []
        for article in articles:
            date_str = article.get('date', '')
            if not date_str or date_str == 'Unknown':
                continue
            try:
                article_date = datetime.strptime(date_str[:10], '%Y-%m-%d').date()
                if start_date <= article_date <= end_date:
                    filtered.append(article)
            except ValueError:
                continue
        return filtered
    
    def html_to_markdown(self, html_content: str) -> str:
        """Convert HTML content to clean Markdown."""
        if not html_content:
            return ""
        
        # Remove script and style tags
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
        
        # Headers
        html_content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', html_content, flags=re.DOTALL)
        
        # Bold and italic
        html_content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', html_content, flags=re.DOTALL)
        
        # Links
        html_content = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', r'[\2](\1)', html_content, flags=re.DOTALL)
        
        # Blockquotes
        html_content = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'> \1', html_content, flags=re.DOTALL)
        
        # Code blocks
        html_content = re.sub(r'<pre[^>]*>(.*?)</pre>', r'```\n\1\n```', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', html_content, flags=re.DOTALL)
        
        # Paragraphs
        html_content = re.sub(r'</p>', '\n\n', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<p[^>]*>', '', html_content, flags=re.DOTALL)
        
        # Line breaks
        html_content = re.sub(r'<br\s*/?>', '\n', html_content)
        
        # Lists
        html_content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<[ou]l[^>]*>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'</[ou]l>', '', html_content, flags=re.DOTALL)
        
        # Images (preserve as markdown)
        html_content = re.sub(r'<img[^>]*src=["\']([^"\']*)["\'][^>]*alt=["\']([^"\']*)["\']', r'![\2](\1)', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<img[^>]*src=["\']([^"\']*)["\']', r'![\1](\1)', html_content, flags=re.DOTALL)
        
        # Remove remaining HTML tags
        html_content = re.sub(r'<[^>]+>', '', html_content)
        
        # Clean up HTML entities
        html_content = html_content.replace('&nbsp;', ' ')
        html_content = html_content.replace('&lt;', '<')
        html_content = html_content.replace('&gt;', '>')
        html_content = html_content.replace('&amp;', '&')
        html_content = html_content.replace('&quot;', '"')
        
        # Clean up whitespace
        html_content = re.sub(r'\n\n+', '\n\n', html_content)
        html_content = html_content.strip()
        
        return html_content
    
    def sanitize_filename(self, filename: str) -> str:
        """Convert a string to a safe filename."""
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'\s+', '_', filename)
        filename = filename[:200]
        return filename
    
    def create_markdown_file(self, article: Dict) -> str:
        """Create a markdown file for an article, organized by author subfolder."""

        # Organize into author subfolder
        author = article.get('author', 'Unknown')
        safe_author = self.sanitize_filename(author) if author and author != 'Unknown' else 'Unknown'
        author_dir = self.articles_dir / safe_author
        author_dir.mkdir(exist_ok=True)

        safe_title = self.sanitize_filename(article['title'])
        filename = f"{safe_title}.md"
        filepath = author_dir / filename
        
        # Create frontmatter
        date_str = article.get('date', 'Unknown')
        tags = article.get('tags', [])
        
        frontmatter = f"""---
title: {article['title']}
subtitle: {article.get('subtitle', '')}
author: {article.get('author', 'Unknown')}
date: {date_str}
url: {article.get('url', '')}
tags: {json.dumps(tags)}
---

"""
        
        # Convert content to markdown
        markdown_content = self.html_to_markdown(article.get('content', ''))
        
        # Build full file content
        full_content = frontmatter + f"# {article['title']}\n\n"
        
        if article.get('subtitle'):
            full_content += f"*{article['subtitle']}*\n\n"
        
        full_content += f"**Published:** {date_str}\n"
        full_content += f"**Author:** {article.get('author', 'Unknown')}\n"
        full_content += f"**Read original:** [{article['title']}]({article.get('url', '')})\n\n"
        
        full_content += "---\n\n"
        
        if markdown_content:
            full_content += markdown_content
        else:
            full_content += "*No content extracted. Please visit the original article.*\n"
        
        # Add tags section
        if tags:
            full_content += "\n\n## Topics\n\n"
            for tag in tags:
                safe_tag = self.sanitize_filename(tag)
                full_content += f"- #{tag}\n"
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return filename
    
    def generate_index(self):
        """Generate an index file for the vault, grouped by author."""

        if not self.articles:
            return

        pub_name = self.extract_publication_name()

        index_content = f"""# Substack Archive

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Total Articles:** {len(self.articles)}

---

"""

        # Group by author, then sort each group by date (newest first)
        from collections import defaultdict
        by_author = defaultdict(list)
        for article in self.articles:
            author = article.get('author', 'Unknown')
            by_author[author].append(article)

        for author in sorted(by_author.keys()):
            safe_author = self.sanitize_filename(author) if author and author != 'Unknown' else 'Unknown'
            articles = sorted(by_author[author], key=lambda x: x.get('date', ''), reverse=True)
            index_content += f"## {author}\n\n"

            for article in articles:
                date_str = article['date']
                safe_title = self.sanitize_filename(article['title'])
                index_content += f"- [{article['title']}](articles/{safe_author}/{safe_title}.md) — {date_str}\n"

            index_content += "\n"

        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"\nIndex created: {self.index_file}")
    
    def save_metadata(self):
        """Save article metadata as JSON."""
        metadata = {
            'archive_url': self.archive_url,
            'publication_name': self.extract_publication_name(),
            'year_filter': self.year_filter,
            'scraped_at': datetime.now().isoformat(),
            'total_articles': len(self.articles),
            'articles': self.articles
        }
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"Metadata saved: {self.metadata_file}")
    
    def scrape_all(self) -> List[Dict]:
        """Fetch all articles from archive. Tries API first, falls back to HTML scraping."""
        print(f"\n{'='*60}")
        print(f"Substack Archive Scraper")
        print(f"{'='*60}\n")

        # Try API first — returns all articles with pagination and clean dates
        print("Trying API endpoint...")
        articles = self.fetch_articles_via_api()

        if articles:
            print(f"\nFetched {len(articles)} articles via API\n")
            return articles

        # Fall back to HTML scraping (single page only)
        print("API returned no articles, falling back to HTML scraping...")
        html = self.fetch_archive_page()
        if not html:
            return []

        articles = self.parse_archive_page(html)
        print(f"\nFound {len(articles)} articles in archive\n")

        if not articles:
            return []

        print(f"Fetching article details...\n")
        for i, article in enumerate(articles, 1):
            print(f"[{i}/{len(articles)}] {article['title'][:50]}...")
            self.fetch_article_details(article)

        return articles

    def scrape(self) -> List[Dict]:
        """Scrape archive and filter by year_filter (backward-compatible entry point)."""
        articles = self.scrape_all()
        print(f"\nFiltering articles from {self.year_filter}...\n")
        filtered = self.filter_by_year(articles, self.year_filter)
        print(f"Filtered from {len(articles)} to {len(filtered)} articles from {self.year_filter}\n")
        self.articles = filtered
        return filtered
    
    def generate(self):
        """Generate all markdown files and index."""
        
        if not self.articles:
            print("No articles to generate. Aborting.")
            return
        
        print(f"\nGenerating markdown files...\n")
        
        for i, article in enumerate(self.articles, 1):
            try:
                filename = self.create_markdown_file(article)
                print(f"[{i}/{len(self.articles)}] Created: {filename}")
            except Exception as e:
                print(f"[ERROR] Failed to create file for '{article['title']}': {e}")
        
        self.generate_index()
        self.save_metadata()
        
        print(f"\n{'='*60}")
        print(f"✓ COMPLETED!")
        print(f"{'='*60}")
        print(f"\nVault created at: {self.output_dir.absolute()}\n")
        print(f"Next steps:")
        print(f"  1. Open Obsidian")
        print(f"  2. Create new vault → 'Store in a folder on my computer'")
        print(f"  3. Select: {self.output_dir.absolute()}")
        print(f"  4. Open INDEX.md to start browsing\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Scrape Substack archive and filter by date range or year'
    )
    parser.add_argument(
        'archive_url',
        help='Full Substack archive URL (e.g., https://ruben.substack.com/archive?sort=new)'
    )
    parser.add_argument(
        '-y', '--year',
        type=int,
        default=None,
        help='Year to filter articles (e.g. 2026). Ignored if --start-date/--end-date are set.'
    )
    parser.add_argument(
        '--start-date',
        default=None,
        help='Start date for filtering (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end-date',
        default=None,
        help='End date for filtering (YYYY-MM-DD)'
    )
    parser.add_argument(
        '-o', '--output',
        default='./substack_vault',
        help='Output directory for the vault (default: ./substack_vault)'
    )

    args = parser.parse_args()

    # Determine filtering mode
    use_date_range = args.start_date and args.end_date
    year = args.year if args.year else 2026

    scraper = SubstackArchiveScraper(args.archive_url, args.output, year_filter=year)
    all_articles = scraper.scrape_all()

    if use_date_range:
        print(f"\nFiltering articles from {args.start_date} to {args.end_date}...\n")
        scraper.articles = scraper.filter_by_date_range(all_articles, args.start_date, args.end_date)
    else:
        print(f"\nFiltering articles from {year}...\n")
        scraper.articles = scraper.filter_by_year(all_articles, year)

    print(f"Kept {len(scraper.articles)} articles after filtering\n")
    scraper.generate()


if __name__ == '__main__':
    main()
