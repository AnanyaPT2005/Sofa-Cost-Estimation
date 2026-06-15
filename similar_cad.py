import pandas as pd

# =========================
# LOAD CAD FEATURE DATASET
# =========================

df = pd.read_csv("data/cad.csv")

# =========================
# USER INPUT
# =========================

print("\nENTER TARGET SOFA DIMENSIONS\n")

target_length = float(input("Length: "))
target_height = float(input("Height: "))
target_depth = float(input("Depth: "))

# =========================
# FIND MOST SIMILAR CAD
# =========================

best_score = float("inf")
best_match = None

for _, row in df.iterrows():

    score = 0

    # Weighted structural similarity
    score += 5 * abs(row["length"] - target_length)

    score += 3 * abs(row["height"] - target_height)

    score += 5 * abs(row["depth"] - target_depth)

    # Keep best match
    if score < best_score:
        best_score = score
        best_match = row

# =========================
# OUTPUT
# =========================

print("\nMOST SIMILAR CAD TEMPLATE FOUND\n")

print(f"CAD File: {best_match['cad_file']}")
print(f"Length: {best_match['length']}")
print(f"Height: {best_match['height']}")
print(f"Depth: {best_match['depth']}")
print(f"Volume: {best_match['volume']}")
print(f"Surface Area: {best_match['surface_area']}")

similarity_score = 100 / (1 + best_score / 100)
print(f"\nSimilarity Score: {similarity_score:.2f}%")