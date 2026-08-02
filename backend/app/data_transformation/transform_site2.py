# backend/app/data_transformation/transform_site2.py
"""
Source-specific transformer: Source 2 -> canonical schema.

PORTFOLIO VERSION NOTICE
-------------------------
Source 2 is the structurally most complex of the three data sources: its
raw output mixes several layout patterns for the same conceptual fields, so
the production transformer has to disambiguate which raw label maps to
which canonical field depending on context, and reconcile duplicate/partial
values before writing to the canonical schema (see `master_keys.py`).

The real column mapping and disambiguation rules were built by
reverse-engineering this source's actual output over time, so they are
considered proprietary implementation detail and have been omitted from
this portfolio version.

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


class VehicleDataTransformer_site2:
    """Transforms raw Source 2 data into the canonical schema (demo stub)."""

    def __init__(self, config: VehicleDataConfig):
        self.config = config

    def transform(self, df_input: pd.DataFrame) -> pd.DataFrame:
        """Same signature as production: raw ['Key', 'Value'] DataFrame in,
        canonical ['Key', 'Value'] DataFrame out."""
        rng = random.Random(2)
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


DEFAULT_CONFIG_2 = VehicleDataConfig(
    column_mapping={
        "Example raw label A": "make",
        "Example raw label B": "type",
    },
    ordered_keys=MASTER_ORDERED_KEYS,
)
