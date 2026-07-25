import json
import os
import pandas as pd
from scripts.verification.check_scaling import check_scaling

from armrest_scaler import (
    scale_armrests,
    print_scaling_summary
)


def get_user_dimensions():
    """
    Read sofa dimensions from terminal.
    """

    print("\nEnter User Sofa Dimensions (mm)\n")

    length = float(input("Overall Length : "))
    depth = float(input("Overall Depth  : "))
    height = float(input("Overall Height : "))

    return length, depth, height


def load_phase3_json(path):
    with open(path, "r") as f:
        return json.load(f)


def main():

    ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )

    COMPONENT_CSV = os.path.join(
        ROOT,
        "data",
        "renamed_sofa_component.csv"
    )

    PHASE3_JSON = os.path.join(
        os.path.dirname(__file__),
        "dummy_input.json"
    )

    OUTPUT_DIR = os.path.join(ROOT, "outputs")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    OUTPUT_CSV = os.path.join(
        OUTPUT_DIR,
        "scaled_sofa_components.csv"
    )

    # -----------------------------
    # User input
    # -----------------------------

    user_length, user_depth, user_height = get_user_dimensions()

    # -----------------------------
    # Load files
    # -----------------------------

    phase3 = load_phase3_json(PHASE3_JSON)

    component_df = pd.read_csv(COMPONENT_CSV)

    # -----------------------------
    # Scale
    # -----------------------------

    scaled_df, verification_df, info = scale_armrests(
        component_df,
        phase3,
        user_length,
        user_depth,
        user_height
    )

    # ------------------------------------
# Keep only scaled armrest bodies
# ------------------------------------
    # -----------------------------
    # Save scaled armrest CSV
    # -----------------------------

    output_columns = [
        "body",

        "L_mm",
        "W_mm",
        "H_mm",

        "min_x_mm",
        "min_y_mm",
        "min_z_mm",

        "max_x_mm",
        "max_y_mm",
        "max_z_mm",

        "center_x_mm",
        "center_y_mm",
        "center_z_mm",
    ]

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

    output_df = (
        scaled_df[scaled_df["body"].isin(armrest_bodies)][output_columns]
        .copy()
    )

    output_df.rename(columns={
        "L_mm": "scaled_L_mm",
        "W_mm": "scaled_W_mm",
        "H_mm": "scaled_H_mm",

        "min_x_mm": "scaled_min_x_mm",
        "min_y_mm": "scaled_min_y_mm",
        "min_z_mm": "scaled_min_z_mm",

        "max_x_mm": "scaled_max_x_mm",
        "max_y_mm": "scaled_max_y_mm",
        "max_z_mm": "scaled_max_z_mm",

        "center_x_mm": "scaled_center_x_mm",
        "center_y_mm": "scaled_center_y_mm",
        "center_z_mm": "scaled_center_z_mm",
    }, inplace=True)

    output_csv = os.path.join(
        OUTPUT_DIR,
        "scaled_armrest_components.csv"
    )

    output_df.to_csv(output_csv, index=False)

    check_scaling(
    component_df,
    output_df,
    info["scale_x"],
    info["scale_y"],
    info["scale_z"]
    )

    # -----------------------------
    # Print Results
    # -----------------------------

    print_scaling_summary(info)

    print("\nScaled Armrest Bodies\n")
    print(verification_df.to_string(index=False))

    print("\n")
    print("=" * 60)
    print("Scaled CSV written to:")
    print(output_csv)
    print("=" * 60)

if __name__ == "__main__":
    main()