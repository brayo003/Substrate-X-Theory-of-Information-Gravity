import numpy as np
import pandas as pd
from enum import Enum

class DomainType(Enum):
    FINANCIAL = 1
    BIOLOGICAL = 2

class DataCoupler:
    def __init__(self, domain_type: DomainType):
        self.domain_type = domain_type
        self.data = None

    def ingest_data(self, data):
        if not isinstance(data, pd.DataFrame):
            raise ValueError("DataCoupler.ingest_data requires a pandas DataFrame")

        self.data = data.copy()
        self.data.columns = [str(c) for c in self.data.columns]

        feature_columns = self._auto_detect_features()

        metrics = {
            "mean": self.data[feature_columns].mean().to_dict(),
            "std": self.data[feature_columns].std().to_dict(),
            "var": self.data[feature_columns].var().to_dict(),
            "features_used": feature_columns
        }

        return SimpleMetricObject(metrics)

    def _auto_detect_features(self):
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        exclude_keywords = ["date", "time"]

        return [
            col for col in numeric_cols
            if not any(kw in col.lower() for kw in exclude_keywords)
        ]

class SimpleMetricObject:
    def __init__(self, metrics):
        self.metrics = metrics

    def output_metrics(self):
        return self.metrics
