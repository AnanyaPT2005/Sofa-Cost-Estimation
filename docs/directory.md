project_root/
│
├── inputs/
│ └── phase.json # Dummy input from image processing
│
├── outputs/
│ └── scaled_sofa_components.csv # Generated after scaling
├── data/
│ └── renamed_sofa_components.json # Original sofa components data
│ └── sofa_metadata.json # Metadata for the sofa template
│
├── docs/
│ └── directory.md
│ └── ext_ver2_proposal.md
│ └── csv.md
│
├── scripts/
│ └── scaling/
│ ├── scale.py # Main entry point
│ ├── seat_scaler.py
│ ├── backrest_scaler.py
│ ├── armrest_scaler.py
│ └── ... # Other scaling utilities
│
└── ...
