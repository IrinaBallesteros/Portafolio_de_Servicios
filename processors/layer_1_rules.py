import pandas as pd
import re
from .base import DataProcessor
from core.column_mapper import map_columns


class Layer1Rules(DataProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.copy()

        if 'nombre' in df_clean.columns:
            df_clean['nombre'] = df_clean['nombre'].astype(str).str.strip().str.title()

        if 'cedula' in df_clean.columns:
            df_clean['cedula'] = df_clean['cedula'].apply(
                lambda x: re.sub(r'[-.,\s]', '', str(x).split('.')[0]) if pd.notna(x) else ""
            )


        return df_clean