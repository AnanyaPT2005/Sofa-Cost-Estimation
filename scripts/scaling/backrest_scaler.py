import pandas as pd


def scale_backrest(
    component_df,
    phase3,
    sofa_metadata_df,
):

    overall_length = sofa_metadata_df.loc[0, "Overall_Length_mm"]
    overall_height = sofa_metadata_df.loc[0, "Overall_Height_mm"]
    seat_height = sofa_metadata_df.loc[0, "Seat_Height_mm"]

    target_height = overall_height - seat_height

    width_ratio = phase3["components"]["backrest"]["bbox"]["width_ratio"]
    target_length = overall_length * width_ratio

    backrest = component_df[
        component_df["body"] == "backrest_back"
    ]

    template_length = float(backrest.iloc[0]["L_mm"])
    template_height = float(backrest.iloc[0]["H_mm"])

    scale_x = target_length / template_length
    scale_y = target_height / template_height

    scaled_df = component_df.copy()

    # --------------------------------------------------
    # Backrest Front
    # --------------------------------------------------

    front_idx = scaled_df["body"] == "backrest_front"

    template_front_length = float(
        scaled_df.loc[front_idx, "L_mm"].iloc[0]
    )

    scale_front_x = target_length / template_front_length

    scaled_df.loc[front_idx, "scaled_L_mm"] = (
        scaled_df.loc[front_idx, "L_mm"] * scale_front_x
    )

    scaled_df.loc[front_idx, "scaled_W_mm"] = (
        scaled_df.loc[front_idx, "W_mm"]
    )

    scaled_df.loc[front_idx, "scaled_H_mm"] = (
        overall_height - seat_height
    )

    # Keep original coordinates for now
    scaled_df.loc[front_idx, "scaled_min_x_mm"] = scaled_df.loc[front_idx, "min_x_mm"]
    scaled_df.loc[front_idx, "scaled_min_y_mm"] = scaled_df.loc[front_idx, "min_y_mm"]
    scaled_df.loc[front_idx, "scaled_min_z_mm"] = scaled_df.loc[front_idx, "min_z_mm"]

    scaled_df.loc[front_idx, "scaled_max_x_mm"] = scaled_df.loc[front_idx, "max_x_mm"]
    scaled_df.loc[front_idx, "scaled_max_y_mm"] = scaled_df.loc[front_idx, "max_y_mm"]
    scaled_df.loc[front_idx, "scaled_max_z_mm"] = scaled_df.loc[front_idx, "max_z_mm"]

    scaled_df.loc[front_idx, "scaled_center_x_mm"] = scaled_df.loc[front_idx, "center_x_mm"]
    scaled_df.loc[front_idx, "scaled_center_y_mm"] = scaled_df.loc[front_idx, "center_y_mm"]
    scaled_df.loc[front_idx, "scaled_center_z_mm"] = scaled_df.loc[front_idx, "center_z_mm"]

    # --------------------------------------------------
    # Backrest Back
    # --------------------------------------------------

    back_idx = scaled_df["body"] == "backrest_back"

    template_back_length = float(
        scaled_df.loc[back_idx, "L_mm"].iloc[0]
    )

    scale_back_x = target_length / template_back_length
    scaled_df.loc[back_idx, "scaled_L_mm"] = (
        scaled_df.loc[back_idx, "L_mm"] * scale_back_x
    )

    scaled_df.loc[back_idx, "scaled_W_mm"] = (
        scaled_df.loc[back_idx, "W_mm"]
    )

    scaled_df.loc[back_idx, "scaled_H_mm"] = (
        overall_height
    )

    # Keep original coordinates for now
    scaled_df.loc[back_idx, "scaled_min_x_mm"] = scaled_df.loc[back_idx, "min_x_mm"]
    scaled_df.loc[back_idx, "scaled_min_y_mm"] = scaled_df.loc[back_idx, "min_y_mm"]
    scaled_df.loc[back_idx, "scaled_min_z_mm"] = scaled_df.loc[back_idx, "min_z_mm"]

    scaled_df.loc[back_idx, "scaled_max_x_mm"] = scaled_df.loc[back_idx, "max_x_mm"]
    scaled_df.loc[back_idx, "scaled_max_y_mm"] = scaled_df.loc[back_idx, "max_y_mm"]
    scaled_df.loc[back_idx, "scaled_max_z_mm"] = scaled_df.loc[back_idx, "max_z_mm"]

    scaled_df.loc[back_idx, "scaled_center_x_mm"] = scaled_df.loc[back_idx, "center_x_mm"]
    scaled_df.loc[back_idx, "scaled_center_y_mm"] = scaled_df.loc[back_idx, "center_y_mm"]
    scaled_df.loc[back_idx, "scaled_center_z_mm"] = scaled_df.loc[back_idx, "center_z_mm"]

    info = {
    "template_length": template_length,
    "template_depth": float(backrest.iloc[0]["W_mm"]),
    "template_height": template_height,

    "target_length": target_length,
    "target_depth": float(backrest.iloc[0]["W_mm"]),
    "target_height": target_height,

    "scale_x": scale_x,
    "scale_y": scale_y,
    "scale_z": 1.0,
}

    return scaled_df, info