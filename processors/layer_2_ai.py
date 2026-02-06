import pandas as pd
from rapidfuzz import process, fuzz
from .base import DataProcessor


class Layer2AI(DataProcessor):
    def __init__(self):
        self.common_domains = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com"]

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df_ai = df.copy()

        if 'email' in df_ai.columns:
            df_ai['email'] = df_ai['email'].apply(self._fix_email)

        return df_ai

    def _fix_email(self, email):
        if pd.isna(email) or "@" not in str(email): return email
        user, domain = str(email).lower().split('@')
        match = process.extractOne(domain, self.common_domains, scorer=fuzz.WRatio)
        if match and match[1] > 85:
            return f"{user}@{match[0]}"
        return email