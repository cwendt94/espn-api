# Helper functions for json parsing and power rankings

from typing import Any, List


def json_parsing(obj: Any, key: str) -> Any:
    """Recursively pull values of specified key from nested JSON."""
    arr: List[Any] = []

    def extract(obj: Any, arr: List[Any], key: str) -> List[Any]:
        """Return all matching values in an object."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict)) or (
                    isinstance(v, (list)) and v and isinstance(v[0], (list, dict))
                ):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results[0] if results else results
