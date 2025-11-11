import json
from glob import glob

def merge_exam_packages(input_folder, output_file):
    """
    Merges multiple JSON exam packages into a single JSON structure.
    Supports both 'essay': {...} and 'essay': [{...}] formats.
    Searches recursively for all .json files.
    """
    merged_data = {
        "merged_source": "Machine Vision Exams Compilation (2014–2020)",
        "level": "advanced_undergraduate",
        "packages": [],
        "mcqs": [],
        "essay": [],
        "notes": "Merged automatically using Question Bank Generator"
    }

    # Search recursively for JSON files
    for file_path in glob(f"{input_folder}/**/*.json", recursive=True):
        with open(file_path, "r", encoding="utf-8") as f:
            pkg = json.load(f)

            merged_data["packages"].append(pkg.get("package_id", "unknown"))

            # Merge MCQs if any
            if "mcqs" in pkg and isinstance(pkg["mcqs"], list):
                merged_data["mcqs"].extend(pkg["mcqs"])

            # Merge essays — handle object or list
            essay_data = pkg.get("essay")
            if isinstance(essay_data, dict):
                merged_data["essay"].append(essay_data)
            elif isinstance(essay_data, list):
                merged_data["essay"].extend(essay_data)

    # Write output JSON
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(merged_data, out, indent=2, ensure_ascii=False)

    print(f"Merged {len(merged_data['packages'])} packages into {output_file}")
    print(f"Total essays: {len(merged_data['essay'])}")
    print(f"Total MCQs: {len(merged_data['mcqs'])}")
    
# ✅ Run this
merge_exam_packages(".", "merged_machine_vision_exams.json")
