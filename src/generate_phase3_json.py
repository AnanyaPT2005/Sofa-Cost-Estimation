import json
import os


# Read detection result
with open("outputs/detection.json", "r") as f:
    detection = json.load(f)

# Verify that a sofa was detected
if detection["object"] != "couch":
    print("No sofa detected.")
    exit()

# Create Phase 3 JSON
phase3 = {
    "sofa_type": "Straight",
    "seat_count": 3,

    "seat": {
        "width_ratio": 0.78,
        "depth_ratio": 0.44,
        "height_ratio": 0.22
    },

    "backrest": {
        "width_ratio": 0.79,
        "height_ratio": 0.51,
        "thickness_ratio": 0.11
    },

    "armrest": {
        "height_ratio": 0.61,
        "width_ratio": 0.12,
        "depth_ratio": 0.43
    },

    "legs": {
        "count": 4
    },

    "materials": {
        "armrest_frame": "Wood",
        "backrest_frame": "Wood",
        "fabric": "Fabric",
        "leg": "Unknown"
    }
}

# Save Phase 3 JSON
os.makedirs("outputs", exist_ok=True)

with open("outputs/phase3.json", "w") as f:
    json.dump(phase3, f, indent=4)

print("phase3.json created successfully!")