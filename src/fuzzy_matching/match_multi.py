"""Module for fuzzy matching on multiple characteristics."""

from pathlib import Path

import pandas as pd

from fuzzy_matching.matchers import (
    DistanceMatcher,
    NullMatcher,
    TimedeltaMatcher,
    VectorMatcher,
)


class MultiMatcher:
    """Fuzzy matching on multiple characteristics.

    Parameters
    ----------
    top_n : int
        Number of results to return.
    config : dict
        Dict specifying field name and matching algoritm.
    encryption_key : str
        Encryption key to use for storing data.
    storage_path : str, default="storage"
        Folder to store data in.
    """

    def __init__(
        self, top_n, config, encryption_key: str, storage_path="storage"
    ) -> None:
        # Create the storage path if needed.
        storage_path = Path(storage_path)
        storage_path.mkdir(parents=True, exist_ok=True)

        self._top_n = top_n

        self._matchers = {}
        for field, settings in config.items():
            algoritm = settings.get("algoritm").lower()
            weight = settings.get("weight", 1)
            dedupe = settings.get("dedupe", False)

            if algoritm in DistanceMatcher.ALGORITMS:
                self._matchers[field] = DistanceMatcher(
                    field, weight, dedupe, encryption_key, storage_path, algoritm
                )

            elif algoritm == "vector":
                self._matchers[field] = VectorMatcher(
                    field, weight, encryption_key, storage_path
                )

            elif algoritm == "timedelta":
                date_format = settings.get("format", "%d-%m-%Y")
                self._matchers[field] = TimedeltaMatcher(
                    field, weight, encryption_key, storage_path, date_format
                )

            elif algoritm == "null":
                self._matchers[field] = NullMatcher(field, encryption_key, storage_path)

            else:
                raise TypeError(f"Unknown matching algoritm: {algoritm}")

    def create(self, data: pd.DataFrame, id_column: str) -> None:
        """Add data to the matching set."""
        if id_column not in data.columns:
            raise RuntimeError("Missing ID column {id_column} in the data")
        data = data.rename(columns={id_column: "id"})

        missing = set(self._matchers) - set(data.columns)
        if missing:
            raise RuntimeError("Missing columns in the data: " + ".".join(missing))

        for field, matcher in self._matchers.items():
            matcher.create(data[["id", field]])

    def get(self, target: dict) -> pd.DataFrame:
        """Match records from the matching set."""
        results = []

        # Get similarity scores from the individual matchers.
        for field, matcher in self._matchers.items():
            result = matcher.get(target[field])
            if result is None:
                raise RuntimeError(f"No results for {field}; aborting...")

            results.append(result)

        results = pd.concat(results, axis=1, join="inner")
        columns = [c for c in results.columns if c.startswith("similarity")]
        results["similarity"] = results[columns].sum(axis=1)
        results = results.nlargest(self._top_n, columns="similarity")

        return results.sort_values(by="similarity", ascending=False)

    def delete(self) -> None:
        """Delete all matching data."""
        for field, matcher in self._matchers.items():
            matcher.delete(field)
