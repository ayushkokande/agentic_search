import pandas as pd
from typing import List, Any

def places_to_dataframe(places: List[dict]) -> pd.DataFrame:
    """
    Format list of place dicts into a pandas DataFrame for display.
    """
    if not places:
        return pd.DataFrame()
    # Select relevant columns for table
    columns = ["name", "address", "distance", "open_hours", "trust"]
    df = pd.DataFrame(places)
    return df[columns]
