# backend/app/services/transform_service.py
"""
Transformation orchestration + multi-source merge/priority logic.

PORTFOLIO VERSION NOTICE
-------------------------
`apply_transformations` (dispatch to the 3 source-specific transformers) is
unchanged generic orchestration code.

`merge_and_prioritize` below keeps the real production structure (build a
DataFrame indexed by the 97 canonical keys, merge each source's values in,
apply a per-row priority function, sort back into canonical order) but its
field-level priority rules have been simplified for the portfolio version.

In production, `get_final_value` encodes field-specific business rules
learned from real-world discrepancies between the 3 sources: e.g. detecting
hybrid fuel-type strings, deciding which source wins for specific fields
(overriding the general priority order), and a post-processing pass that
reformats emissions values differently depending on the vehicle's emissions
standard. Those rules are considered proprietary implementation detail and
have been omitted from this portfolio version.

# Proprietary transformation logic omitted from portfolio version.

Below, `get_final_value` uses a single generic priority order (Source 2 >
Source 1 > Source 3) for every field, with no field-specific overrides or
post-processing, so the merge step remains runnable as a demo.
"""
import pandas as pd
from typing import Dict, Optional
import logging

from ..data_transformation.transform_site1 import VehicleDataTransformer_site1, DEFAULT_CONFIG_1
from ..data_transformation.transform_site2 import VehicleDataTransformer_site2, DEFAULT_CONFIG_2
from ..data_transformation.transform_site3 import VehicleDataTransformer_site3, DEFAULT_CONFIG_3
from ..data_transformation.master_keys import MASTER_ORDERED_KEYS

transformer1 = VehicleDataTransformer_site1(DEFAULT_CONFIG_1)
transformer2 = VehicleDataTransformer_site2(DEFAULT_CONFIG_2)
transformer3 = VehicleDataTransformer_site3(DEFAULT_CONFIG_3)

logger = logging.getLogger(__name__)


def apply_transformations(
    scraped_data: Dict[str, Optional[pd.DataFrame]]
) -> Dict[str, Optional[pd.DataFrame]]:
    """Applies the source-specific transformer to each scraped DataFrame."""
    transformed_data = {}

    if "site1" in scraped_data and scraped_data["site1"] is not None and not scraped_data["site1"].empty:
        transformed_data["site1"] = transformer1.transform(scraped_data["site1"])
    else:
        transformed_data["site1"] = None

    if "site2" in scraped_data and scraped_data["site2"] is not None and not scraped_data["site2"].empty:
        transformed_data["site2"] = transformer2.transform(scraped_data["site2"])
    else:
        transformed_data["site2"] = None

    if "site3" in scraped_data and scraped_data["site3"] is not None and not scraped_data["site3"].empty:
        transformed_data["site3"] = transformer3.transform(scraped_data["site3"])
    else:
        transformed_data["site3"] = None

    return transformed_data


def merge_and_prioritize(
    transformed_data: Dict[str, Optional[pd.DataFrame]]
) -> pd.DataFrame:
    """Merges the transformed DataFrames and applies the priority logic."""
    merged_df = pd.DataFrame(MASTER_ORDERED_KEYS, columns=['Key'])

    for i in range(1, 4):
        site_name = f'site{i}'
        df = transformed_data.get(site_name)
        col_name = f'Valor Sitio {i}'

        if df is not None and not df.empty:
            df_renamed = df[['Key', 'Value']].rename(columns={'Value': col_name})
            merged_df = pd.merge(merged_df, df_renamed, on='Key', how='left')
        else:
            merged_df[col_name] = "-"

    merged_df = merged_df.fillna("-")

    def get_final_value(row):
        """Simplified demo priority rule: Source 2 > Source 1 > Source 3,
        applied uniformly to every field (no field-specific overrides)."""
        s1 = row.get('Valor Sitio 1')
        s2 = row.get('Valor Sitio 2')
        s3 = row.get('Valor Sitio 3')

        if s2 is not None and str(s2) not in ['-', 'None']:
            return s2
        if s1 is not None and str(s1) not in ['-', 'None']:
            return s1
        if s3 is not None and str(s3) not in ['-', 'None']:
            return s3

        return "-"

    merged_df['Valor Final'] = merged_df.apply(get_final_value, axis=1)

    merged_df['Key'] = pd.Categorical(merged_df['Key'], categories=MASTER_ORDERED_KEYS, ordered=True)
    merged_df = merged_df.sort_values("Key").reset_index(drop=True)

    final_columns = ['Key', 'Valor Sitio 1', 'Valor Sitio 2', 'Valor Sitio 3', 'Valor Final']
    return merged_df[final_columns]
