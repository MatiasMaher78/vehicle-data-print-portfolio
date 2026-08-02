# backend/app/scraping/scraping_site_2.py
"""
Scraper for Source 2.

PORTFOLIO VERSION NOTICE
-------------------------
This is a simplified example scraper for the portfolio version. Source 2 is
the structurally most complex of the three sources, and the real
implementation contains CSS selectors and disambiguation rules
reverse-engineered from its actual page structure, which are considered
proprietary implementation detail and have been omitted here.

The example below illustrates the same pattern (BaseScraper subclass +
BeautifulSoup parsing -> pandas DataFrame of Key/Value pairs), including an
optional argument for a source-specific option (mirroring the production
`transmission_manual` option), against a generic, hypothetical HTML
structure instead.
"""

import pandas as pd

from .base_scraper import BaseScraper


class Site2Scraper(BaseScraper):
    def scrape(self, url, transmission_manual=None):
        soup = self.fetch_page(url)
        data = []

        # Example generic structure: label/value pairs in adjacent table
        # cells, e.g.:
        #   <tr><td class="field-label">Engine code</td><td class="field-value">EXAMPLE123</td></tr>
        for row in soup.find_all("tr"):
            label_el = row.find("td", class_="field-label")
            value_el = row.find("td", class_="field-value")
            if label_el and value_el:
                data.append((label_el.get_text(strip=True), value_el.get_text(strip=True)))

        # `transmission_manual` mirrors the production option that selects
        # between manual/automatic transmission variants when a source
        # exposes multiple entries for the same base vehicle. Omitted here.
        _ = transmission_manual

        return pd.DataFrame(data, columns=["Key", "Value"])
