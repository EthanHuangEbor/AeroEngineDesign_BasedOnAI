"""CSV export helpers for reproducible MTA-VHEP result tables."""

from pathlib import Path

import pandas as pd


def write_dataframe_csv(df: pd.DataFrame, path: Path) -> None:
    """Write a DataFrame to CSV with LF row terminators for downstream tools."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, lineterminator="\n")
