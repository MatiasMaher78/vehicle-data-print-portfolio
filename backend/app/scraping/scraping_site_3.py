# backend/app/scraping/scraping_site_3.py
"""
Scraper for Source 3.

PORTFOLIO VERSION NOTICE
-------------------------
This is a simplified example scraper for the portfolio version. The real
implementation contains a table selector and a header-to-canonical-field
mapping reverse-engineered from Source 3's actual page structure, which are
considered proprietary implementation detail and have been omitted here.

The example below illustrates the same pattern (BaseScraper subclass +
BeautifulSoup table parsing -> pandas DataFrame of Key/Value pairs) against
a generic, hypothetical HTML structure instead.
"""

import pandas as pd

from .base_scraper import BaseScraper


class Site3Scraper(BaseScraper):
    """Example table-based scraper for Source 3."""

    def scrape(self, url: str) -> pd.DataFrame:
        try:
            soup = self.fetch_page(url)
        except Exception:
            return pd.DataFrame(columns=["Key", "Value"])

        extracted_data = []

        # Example generic structure: a single details table with header/data
        # cell pairs per row, e.g. <table class="details"><tr><th>Body type</th><td>Sedan</td></tr>...
        details_table = soup.find("table", class_="details")
        if details_table:
            for row in details_table.find_all("tr"):
                header = row.find("th")
                data_cell = row.find("td")
                if header and data_cell:
                    extracted_data.append((header.get_text(strip=True), data_cell.get_text(strip=True)))

        return pd.DataFrame(extracted_data, columns=["Key", "Value"])
