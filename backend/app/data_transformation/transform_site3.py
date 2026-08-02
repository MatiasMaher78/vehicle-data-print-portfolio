# backend/app/data_transformation/transform_site3.py
"""
Source-specific transformer: Source 3 -> canonical schema.

PORTFOLIO VERSION NOTICE
-------------------------
Source 3 exposes a simpler, table-based layout compared to the other two
sources. In production, this module still has to rename source-specific
headers to canonical field keys and clean the extracted text values before
writing to the canonical schema (see `master_keys.py`).

The real header mapping and cleaning rules were built by reverse-engineering
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


class VehicleDataTransformer_site3:
    """Transforms raw Source 3 data into the canonical schema (demo stub)."""

    def __init__(self, config: VehicleDataConfig):
        self.config = config

    def transform(self, df_input: pd.DataFrame) -> pd.DataFrame:
        """Same signature as production: raw ['Key', 'Value'] DataFrame in,
        canonical ['Key', 'Value'] DataFrame out."""
        rng = random.Random(3)
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


DEFAULT_CONFIG_3 = VehicleDataConfig(
    column_mapping={
        "Example raw label A": "make",
        "Example raw label B": "type",
    },
    ordered_keys=MASTER_ORDERED_KEYS,
)
