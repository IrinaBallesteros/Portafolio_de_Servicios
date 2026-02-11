import pandas as pd

class DataProcessor:
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("Cada módulo debe implementar su propio método process")