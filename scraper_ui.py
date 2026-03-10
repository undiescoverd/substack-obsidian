#!/usr/bin/env python3
"""
Substack → Obsidian Scraper UI
Run locally:  streamlit run scraper_ui.py
Deploy:       https://streamlit.io/cloud
"""

import streamlit as st
import subprocess
import sys
import shutil
import tempfile
from datetime import date, timedelta
from pathlib import Path

st.set_page_config(page_title="Substack → Obsidian", page_icon="📚", layout="centered")

st.title("📚 Substack → Obsidian")
st.caption("Scrape any Substack archive and download it as an Obsidian vault")

with st.expander("How to use", expanded=False):
    st.markdown("""
1. Paste any Substack URL — e.g. `https://example.substack.com`
2. Pick the date range you want to scrape
3. Click **Run Scraper**
4. Download the zip when it's done
5. Unzip it, then open Obsidian → **Open folder as vault** → select the unzipped folder
""")

# --- Inputs ---
url = st.text_input(
    "Archive URL",
    placeholder="https://example.substack.com",
    help="Paste any Substack URL — homepage, archive, or post link. We'll find the archive automatically.",
)

all_articles = st.toggle("Get all articles", value=True)

if not all_articles:
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=date.today() - timedelta(days=365))
    with col2:
        end_date = st.date_input("To", value=date.today())
else:
    start_date = date(2010, 1, 1)
    end_date = date.today()

vault_name = st.text_input(
    "Vault name (used as folder name inside the zip)",
    value="substack_vault",
    placeholder="substack_vault",
)

def normalize_url(raw: str) -> str:
    """Accept any Substack URL and return the archive URL."""
    import re
    raw = raw.strip().rstrip("/").split("?")[0]

    # Handle reader app URLs: substack.com/@username/... -> username.substack.com
    match = re.match(r'https?://substack\.com/@([a-zA-Z0-9_-]+)', raw)
    if match:
        username = match.group(1)
        return f"https://{username}.substack.com/archive?sort=new"

    # Handle newsletter URLs: username.substack.com/anything -> username.substack.com/archive
    match = re.match(r'(https?://[a-zA-Z0-9_-]+\.substack\.com)', raw)
    if match:
        return match.group(1) + "/archive?sort=new"

    return raw  # return as-is, scraper will surface an error


# --- Run ---
if st.button("▶ Run Scraper", type="primary", use_container_width=True):
    if not url.strip():
        st.error("Please enter a Substack URL.")
    elif start_date > end_date:
        st.error("Start date must be before end date.")
    else:
        archive_url = normalize_url(url)
        st.caption(f"Using archive URL: `{archive_url}`")
        scraper_path = Path(__file__).parent / "substack_archive_scraper.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = str(Path(tmpdir) / vault_name.strip())

            cmd = [
                sys.executable, str(scraper_path),
                archive_url,
                "--start-date", str(start_date),
                "--end-date", str(end_date),
                "-o", output_dir,
            ]

            log_placeholder = st.empty()
            log_lines = []

            with st.spinner("Scraping articles..."):
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                for line in proc.stdout:
                    log_lines.append(line.rstrip())
                    log_placeholder.code("\n".join(log_lines[-40:]))
                proc.wait()

            if proc.returncode != 0:
                st.error("Scraper encountered an error. See the log above.")
            else:
                # Check articles were actually created
                articles_dir = Path(output_dir) / "articles"
                article_count = len(list(articles_dir.glob("*.md"))) if articles_dir.exists() else 0

                if article_count == 0:
                    st.warning("No articles were found for the selected date range. Try widening the date range.")
                else:
                    # Zip the vault
                    zip_path = Path(tmpdir) / vault_name.strip()
                    shutil.make_archive(str(zip_path), "zip", tmpdir, vault_name.strip())
                    zip_file = str(zip_path) + ".zip"

                    with open(zip_file, "rb") as f:
                        zip_bytes = f.read()

                    st.success(f"Done! Scraped **{article_count} articles**.")

                    st.download_button(
                        label="⬇️ Download Vault (zip)",
                        data=zip_bytes,
                        file_name=f"{vault_name.strip()}.zip",
                        mime="application/zip",
                        use_container_width=True,
                    )

                    st.info("""
**After downloading:**
1. Unzip the file
2. Open Obsidian
3. Click **Open folder as vault**
4. Select the unzipped folder
5. Open `INDEX.md` to start browsing
""")
