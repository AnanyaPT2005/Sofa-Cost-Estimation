import pandas as pd


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def _compute_scale_factors(
        df,
        phase3_json,
        sofa_metadata_df,
        user_length,
        user_depth,
        user_height
):
    """
    Computes logical armrest dimensions and target dimensions.

    New Rules
    ---------
    - Ignore armrest_top
    - Ignore armrest_top (1)
    - Ignore armrest_back
    - Base and Front have identical L/W after scaling
    - Base + Front heights = Armrest_Height_mm
    """

    arm = phase3_json["components"]["armrest"]["bbox"]

    target_length = arm["width_ratio"] * user_length
    target_depth = arm["depth_ratio"] * user_depth

    # Use metadata instead of image ratio for height
    target_height = float(sofa_metadata_df.iloc[0]["Armrest_Height_mm"])

    # ---------- TEMPLATE DIMENSIONS ----------

    base = df[df["body"] == "left_armrest_base"].iloc[0]
    front = df[df["body"] == "left_armrest_front"].iloc[0]

    template_length = base["L_mm"]
    template_depth = base["W_mm"]

    template_base_height = base["H_mm"]
    template_front_height = front["H_mm"]

    template_height = (
        template_base_height +
        template_front_height
    )

    scale_x = target_length / template_length
    scale_y = target_depth / template_depth
    scale_z = target_height / template_height

    info = {

        "template_length": template_length,
        "template_depth": template_depth,
        "template_height": template_height,

        "template_base_height": template_base_height,
        "template_front_height": template_front_height,

        "target_length": target_length,
        "target_depth": target_depth,
        "target_height": target_height,

        "scale_x": scale_x,
        "scale_y": scale_y,
        "scale_z": scale_z,
    }

    return info

# ---------------------------------------------------------
# Scale one body
# ---------------------------------------------------------

def _scale_body(row, info):

    row = row.copy()

    body = row["body"]

    scale_x = info["scale_x"]
    scale_y = info["scale_y"]
    scale_z = info["scale_z"]

    # -----------------------------
    # Base dimensions after scaling
    # -----------------------------

    scaled_length = info["target_length"]
    scaled_depth = info["target_depth"]

    # -----------------------------
    # Height
    # -----------------------------

    if "base" in body:

        new_height = (
            info["template_base_height"] * scale_z
        )

    elif "front" in body:

        new_height = (
            info["template_front_height"] * scale_z
        )

    else:
        return row

    # -----------------------------
    # Update dimensions
    # -----------------------------

    row["scaled_L_mm"] = round(scaled_length, 2)
    row["scaled_W_mm"] = round(scaled_depth, 2)
    row["scaled_H_mm"] = round(new_height, 2)
    # -----------------------------
    # Keep original coordinates
    # (Placement will be done later)
    # -----------------------------

    row["scaled_min_x_mm"] = row["min_x_mm"]
    row["scaled_min_y_mm"] = row["min_y_mm"]
    row["scaled_min_z_mm"] = row["min_z_mm"]

    row["scaled_max_x_mm"] = row["max_x_mm"]
    row["scaled_max_y_mm"] = row["max_y_mm"]
    row["scaled_max_z_mm"] = row["max_z_mm"]

    row["scaled_center_x_mm"] = row["center_x_mm"]
    row["scaled_center_y_mm"] = row["center_y_mm"]
    row["scaled_center_z_mm"] = row["center_z_mm"]

    return row

# ---------------------------------------------------------
# Main scaling function
# ---------------------------------------------------------

def scale_armrests(
        component_df,
        phase3_json,
        sofa_metadata_df,
        user_length,
        user_depth,
        user_height
):

    armrest_bodies = [
        "left_armrest_base",
        "left_armrest_front",
        "right_armrest_base",
        "right_armrest_front",
    ]

    info = _compute_scale_factors(
        component_df,
        phase3_json,
        sofa_metadata_df,
        user_length,
        user_depth,
        user_height,
    )

    scaled_df = component_df.copy()

    for idx, row in scaled_df.iterrows():

        if row["body"] not in armrest_bodies:
            continue

        scaled_df.loc[idx] = _scale_body(row, info)

    return scaled_df, info