import pandas as pd


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def _compute_scale_factors(df, phase3_json, user_length, user_depth, user_height):
    """
    Computes logical armrest dimensions and scale factors.
    """

    arm = phase3_json["components"]["armrest"]["bbox"]

    target_length = arm["width_ratio"] * user_length
    target_depth = arm["depth_ratio"] * user_depth
    target_height = arm["height_ratio"] * user_height

    # ---------- Left armrest logical dimensions ----------

    top = df[df["body"] == "left_armrest_top"].iloc[0]
    top2 = df[df["body"] == "left_armrest_top (1)"].iloc[0]
    base = df[df["body"] == "left_armrest_base"].iloc[0]
    front = df[df["body"] == "left_armrest_front"].iloc[0]

    logical_length = top["L_mm"] + top2["L_mm"]
    logical_depth = base["W_mm"]
    logical_height = base["H_mm"] + front["H_mm"]

    scale_x = target_length / logical_length
    scale_y = target_depth / logical_depth
    scale_z = target_height / logical_height

    info = {
        "template_length": logical_length,
        "template_depth": logical_depth,
        "template_height": logical_height,
        "target_length": target_length,
        "target_depth": target_depth,
        "target_height": target_height,
        "scale_x": scale_x,
        "scale_y": scale_y,
        "scale_z": scale_z,
    }

    return scale_x, scale_y, scale_z, info


# ---------------------------------------------------------
# Scale one body
# ---------------------------------------------------------

def _scale_body(row, sx, sy, sz):

    row = row.copy()

    old_l = row["L_mm"]
    old_w = row["W_mm"]
    old_h = row["H_mm"]

    new_l = old_l * sx
    new_w = old_w * sy
    new_h = old_h * sz

    row["L_mm"] = round(new_l, 2)
    row["W_mm"] = round(new_w, 2)
    row["H_mm"] = round(new_h, 2)

    # ---------- Keep body centre fixed ----------

    cx = row["center_x_mm"]
    cy = row["center_y_mm"]
    cz = row["center_z_mm"]

    row["min_x_mm"] = round(cx - new_l / 2, 2)
    row["max_x_mm"] = round(cx + new_l / 2, 2)

    row["min_y_mm"] = round(cy - new_w / 2, 2)
    row["max_y_mm"] = round(cy + new_w / 2, 2)

    row["min_z_mm"] = round(cz - new_h / 2, 2)
    row["max_z_mm"] = round(cz + new_h / 2, 2)

    # centre unchanged

    row["center_x_mm"] = round(cx, 2)
    row["center_y_mm"] = round(cy, 2)
    row["center_z_mm"] = round(cz, 2)

    return row


# ---------------------------------------------------------
# Main scaling function
# ---------------------------------------------------------

def scale_armrests(
        component_df,
        phase3_json,
        user_length,
        user_depth,
        user_height
):

    armrest_bodies = [
    "left_armrest_top",
    "left_armrest_top (1)",
    "left_armrest_front",
    "left_armrest_base",

    "right_armrest_top",
    "right_armrest_top (1)",
    "right_armrest_front",
    "right_armrest_base",
    ]

    sx, sy, sz, info = _compute_scale_factors(
        component_df,
        phase3_json,
        user_length,
        user_depth,
        user_height,
    )

    scaled_df = component_df.copy()

    verification = []

    for idx, row in scaled_df.iterrows():

        if row["body"] not in armrest_bodies:
            continue

        old_l = row["L_mm"]
        old_w = row["W_mm"]
        old_h = row["H_mm"]

        scaled = _scale_body(row, sx, sy, sz)

        scaled_df.loc[idx] = scaled

        verification.append({
            "Body": row["body"],
            "Old L": round(old_l, 2),
            "New L": round(scaled["L_mm"], 2),
            "Old W": round(old_w, 2),
            "New W": round(scaled["W_mm"], 2),
            "Old H": round(old_h, 2),
            "New H": round(scaled["H_mm"], 2),
        })

    verification_df = pd.DataFrame(verification)

    return scaled_df, verification_df, info


# ---------------------------------------------------------
# Pretty printing
# ---------------------------------------------------------

def print_scaling_summary(info):

    print("\n")
    print("=" * 60)
    print("ARMREST SCALING SUMMARY")
    print("=" * 60)

    print("\nTemplate Logical Dimensions")

    print(f"Length : {info['template_length']:.2f}")
    print(f"Depth  : {info['template_depth']:.2f}")
    print(f"Height : {info['template_height']:.2f}")

    print("\nTarget Dimensions")

    print(f"Length : {info['target_length']:.2f}")
    print(f"Depth  : {info['target_depth']:.2f}")
    print(f"Height : {info['target_height']:.2f}")

    print("\nScale Factors")

    print(f"Scale X : {info['scale_x']:.4f}")
    print(f"Scale Y : {info['scale_y']:.4f}")
    print(f"Scale Z : {info['scale_z']:.4f}")

    print("=" * 60)