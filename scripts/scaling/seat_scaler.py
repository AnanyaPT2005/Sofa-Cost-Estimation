# import pandas as pd


# # ---------------------------------------------------------
# # Bodies
# # ---------------------------------------------------------

# SEAT_BODIES = [
#     "seat_top",
#     "seat_front",
# ]


# # ---------------------------------------------------------
# # Utility functions
# # ---------------------------------------------------------

# def scale_seats(
#     component_df,
#     phase3,
#     sofa_metadata_df,
# ):
    
#     """
#     Computes logical seat dimensions.

#     Rules
#     -----
#     seat_top
#         L -> Scale
#         W -> Keep
#         H -> Scale (Seat Depth)

#     seat_front
#         L -> Scale
#         W -> Scale (Seat Height)
#         H -> Keep
#     """

#     seat = phase3_json["components"]["seat"]["bbox"]

#     target_length = seat["width_ratio"] * user_length
#     target_depth = seat["depth_ratio"] * user_depth
#     target_height = seat["height_ratio"] * user_height

#     top = component_df[
#         component_df["body"] == "seat_top"
#     ].iloc[0]

#     front = component_df[
#         component_df["body"] == "seat_front"
#     ].iloc[0]

#     template_length = top["L_mm"]

#     # Logical depth comes from seat_top height
#     template_depth = top["H_mm"]

#     # Logical seat height comes from seat_front height
#     template_height = front["H_mm"]

#     scale_x = target_length / template_length
#     scale_y = target_depth / template_depth
#     scale_z = target_height / template_height

#     info = {

#         "template_length": template_length,
#         "template_depth": template_depth,
#         "template_height": template_height,

#         "target_length": target_length,
#         "target_depth": target_depth,
#         "target_height": target_height,

#         "scale_x": scale_x,
#         "scale_y": scale_y,
#         "scale_z": scale_z,
#     }

#     return info


# # ---------------------------------------------------------
# # Scale one body
# # ---------------------------------------------------------

# def _scale_body(row, info):

#     row = row.copy()

#     body = row["body"]

#     # -------------------------------------------------
#     # seat_top
#     # -------------------------------------------------

#     if body == "seat_top":

#         scaled_length = info["target_length"]

#         # Thickness unchanged
#         scaled_width = row["W_mm"]

#         # Logical seat depth
#         scaled_height = row["H_mm"] * info["scale_y"]

#     # -------------------------------------------------
#     # seat_front
#     # -------------------------------------------------

#     elif body == "seat_front":

#         scaled_length = info["target_length"]

#         # Logical seat height
#         scaled_width = row["W_mm"] * info["scale_z"]

#         # Thickness unchanged
#         scaled_height = row["H_mm"]

#     else:
#         return row

#     # -------------------------------------------------
#     # Store scaled dimensions
#     # -------------------------------------------------

#     row["scaled_L_mm"] = round(scaled_length, 2)
#     row["scaled_W_mm"] = round(scaled_width, 2)
#     row["scaled_H_mm"] = round(scaled_height, 2)

#     # -------------------------------------------------
#     # Keep original coordinates
#     # (Placement handled later)
#     # -------------------------------------------------

#     row["scaled_min_x_mm"] = row["min_x_mm"]
#     row["scaled_min_y_mm"] = row["min_y_mm"]
#     row["scaled_min_z_mm"] = row["min_z_mm"]

#     row["scaled_max_x_mm"] = row["max_x_mm"]
#     row["scaled_max_y_mm"] = row["max_y_mm"]
#     row["scaled_max_z_mm"] = row["max_z_mm"]

#     row["scaled_center_x_mm"] = row["center_x_mm"]
#     row["scaled_center_y_mm"] = row["center_y_mm"]
#     row["scaled_center_z_mm"] = row["center_z_mm"]

#     return row

# # ---------------------------------------------------------
# # Scale seat bodies
# # ---------------------------------------------------------

# def scale_seats(
#         component_df,
#         phase3_json,
#         user_length,
#         user_depth,
#         user_height,
# ):
#     """
#     Scale seat bodies.

#     Returns
#     -------
#     scaled_df
#     info
#     """

#     info = _compute_scale_factors(
#         component_df,
#         phase3_json,
#         user_length,
#         user_depth,
#         user_height,
#     )

#     scaled_df = component_df.copy()

#     for idx, row in scaled_df.iterrows():

#         if row["body"] not in SEAT_BODIES:
#             continue

#         scaled_df.loc[idx] = _scale_body(
#             row,
#             info,
#         )

#     return (
#         scaled_df,
#         info,
#     )


# # ---------------------------------------------------------
# # Print summary
# # ---------------------------------------------------------

# def print_seat_summary(info):

#     print("\n")
#     print("=" * 60)
#     print("SEAT SCALING SUMMARY")
#     print("=" * 60)

#     print("\nTemplate Dimensions")

#     print(
#         f"Length : {info['template_length']:.2f} mm"
#     )
#     print(
#         f"Depth  : {info['template_depth']:.2f} mm"
#     )
#     print(
#         f"Height : {info['template_height']:.2f} mm"
#     )

#     print("\nTarget Dimensions")

#     print(
#         f"Length : {info['target_length']:.2f} mm"
#     )
#     print(
#         f"Depth  : {info['target_depth']:.2f} mm"
#     )
#     print(
#         f"Height : {info['target_height']:.2f} mm"
#     )

#     print("\nScale Factors")

#     print(
#         f"Scale X : {info['scale_x']:.4f}"
#     )
#     print(
#         f"Scale Y : {info['scale_y']:.4f}"
#     )
#     print(
#         f"Scale Z : {info['scale_z']:.4f}"
#     )

#     print("=" * 60)




import pandas as pd


# ---------------------------------------------------------
# Bodies
# ---------------------------------------------------------

SEAT_BODIES = [
    "seat_top",
    "seat_front",
]


# ---------------------------------------------------------
# Compute scale factors
# ---------------------------------------------------------

def _compute_scale_factors(
    component_df,
    phase3,
    user_length,
    user_depth,
    seat_height,
):
    """
    Compute logical seat scaling factors.

    seat_top
        L -> Sofa Length
        W -> Cushion Thickness
        H -> Seat Depth

    seat_front
        L -> Sofa Length
        W -> Seat Height
        H -> Front Thickness
    """

    ratios = phase3["components"]["seat"]["bbox"]

    target_length = ratios["width_ratio"] * user_length
    target_depth = ratios["depth_ratio"] * user_depth
    target_height = ratios["height_ratio"] * seat_height

    seat_top = component_df[
        component_df["body"] == "seat_top"
    ].iloc[0]

    seat_front = component_df[
        component_df["body"] == "seat_front"
    ].iloc[0]

    # Logical template dimensions

    template_length = float(seat_top["L_mm"])
    template_depth = float(seat_top["H_mm"])
    template_height = float(seat_front["W_mm"])

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

    return info


# ---------------------------------------------------------
# Scale one body
# ---------------------------------------------------------

def _scale_body(
    row,
    info,
):

    row = row.copy()

    body = row["body"]

    # -------------------------------------------------
    # seat_top
    # -------------------------------------------------

    if body == "seat_top":

        scaled_length = row["L_mm"] * info["scale_x"]

        # Thickness stays constant
        scaled_width = row["W_mm"]

        # Seat depth scales
        scaled_height = row["H_mm"] * info["scale_y"]

    # -------------------------------------------------
    # seat_front
    # -------------------------------------------------

    elif body == "seat_front":

        scaled_length = row["L_mm"] * info["scale_x"]

        # Seat height scales
        scaled_width = row["W_mm"] * info["scale_z"]

        # Thickness stays constant
        scaled_height = row["H_mm"]

    else:
        return row

    # -------------------------------------------------
    # Store scaled dimensions
    # -------------------------------------------------

    row["scaled_L_mm"] = round(scaled_length, 2)
    row["scaled_W_mm"] = round(scaled_width, 2)
    row["scaled_H_mm"] = round(scaled_height, 2)

    # -------------------------------------------------
    # Copy coordinates
    # (Repositioning happens later)
    # -------------------------------------------------

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
# Scale seat bodies
# ---------------------------------------------------------

def scale_seats(
    component_df,
    phase3,
    sofa_metadata_df,
):
    """
    Scale seat bodies.

    Returns
    -------
    scaled_df
    info
    """

    user_length = float(
        sofa_metadata_df.iloc[0]["Overall_Length_mm"]
    )

    user_depth = float(
        sofa_metadata_df.iloc[0]["Overall_Depth_mm"]
    )

    seat_height = float(
        sofa_metadata_df.iloc[0]["Seat_Height_mm"]
    )

    info = _compute_scale_factors(
        component_df,
        phase3,
        user_length,
        user_depth,
        seat_height,
    )

    scaled_df = component_df.copy()

    for idx, row in scaled_df.iterrows():

        if row["body"] not in SEAT_BODIES:
            continue

        scaled_df.loc[idx] = _scale_body(
            row,
            info,
        )

    return (
        scaled_df,
        info,
    )


# ---------------------------------------------------------
# Print summary
# ---------------------------------------------------------

def print_seat_summary(info):

    print("\n")
    print("=" * 60)
    print("SEAT SCALING SUMMARY")
    print("=" * 60)

    print("\nTemplate Dimensions")

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