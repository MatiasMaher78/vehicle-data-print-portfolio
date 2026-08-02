# backend/app/data_transformation/transform_site1.py
"""
Source-specific transformer: Source 1 -> canonical schema.

PORTFOLIO VERSION NOTICE
-------------------------
In production, this module normalizes the raw key/value pairs scraped from
Source 1 into the 97-field canonical schema (see `master_keys.py`). That
involves, among other steps:
  - Renaming source-specific labels to canonical field keys.
  - Cleaning/normalizing raw text values (units, decimal separators, noise).
  - Deriving computed fields that Source 1 does not expose directly
    (e.g. axle count/track from a combined raw field, mass distribution
    across axles, max trailer mass).
  - Detecting and formatting the emissions standard / exhaust category
    from source-specific codes.
  - Parsing NEDC and WLTP consumption values into their individual
    per-field slots (urban/extra-urban/combined, low/medium/high/max).

The real column mapping and parsing rules were built by reverse-engineering
this source's actual output over time, so they are considered proprietary
implementation detail and have been omitted from this portfolio version.

# Proprietary transformation logic omitted from portfolio version.

Below is a structurally-equivalent mock: same public class/method interface
as production, but returning example data shaped like a real transformer
output, so the rest of the pipeline (merge, export) remains runnable as a
demo.
"""

import random
from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from .master_keys import MASTER_ORDERED_KEYS


@dataclass
class VehicleDataConfig:
    """Configuration for a source-specific transformer."""
    column_mapping: Dict[str, str]
    ordered_keys: List[str]


class VehicleDataTransformer_site1:
    """Transforms raw Source 1 data into the canonical schema (demo stub)."""

    def __init__(self, config: VehicleDataConfig):
        self.config = config

    def transform(self, df_input: pd.DataFrame) -> pd.DataFrame:
        """Same signature as production: raw ['Key', 'Value'] DataFrame in,
        canonical ['Key', 'Value'] DataFrame out."""
        rng = random.Random(1)
        rows = [
            {"Key": key, "Value": self._example_value(key, rng)}
            for key in self.config.ordered_keys
        ]
        return pd.DataFrame(rows, columns=["Key", "Value"])

    @staticmethod
    def _example_value(key: str, rng: random.Random) -> str:
        """Placeholder value generator, only used for demo purposes."""
        if rng.random() < 0.3:
            return "-"
        return f"demo-{key}"


DEFAULT_CONFIG_1 = VehicleDataConfig(
    column_mapping={
        "Example raw label A": "make",
        "Example raw label B": "type",
    },
    ordered_keys=MASTER_ORDERED_KEYS,
)
