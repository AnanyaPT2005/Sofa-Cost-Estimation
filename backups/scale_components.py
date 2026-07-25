import pandas as pd

CSV_PATH = "data/sofa_bodies_labeled.csv"
INPUT_LENGTH_MM = 1800
REF_LENGTH_MM = 1610

df = pd.read_csv(CSV_PATH)
ext = df[(df["visibility"] == "External") & (df["measurement_type"] == "Continuous")].copy()

scale = INPUT_LENGTH_MM / REF_LENGTH_MM

# scale dimensions
ext["scaled_L"] = (ext["L_mm"] * scale).round(2)
ext["scaled_W"] = (ext["W_mm"] * scale).round(2)
ext["scaled_H"] = (ext["H_mm"] * scale).round(2)
ext["scaled_volume"] = (ext["volume_mm3"] * (scale**3)).round(2)

# scale positions
for col in ["min_x_mm","min_y_mm","min_z_mm",
            "max_x_mm","max_y_mm","max_z_mm",
            "center_x_mm","center_y_mm","center_z_mm"]:
    ext[f"scaled_{col}"] = (ext[col] * scale).round(2)

out = ext[["body","Category","appearance",
           "scaled_L","scaled_W","scaled_H","scaled_volume",
           "scaled_min_x_mm","scaled_min_y_mm","scaled_min_z_mm",
           "scaled_max_x_mm","scaled_max_y_mm","scaled_max_z_mm",
           "scaled_center_x_mm","scaled_center_y_mm","scaled_center_z_mm"]]

out.to_csv("outputs/scaled_external.csv", index=False)
print(f"Scale factor: {scale:.4f}")
print(out.to_string())