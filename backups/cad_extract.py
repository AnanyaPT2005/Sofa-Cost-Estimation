import os
import trimesh
import pandas as pd

# =========================
# FOLDERS
# =========================

MODEL_FOLDER = "models"
OUTPUT_CSV = "data/cad.csv"

# =========================
# STORE EXTRACTED FEATURES
# =========================

cad_data = []

# =========================
# LOOP THROUGH ALL CAD FILES
# =========================

for file_name in os.listdir(MODEL_FOLDER):

    # Only process OBJ and STL files
    if file_name.endswith(".obj") or file_name.endswith(".stl"):

        file_path = os.path.join(MODEL_FOLDER, file_name)

        try:
            # Load mesh
            mesh = trimesh.load(file_path)

            # Bounding box dimensions
            bounds = mesh.bounds

            length = bounds[1][0] - bounds[0][0]
            height = bounds[1][1] - bounds[0][1]
            depth = bounds[1][2] - bounds[0][2]

            # Geometric features
            volume = mesh.volume
            surface_area = mesh.area

            # Save features
            cad_data.append({
                "cad_file": file_name,
                "length": round(length, 2),
                "height": round(height, 2),
                "depth": round(depth, 2),
                "volume": round(volume, 2),
                "surface_area": round(surface_area, 2)
            })

            print(f"Processed: {file_name}")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

# =========================
# SAVE TO CSV
# =========================

df = pd.DataFrame(cad_data)

df.to_csv(OUTPUT_CSV, index=False)

print("\nCAD feature extraction completed.")
print(f"Saved to: {OUTPUT_CSV}")