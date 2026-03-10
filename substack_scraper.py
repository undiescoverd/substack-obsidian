#!/usr/bin/env python3
"""
Substack Profile Scraper & Obsidian Knowledge Base Generator

This script scrapes a Substack publication and creates a structured Obsidian vault
with individual markdown files for each article, including metadata and backlinks.
"""

import requests
import json
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
from typing import Optional, List, Dict
import time

# Try to import optional dependencies
try:
    from bs4 import BeautifulSoup
    HAS_BEAUTIFULSOUP = True
except ImportError:
    HAS_BEAUTIFULSOUP = False

try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False


class SubstackScraper:
    """Scrapes Substack publications and generates Obsidian markdown files."""
    
    def __init__(self, publication_url: str, output_dir: str = "./substack_vault"):
        """
        Initialize the scraper.
        
        Args:
            publication_url: URL of the Substack publication (e.g., "https://example.substack.com")
            output_dir: Directory to store generated markdown files
        """
        self.publication_url = publication_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.articles_dir = self.output_dir / "articles"
        self.articles_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.output_dir / "metadata.json"
        self.index_file = self.output_dir / "INDEX.md"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.articles = []
        
    def extract_publication_name(self) -> str:
        """Extract publication name from URL."""
        # Remove protocol and domain
        name = self.publication_url.replace('https://', '').replace('http://', '')
        name = name.replace('.substack.com', '').replace('www.', '')
        return name
    
    def scrape_via_api(self) -> List[Dict]:
        """
        Scrape articles using Substack's API endpoint.
        This is more reliable than HTML scraping.
        """
        pub_name = self.extract_publication_name()
        articles = []
        
        try:
            # Substack exposes articles via API
            api_url = f"https://{pub_name}.substack.com/api/v1/publications"
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            pub_data = response.json()
            
            # Get the publication ID
            pub_id = pub_data.get('id')
            if not pub_id:
                print("Could not extract publication ID from API")
                return articles
            
            # Fetch articles (paginated)
            offset = 0
            limit = 12
            
            while True:
                api_posts_url = f"https://{pub_name}.substack.com/api/v1/posts"
                params = {
                    'limit': limit,
                    'offset': offset,
                    'publication_id': pub_id
                }
                
                response = self.session.get(api_posts_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                posts = data.get('data', [])
                if not posts:
                    break
                
                for post in posts:
                    article = {
                        'title': post.get('title', 'Untitled'),
                        'subtitle': post.get('subtitle', ''),
                        'url': post.get('canonical_url', f"{self.publication_url}/p/{post.get('slug')}"),
                        'date': post.get('post_date', ''),
                        'author': post.get('byline', ''),
                        'content': post.get('body_html', post.get('body', '')),
                        'tags': [t.get('name', '') for t in post.get('topics', [])],
                        'slug': post.get('slug', ''),
                    }
                    articles.append(article)
                
                offset += limit
                time.sleep(0.5)  # Be respectful with requests
                
        except Exception as e:
            print(f"API scraping failed: {e}")
            return articles
        
        return articles
    
    def scrape_via_rss(self) -> List[Dict]:
        """
        Scrape articles using RSS feed (simpler, more reliable).
        """
        if not HAS_FEEDPARSER:
            print("feedparser not installed. Install with: pip install feedparser")
            return []
        
        articles = []
        
        try:
            pub_name = self.extract_publication_name()
            rss_url = f"https://{pub_name}.substack.com/feed"
            
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                print(f"No entries found in RSS feed: {rss_url}")
                return articles
            
            for entry in feed.entries:
                # Extract content
                content = entry.get('summary', '')
                if 'content' in entry:
                    content = entry['content'][0]['value']
                
                article = {
                    'title': entry.get('title', 'Untitled'),
                    'subtitle': '',
                    'url': entry.get('link', ''),
                    'date': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'content': content,
                    'tags': [tag['term'] for tag in entry.get('tags', [])],
                    'slug': entry.get('id', '').split('/')[-1],
                }
                articles.append(article)
            
        except Exception as e:
            print(f"RSS scraping failed: {e}")
            return articles
        
        return articles
    
    def fetch_article_full_content(self, article_url: str) -> Optional[str]:
        """
        Fetch the full article content by scraping the page.
        Uses beautifulsoup if available.
        """
        if not HAS_BEAUTIFULSOUP:
            return None
        
        try:
            response = self.session.get(article_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the article content (Substack specific selectors)
            article_content = soup.find('div', {'class': re.compile('.*post-content.*')})
            if article_content:
                return str(article_content)
            
            return None
            
        except Exception as e:
            print(f"Failed to fetch full content from {article_url}: {e}")
            return None
    
    def scrape(self) -> List[Dict]:
        """
        Scrape Substack publication using available methods.
        Tries RSS first (most reliable), then API.
        """
        print(f"Scraping Substack publication: {self.publication_url}")
        
        # Try RSS first
        articles = self.scrape_via_rss()
        
        # If RSS fails, try API
        if not articles:
            print("RSS feed empty, trying API...")
            articles = self.scrape_via_api()
        
        if not articles:
            print("No articles found. Check the publication URL.")
            return articles
        
        print(f"Found {len(articles)} articles")
        
        # Optional: Fetch full content for each article
        # Uncomment to enable (slower but more complete):
        # for article in articles:
        #     full_content = self.fetch_article_full_content(article['url'])
        #     if full_content:
        #         article['content'] = full_content
        #     time.sleep(1)  # Rate limiting
        
        self.articles = articles
        return articles
    
    def sanitize_filename(self, filename: str) -> str:
        """Convert a string to a safe filename."""
        # Remove invalid filename characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces with underscores
        filename = re.sub(r'\s+', '_', filename)
        # Limit length
        filename = filename[:200]
        return filename
    
    def html_to_markdown(self, html_content: str) -> str:
        """
        Convert HTML content to markdown.
        Simple conversion - can be enhanced with html2text library.
        """
        if not html_content:
            return ""
        
        # Basic HTML to Markdown conversion
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
        
        # Paragraphs
        html_content = re.sub(r'</p>', '\n\n', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<p[^>]*>', '', html_content, flags=re.DOTALL)
        
        # Line breaks
        html_content = re.sub(r'<br\s*/?>', '\n', html_content)
        
        # Lists
        html_content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<[ou]l[^>]*>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'</[ou]l>', '', html_content, flags=re.DOTALL)
        
        # Remove remaining HTML tags
        html_content = re.sub(r'<[^>]+>', '', html_content)
        
        # Clean up whitespace
        html_content = re.sub(r'\n\n+', '\n\n', html_content)
        html_content = html_content.strip()
        
        return html_content
    
    def create_markdown_file(self, article: Dict) -> str:
        """Create a markdown file for an article with Obsidian-style frontmatter."""
        
        # Create safe filename
        safe_title = self.sanitize_filename(article['title'])
        filename = f"{safe_title}.md"
        filepath = self.articles_dir / filename
        
        # Prepare frontmatter
        date_str = article['date'][:10] if article['date'] else ''
        
        frontmatter = f"""---
title: {article['title']}
subtitle: {article.get('subtitle', '')}
author: {article.get('author', '')}
date: {date_str}
url: {article['url']}
tags: {json.dumps(article.get('tags', []))}
---

"""
        
        # Convert content to markdown
        markdown_content = self.html_to_markdown(article.get('content', ''))
        
        # Build full file content
        full_content = frontmatter + f"## {article['title']}\n\n"
        
        if article.get('subtitle'):
            full_content += f"*{article['subtitle']}*\n\n"
        
        full_content += f"**Published:** {date_str}\n"
        full_content += f"**Author:** {article.get('author', 'Unknown')}\n\n"
        full_content += f"**Source:** [{article['title']}]({article['url']})\n\n"
        
        full_content += "---\n\n"
        full_content += markdown_content
        
        # Add backlink references
        if article.get('tags'):
            full_content += "\n\n## Related Topics\n\n"
            for tag in article['tags']:
                safe_tag = self.sanitize_filename(tag)
                full_content += f"- [[{safe_tag}]]\n"
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return filename
    
    def generate_index(self):
        """Generate an index file for the vault."""
        
        if not self.articles:
            return
        
        index_content = f"""# {self.extract_publication_name().replace('_', ' ').title()} - Knowledge Base

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## About

This is an Obsidian vault containing archived content from:
**{self.publication_url}**

Total Articles: {len(self.articles)}

## Organization

- **articles/** - Individual article notes
- **metadata.json** - Raw article metadata

## Recent Articles

"""
        
        # Sort by date (newest first)
        sorted_articles = sorted(
            self.articles,
            key=lambda x: x.get('date', ''),
            reverse=True
        )[:20]
        
        for article in sorted_articles:
            date_str = article['date'][:10] if article['date'] else 'N/A'
            safe_title = self.sanitize_filename(article['title'])
            index_content += f"- [[{safe_title}]] ({date_str})\n"
        
        index_content += "\n## All Articles\n\n"
        
        for article in sorted_articles:
            date_str = article['date'][:10] if article['date'] else 'N/A'
            safe_title = self.sanitize_filename(article['title'])
            index_content += f"- [[{safe_title}]] - {article['title']}\n"
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"Index created: {self.index_file}")
    
    def save_metadata(self):
        """Save article metadata as JSON."""
        metadata = {
            'publication_url': self.publication_url,
            'publication_name': self.extract_publication_name(),
            'scraped_at': datetime.now().isoformat(),
            'total_articles': len(self.articles),
            'articles': self.articles
        }
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"Metadata saved: {self.metadata_file}")
    
    def generate(self):
        """Generate all markdown files and index."""
        print(f"\nGenerating markdown files in: {self.output_dir}")
        
        for i, article in enumerate(self.articles, 1):
            try:
                filename = self.create_markdown_file(article)
                print(f"  [{i}/{len(self.articles)}] Created: {filename}")
            except Exception as e:
                print(f"  [ERROR] Failed to create file for '{article['title']}': {e}")
        
        self.generate_index()
        self.save_metadata()
        
        print(f"\n✓ Completed! Vault created at: {self.output_dir}")
        print(f"\nTo use with Obsidian:")
        print(f"  1. Open Obsidian")
        print(f"  2. Create new vault and point to: {self.output_dir.absolute()}")
        print(f"  3. Open the INDEX.md file to start exploring!")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scrape Substack publications and create Obsidian vaults'
    )
    parser.add_argument(
        'url',
        help='Substack publication URL (e.g., https://example.substack.com)'
    )
    parser.add_argument(
        '-o', '--output',
        default='./substack_vault',
        help='Output directory for the vault (default: ./substack_vault)'
    )
    parser.add_argument(
        '--full-content',
        action='store_true',
        help='Fetch full article content (slower but more complete)'
    )
    
    args = parser.parse_args()
    
    # Normalize URL
    url = args.url
    if not url.startswith('http'):
        url = f'https://{url}'
    
    # Create scraper and run
    scraper = SubstackScraper(url, args.output)
    scraper.scrape()
    scraper.generate()


if __name__ == '__main__':
    main()
