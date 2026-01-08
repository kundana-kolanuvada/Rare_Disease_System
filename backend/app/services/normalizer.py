import re
from typing import List, Iterable

# Valid HPO ID pattern
HPO_PATTERN = re.compile(r"^HP:\d{7}$")

def normalize_hpo_ids(hpo_ids: Iterable[str]) -> List[str]:
    """
    Normalize user-provided HPO IDs:
    - safely handle None / empty input
    - trim spaces
    - convert to uppercase
    - remove duplicates
    - discard invalid formats
    - return stable, sorted output
    """

    if not hpo_ids:
        return []

    normalized = set()

    for hpo in hpo_ids:
        if not isinstance(hpo, str):
            continue

        clean = hpo.strip().upper()

        if HPO_PATTERN.match(clean):
            normalized.add(clean)

    return sorted(normalized)
