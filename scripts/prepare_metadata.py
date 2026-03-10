import xml.etree.ElementTree as ET
import json
import os

# Define paths to raw XML files
RAW_DATA_DIR = "backend/data/raw"
OUTPUT_FILE = "backend/data/enriched_metadata.json"

FILES = {
    "ages": os.path.join(RAW_DATA_DIR, "en_product9_ages.xml"),
    "prev": os.path.join(RAW_DATA_DIR, "en_product9_prev.xml"),
    "pheno": os.path.join(RAW_DATA_DIR, "en_product4 (1).xml"),
    "genes": os.path.join(RAW_DATA_DIR, "en_product6.xml"),
    "funct": os.path.join(RAW_DATA_DIR, "en_funct_consequences.xml")
}

def parse_xml(file_path):
    if not os.path.exists(file_path):
        print(f"Warning: File not found: {file_path}")
        return None
    print(f"Parsing {file_path}...")
    return ET.parse(file_path).getroot()

def enrich_data():
    # Master dictionary: OrphaCode -> Metadata
    enriched_data = {}

    # 1. Parse Ages and Inheritance (en_product9_ages.xml)
    root = parse_xml(FILES["ages"])
    if root is not None:
        for disorder in root.findall(".//Disorder"):
            orpha_code = disorder.find("OrphaCode").text
            name = disorder.find("Name").text
            
            # Extract Onset
            onsets = [on.find("Name").text for on in disorder.findall(".//AverageAgeOfOnset/Name/..")]
            
            # Extract Inheritance
            inheritances = [inh.find("Name").text for inh in disorder.findall(".//TypeOfInheritance/Name/..")]
            
            enriched_data[orpha_code] = {
                "orpha_code": orpha_code,
                "name": name,
                "onset": onsets,
                "inheritance": inheritances,
                "prevalence": [],
                "symptoms": [],
                "genes": []
            }

    # 2. Parse Prevalence (en_product9_prev.xml)
    root = parse_xml(FILES["prev"])
    if root is not None:
        for disorder in root.findall(".//Disorder"):
            orpha_code = disorder.find("OrphaCode").text
            if orpha_code in enriched_data:
                prevalences = []
                for prev in disorder.findall(".//Prevalence"):
                    p_class = prev.find(".//PrevalenceClass/Name")
                    if p_class is not None:
                        prevalences.append(p_class.text)
                enriched_data[orpha_code]["prevalence"] = list(set(prevalences))

    # 3. Parse Genes (en_product6.xml)
    root = parse_xml(FILES["genes"])
    if root is not None:
        for disorder in root.findall(".//Disorder"):
            orpha_code_elem = disorder.find("OrphaCode")
            if orpha_code_elem is None: continue
            orpha_code = orpha_code_elem.text
            
            if orpha_code in enriched_data:
                # Correct way to find Symbols within Genes nested in Disorder
                genes = [symbol.text for symbol in disorder.findall(".//Gene/Symbol") if symbol is not None]
                enriched_data[orpha_code]["genes"] = list(set(genes))

    # 4. Parse Phenotypes & Frequencies (en_product4 (1).xml)
    root = parse_xml(FILES["pheno"])
    if root is not None:
        for disorder in root.findall(".//Disorder"):
            orpha_code = disorder.find("OrphaCode").text
            if orpha_code in enriched_data:
                symptoms = []
                for assoc in disorder.findall(".//HPODisorderAssociation"):
                    hpo_id = assoc.find(".//HPOId").text
                    hpo_name = assoc.find(".//HPOTerm").text
                    freq = assoc.find(".//HPOFrequency/Name").text if assoc.find(".//HPOFrequency/Name") is not None else "Unknown"
                    symptoms.append({
                        "hpo_id": hpo_id,
                        "hpo_name": hpo_name,
                        "frequency": freq
                    })
                enriched_data[orpha_code]["symptoms"] = symptoms

    # Save to JSON
    print(f"Saving enriched metadata for {len(enriched_data)} diseases to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched_data, f, indent=2)
    print("Task 1 Complete!")

if __name__ == "__main__":
    enrich_data()
