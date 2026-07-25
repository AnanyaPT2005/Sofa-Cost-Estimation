import pandas as pd


SEAT_BODIES = [
    "seat_top",
    "seat_front",
]


def _compute_scale_factors(
    component_df,
    phase3,
    user_length,
    user_depth,
    user_height,
):
    """
    Compute seat scale factors.
    """

    ratios = phase3["components"]["seat"]["bbox"]

    target_length = ratios["width_ratio"] * user_length
    target_depth = ratios["depth_ratio"] * user_depth
    target_height = ratios["height_ratio"] * user_height

    seat_df = component_df[
        component_df["body"].isin(SEAT_BODIES)
    ].copy()

    if len(seat_df) != 2:
        raise ValueError(
            "seat_top and seat_front must exist in the component CSV."
        )

    seat_top = seat_df[
        seat_df["body"] == "seat_top"
    ].iloc[0]

    seat_front = seat_df[
        seat_df["body"] == "seat_front"
    ].iloc[0]

    # ------------------------------------
    # Logical template dimensions
    # ------------------------------------

    template_length = seat_top["L_mm"]

    template_depth = seat_top["H_mm"]

    # User confirmed this is the logical height
    template_height = seat_front["H_mm"]

    scale_x = target_length / template_length
    scale_y = target_depth / template_depth
    scale_z = target_height / template_height

    info = {

        "template_length": template_length,
        "template_depth": template_depth,
        "template_height": template_height,

        "target_length": target_length,
        "target_depth": target_depth,
        "target_height": target_height,

        "scale_x": scale_x,
        "scale_y": scale_y,
        "scale_z": scale_z,
    }

    return scale_x, scale_y, scale_z, info


def _scale_body(row, sx, sy, sz):
    """
    Scale one seat body while keeping its centre fixed.
    Coordinate logic is identical to armrest_scaler.py
    """

    row = row.copy()

    if row["body"] == "seat_top":
        new_L = row["L_mm"] * sx      # Length
        new_W = row["W_mm"] * sz      # Thickness
        new_H = row["H_mm"] * sy      # Depth

    elif row["body"] == "seat_front":
        new_L = row["L_mm"] * sx      # Length
        new_W = row["W_mm"] * sy      # Height
        new_H = row["H_mm"] * sz      # Thickness

    cx = row["center_x_mm"]
    cy = row["center_y_mm"]
    cz = row["center_z_mm"]

    row["L_mm"] = round(new_L, 2)
    row["W_mm"] = round(new_W, 2)
    row["H_mm"] = round(new_H, 2)

    row["min_x_mm"] = round(cx - new_L / 2, 2)
    row["max_x_mm"] = round(cx + new_L / 2, 2)

    row["min_y_mm"] = round(cy - new_W / 2, 2)
    row["max_y_mm"] = round(cy + new_W / 2, 2)

    row["min_z_mm"] = round(cz - new_H / 2, 2)
    row["max_z_mm"] = round(cz + new_H / 2, 2)

    return row

def scale_seats(
    component_df,
    phase3,
    user_length,
    user_depth,
    user_height,
):
    """
    Scale seat bodies.

    Returns
    -------
    scaled_df
    verification_df
    info
    """

    sx, sy, sz, info = _compute_scale_factors(
        component_df,
        phase3,
        user_length,
        user_depth,
        user_height,
    )

    scaled_df = component_df.copy()

    verification_rows = []

    for idx, row in scaled_df.iterrows():

        if row["body"] not in SEAT_BODIES:
            continue

        old = row.copy()

        new = _scale_body(
            row,
            sx,
            sy,
            sz,
        )

        scaled_df.loc[idx] = new

        verification_rows.append({

            "Body": row["body"],

            "Old L": round(old["L_mm"], 2),
            "New L": round(new["L_mm"], 2),

            "Old W": round(old["W_mm"], 2),
            "New W": round(new["W_mm"], 2),

            "Old H": round(old["H_mm"], 2),
            "New H": round(new["H_mm"], 2),
        })

    verification_df = pd.DataFrame(
        verification_rows
    )

    return (
        scaled_df,
        verification_df,
        info,
    )


def print_seat_summary(info):

    print("\n")
    print("=" * 60)
    print("SEAT SCALING SUMMARY")
    print("=" * 60)

    print("\nTemplate Logical Dimensions")
    print(
        f"Length : {info['template_length']:.2f} mm"
    )
    print(
        f"Depth  : {info['template_depth']:.2f} mm"
    )
    print(
        f"Height : {info['template_height']:.2f} mm"
    )

    print("\nTarget Dimensions")
    print(
        f"Length : {info['target_length']:.2f} mm"
    )
    print(
        f"Depth  : {info['target_depth']:.2f} mm"
    )
    print(
        f"Height : {info['target_height']:.2f} mm"
    )

    print("\nScale Factors")
    print(
        f"Scale X : {info['scale_x']:.4f}"
    )
    print(
        f"Scale Y : {info['scale_y']:.4f}"
    )
    print(
        f"Scale Z : {info['scale_z']:.4f}"
    )

    print("=" * 60)