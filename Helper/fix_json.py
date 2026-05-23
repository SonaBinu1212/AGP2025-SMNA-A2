"""
COSC2671 Social Media and Network Analytics
@author Sona Binu, S4137524, RMIT University, 2026

Quick utility script I wrote to validate and clean the raw JSON file
after fetching. Sometimes the API returns comments with weird control
characters that break json.loads(), so this strips them out and saves
a clean version if needed.
"""

import json
import re

# Read the raw file
with open('../data/agp2025.json', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

try:
    data = json.loads(content)
    print("JSON is valid!")
except json.JSONDecodeError as e:
    print(f"JSON error at: {e}")

    # Strip out control characters that can sneak in from API responses
    content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', content)

    try:
        data = json.loads(content)
        print("Fixed! Saving clean version...")
        with open('../data/agp2025_fixed.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Saved to ../data/agp2025_fixed.json")
    except json.JSONDecodeError as e2:
        print(f"Could not fix: {e2}")
        print("Need to re-fetch data")