import json
import os

def load_mapping(mapping_path):
    if not os.path.exists(mapping_path):
        print(f"⚠️ Mapping file not found: {mapping_path}. Using default mapping.")
        return {
            "A": {"a": "a", "b": "b", "c": "c", "d": "d"},
            "B": {"a": "b", "b": "c", "c": "d", "d": "a"}
        }
    with open(mapping_path, 'r') as f:
        return json.load(f)