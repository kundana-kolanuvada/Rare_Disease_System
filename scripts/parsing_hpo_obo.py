import os
import json

def parse_hpo_obo(obo_file_path):
    """
    Parses the HPO OBO file to extract HPO ID -> HPO name mappings.
    """
    hpo_terms = {}
    with open(obo_file_path, 'r', encoding='utf-8') as f:
        current_id = None
        current_name = None

        for line in f:
            line = line.strip()

            if line == '[Term]':
                if current_id and current_name:
                    hpo_terms[current_id] = current_name
                current_id = None
                current_name = None

            elif line.startswith('id:'):
                current_id = line.split(':', 1)[1].strip()

            elif line.startswith('name:'):
                current_name = line.split(':', 1)[1].strip()

            elif line.startswith('[Typedef]'):
                current_id = None
                current_name = None

        # Add last term
        if current_id and current_name:
            hpo_terms[current_id] = current_name

    return hpo_terms


def parse_hpo_annotations(annotations_file_path):
    """
    Parses phenotype.hpoa and groups HPO IDs by disease name.
    Ignores qualifier, frequency, onset (MVP).
    """
    disease_hpo_map = {}

    with open(annotations_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split('\t')

            # parts[1] -> disease_name
            # parts[3] -> HPO ID
            if len(parts) >= 4 and parts[3].startswith('HP:'):
                disease_name = parts[1].strip()
                hpo_id = parts[3].strip()

                if disease_name not in disease_hpo_map:
                    disease_hpo_map[disease_name] = set()

                disease_hpo_map[disease_name].add(hpo_id)

    return disease_hpo_map


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    obo_file = os.path.join(script_dir, '..', 'data', 'raw', 'hp.obo')
    annotations_file = os.path.join(script_dir, '..', 'data', 'raw', 'phenotype.hpoa')
    output_json_file = os.path.join(script_dir, '..', 'data', 'diseases.json')

    print(f"Parsing HPO OBO file: {obo_file}")
    hpo_id_to_name = parse_hpo_obo(obo_file)
    print(f"Loaded {len(hpo_id_to_name)} HPO terms")

    print(f"Parsing HPO annotations file: {annotations_file}")
    disease_hpo_map = parse_hpo_annotations(annotations_file)
    print(f"Loaded annotations for {len(disease_hpo_map)} diseases")

    # Final structure optimized for matching
    processed_diseases = []

    for disease_name, hpo_ids in disease_hpo_map.items():
        hpo_terms = [
            {
                "hpo_id": hpo_id,
                "hpo_name": hpo_id_to_name.get(hpo_id, "Unknown HPO Name")
            }
            for hpo_id in sorted(hpo_ids)
        ]

        processed_diseases.append({
            "disease_name": disease_name,
            "hpo_terms": hpo_terms
        })

    print(f"Saving processed disease data to {output_json_file}")
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(processed_diseases, f, indent=2, ensure_ascii=False)

    print("Done.")


if __name__ == "__main__":
    main()
