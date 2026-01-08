import json
import re
from pathlib import Path

HPO_PATTERN = re.compile(r"^HP:\d{7}$")

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "backend"
    / "data"
    / "diseases.json"
)

def clean_and_overwrite():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        diseases = json.load(f)

    cleaned_diseases = []
    removed_count = 0

    for disease in diseases:
        disease_name = disease.get("disease_name", "").strip()
        hpo_terms = disease.get("hpo_terms", [])

        if not disease_name or not isinstance(hpo_terms, list):
            removed_count += 1
            continue

        seen_hpo_ids = set()
        cleaned_hpo_terms = []

        for hpo in hpo_terms:
            if not isinstance(hpo, dict):
                continue

            hpo_id = hpo.get("hpo_id", "").strip()
            hpo_name = hpo.get("hpo_name", "").strip()

            # Validate HPO ID format
            if not HPO_PATTERN.match(hpo_id):
                continue

            # Remove duplicate HPO IDs
            if hpo_id in seen_hpo_ids:
                continue

            seen_hpo_ids.add(hpo_id)

            cleaned_hpo_terms.append({
                "hpo_id": hpo_id,
                "hpo_name": hpo_name
            })

        # Remove disease if no valid HPO terms
        if not cleaned_hpo_terms:
            removed_count += 1
            continue

        cleaned_diseases.append({
            "disease_name": disease_name,
            "hpo_terms": cleaned_hpo_terms
        })

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned_diseases, f, indent=2, ensure_ascii=False)

    print("✅ Dataset cleaned and overwritten successfully\n")
    print(f"Original diseases count : {len(diseases)}")
    print(f"Remaining diseases      : {len(cleaned_diseases)}")
    print(f"Diseases deleted        : {removed_count}")


if __name__ == "__main__":
    clean_and_overwrite()
