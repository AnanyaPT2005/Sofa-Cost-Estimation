# ============================================================
# PHASE 4A - EXTERNAL SCALING
# Scales seat_top and seat_front
# Generates:
#   scaled_external.json
#   scaled_external.csv
#   scaled_sofa_metadata.csv
# ============================================================

import pandas as pd
import json

# ============================================================
# USER INPUT
# ============================================================

print("========== PHASE 4A ==========")

USER_LENGTH = float(input("Enter Overall Length (mm): "))
USER_DEPTH = float(input("Enter Overall Depth (mm): "))
USER_HEIGHT = float(input("Enter Overall Height (mm): "))

# ============================================================
# READ COMPONENT DATASET
# ============================================================

columns = [

    "Template",
    "Assembly",
    "Component",

    "L_mm",
    "W_mm",
    "H_mm",

    "Xmin",
    "Ymin",
    "Zmin",

    "Xmax",
    "Ymax",
    "Zmax",

    "CenterX",
    "CenterY",
    "CenterZ",

    "Volume",
    "Material",
    "Body_Count",
    "Measurement_Type",
    "Visibility"

]

components = pd.read_csv(
    "renamed_sofa_component.csv",
    header=None,
    names=columns
)

# ============================================================
# CONVERT NUMERIC COLUMNS
# ============================================================

numeric_columns = [

    "L_mm",
    "W_mm",
    "H_mm",

    "Xmin",
    "Ymin",
    "Zmin",

    "Xmax",
    "Ymax",
    "Zmax",

    "CenterX",
    "CenterY",
    "CenterZ",

    "Volume"

]

for col in numeric_columns:

    components[col] = pd.to_numeric(
        components[col],
        errors="coerce"
    )

# ============================================================
# READ METADATA
# ============================================================

metadata = pd.read_csv(
    "updated_sofa_metadat.csv"
)

# ============================================================
# READ PHASE3 JSON
# ============================================================

with open("phase3.json", "r") as f:

    phase3 = json.load(f)

# ============================================================
# VALIDATION
# ============================================================

print("\nChecking Template...")

if phase3["sofa_type"] != "Straight":

    raise Exception("Unsupported Sofa Type")

if phase3["seat_configuration"] != "Jointed":

    raise Exception("Only Jointed Seat Configuration Supported")

external = components[
    components["Visibility"].str.lower() == "external"
]

if len(external) == 0:

    raise Exception("No External Components Found")

print("Template Validated Successfully")

# ============================================================
# EXTRACT SEAT RATIOS
# ============================================================

seat_ratio = phase3["components"]["seat"]["bbox"]

seat_width_ratio = seat_ratio["width_ratio"]
seat_depth_ratio = seat_ratio["depth_ratio"]
seat_height_ratio = seat_ratio["height_ratio"]

# ============================================================
# TARGET DIMENSIONS
# ============================================================

target_length = seat_width_ratio * USER_LENGTH
target_depth = seat_depth_ratio * USER_DEPTH
target_height = seat_height_ratio * USER_HEIGHT

print("\nTarget Seat Dimensions")

print("Length :", round(target_length,2))
print("Depth  :", round(target_depth,2))
print("Height :", round(target_height,2))

# ============================================================
# SELECT ONLY SEAT COMPONENTS
# ============================================================

seat_components = external[
    external["Component"].isin([
        "seat_top",
        "seat_front"
    ])
].copy()

if len(seat_components) == 0:

    raise Exception("seat_top / seat_front not found")

# ============================================================
# MERGE TEMPLATE DIMENSIONS
# ============================================================

template_length = seat_components["L_mm"].sum()

template_depth = seat_components["W_mm"].max()

template_height = seat_components["H_mm"].max()

print("\nTemplate Dimensions")

print("Length :", template_length)
print("Depth  :", template_depth)
print("Height :", template_height)

# ============================================================
# SCALE FACTORS
# ============================================================

scale_x = target_length / template_length

scale_y = target_depth / template_depth

scale_z = target_height / template_height

print("\nScale Factors")

print("ScaleX =", round(scale_x,6))
print("ScaleY =", round(scale_y,6))
print("ScaleZ =", round(scale_z,6))

# ============================================================
# OUTPUT LIST
# ============================================================

scaled_output = []
# ============================================================
# SCALE seat_top AND seat_front
# ============================================================

for _, row in seat_components.iterrows():

    body = {}

    body["Component"] = row["Component"]

    body["Original_Dimensions"] = {

        "Length_mm": round(row["L_mm"],2),
        "Width_mm": round(row["W_mm"],2),
        "Height_mm": round(row["H_mm"],2)

    }

    body["Scale_Factors"] = {

        "ScaleX": round(scale_x,6),
        "ScaleY": round(scale_y,6),
        "ScaleZ": round(scale_z,6)

    }

    # ==========================================
    # Scaled Dimensions
    # ==========================================

    scaled_length = row["L_mm"] * scale_x
    scaled_width = row["W_mm"] * scale_y
    scaled_height = row["H_mm"] * scale_z

    body["Scaled_Dimensions"] = {

        "Length_mm": round(scaled_length,2),
        "Width_mm": round(scaled_width,2),
        "Height_mm": round(scaled_height,2)

    }

    # ==========================================
    # Scale Bounding Box Coordinates
    # ==========================================

    coordinates = {

        "Xmin": round(row["Xmin"] * scale_x,2),
        "Ymin": round(row["Ymin"] * scale_y,2),
        "Zmin": round(row["Zmin"] * scale_z,2),

        "Xmax": round(row["Xmax"] * scale_x,2),
        "Ymax": round(row["Ymax"] * scale_y,2),
        "Zmax": round(row["Zmax"] * scale_z,2)

    }

    body["Scaled_Coordinates"] = coordinates

    # ==========================================
    # Scale Center Coordinates
    # ==========================================

    center = {

        "CenterX": round(row["CenterX"] * scale_x,2),
        "CenterY": round(row["CenterY"] * scale_y,2),
        "CenterZ": round(row["CenterZ"] * scale_z,2)

    }

    body["Scaled_Center"] = center

    scaled_output.append(body)

# ============================================================
# SAVE JSON
# ============================================================

with open("scaled_external.json","w") as f:

    json.dump(
        scaled_output,
        f,
        indent=4
    )

print("\nscaled_external.json Created")

# ============================================================
# CREATE CSV OUTPUT
# ============================================================

csv_rows = []

for item in scaled_output:

    row = {

        "Component": item["Component"],

        "ScaleX": item["Scale_Factors"]["ScaleX"],
        "ScaleY": item["Scale_Factors"]["ScaleY"],
        "ScaleZ": item["Scale_Factors"]["ScaleZ"],

        "Length_mm": item["Scaled_Dimensions"]["Length_mm"],
        "Width_mm": item["Scaled_Dimensions"]["Width_mm"],
        "Height_mm": item["Scaled_Dimensions"]["Height_mm"],

        "Xmin": item["Scaled_Coordinates"]["Xmin"],
        "Ymin": item["Scaled_Coordinates"]["Ymin"],
        "Zmin": item["Scaled_Coordinates"]["Zmin"],

        "Xmax": item["Scaled_Coordinates"]["Xmax"],
        "Ymax": item["Scaled_Coordinates"]["Ymax"],
        "Zmax": item["Scaled_Coordinates"]["Zmax"],

        "CenterX": item["Scaled_Center"]["CenterX"],
        "CenterY": item["Scaled_Center"]["CenterY"],
        "CenterZ": item["Scaled_Center"]["CenterZ"]

    }

    csv_rows.append(row)

scaled_csv = pd.DataFrame(csv_rows)

scaled_csv.to_csv(

    "scaled_external.csv",

    index=False

)

print("scaled_external.csv Created")
# ============================================================
# UPDATE SOFA METADATA
# ============================================================

metadata.loc[0, "Overall_Length_mm"] = USER_LENGTH
metadata.loc[0, "Overall_Depth_mm"] = USER_DEPTH
metadata.loc[0, "Overall_Height_mm"] = USER_HEIGHT

# Optional: Update calculated seat dimensions
metadata.loc[0, "Seat_Width_mm"] = round(target_length, 2)
metadata.loc[0, "Seat_Depth_mm"] = round(target_depth, 2)
metadata.loc[0, "Seat_Height_mm"] = round(target_height, 2)

metadata.to_csv(
    "scaled_sofa_metadata.csv",
    index=False
)

print("scaled_sofa_metadata.csv Created")

# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n========================================")
print("PHASE 4A COMPLETED SUCCESSFULLY")
print("========================================")

print("\nUser Dimensions")
print("-------------------------")
print(f"Overall Length : {USER_LENGTH:.2f} mm")
print(f"Overall Depth  : {USER_DEPTH:.2f} mm")
print(f"Overall Height : {USER_HEIGHT:.2f} mm")

print("\nSeat Target Dimensions")
print("-------------------------")
print(f"Length : {target_length:.2f} mm")
print(f"Depth  : {target_depth:.2f} mm")
print(f"Height : {target_height:.2f} mm")

print("\nScale Factors")
print("-------------------------")
print(f"Scale X : {scale_x:.6f}")
print(f"Scale Y : {scale_y:.6f}")
print(f"Scale Z : {scale_z:.6f}")

print("\nScaled Components")
print("-------------------------")

for item in scaled_output:

    print(f"\nComponent : {item['Component']}")

    print(
        "Scaled Size : "
        f"{item['Scaled_Dimensions']['Length_mm']} x "
        f"{item['Scaled_Dimensions']['Width_mm']} x "
        f"{item['Scaled_Dimensions']['Height_mm']} mm"
    )

print("\nGenerated Files")
print("-------------------------")
print("✓ scaled_external.json")
print("✓ scaled_external.csv")
print("✓ scaled_sofa_metadata.csv")

print("\nDone.")