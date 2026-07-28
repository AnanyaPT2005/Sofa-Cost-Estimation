import json
import os
import sys

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pandas as pd
from scripts.verification.check_scaling import check_scaling
from scripts.verification.armrest_checks import check_armrest_logic
from scripts.verification.seat_checks import check_seat_logic

from armrest_scaler import (
    scale_armrests,
    print_scaling_summary,
)

from seat_scaler import (
    scale_seats,
    print_seat_summary,
)

from scripts.verification.check_scaling import check_scaling
from scripts.verification.armrest_checks import check_armrest_logic
from scripts.verification.seat_checks import check_seat_logic


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

    # --------------------------------------------------
    # User Input
    # --------------------------------------------------

    user_length, user_depth, user_height = get_user_dimensions()

    # --------------------------------------------------
    # Load Files
    # --------------------------------------------------

    phase3 = load_phase3_json(PHASE3_JSON)

    component_df = pd.read_csv(COMPONENT_CSV)

    # --------------------------------------------------
    # Scale Armrests
    # --------------------------------------------------

    sofa_metadata_df = pd.read_csv("csv/sofa_metadata.csv")

    armrest_scaled_df, armrest_info = scale_armrests(
        component_df,
        phase3,
        sofa_metadata_df,
        user_length,
        user_depth,
        user_height,
    )

    # --------------------------------------------------
    # Scale Seats
    # --------------------------------------------------

    scaled_df, seat_verification_df, seat_info = scale_seats(
        armrest_scaled_df,
        phase3,
        user_length,
        user_depth,
        user_height,
    )

    # --------------------------------------------------
# Save Only Scaled Components
# --------------------------------------------------

    scaled_bodies = [
        # Armrests
        "left_armrest_top",
        "left_armrest_top (1)",
        "left_armrest_front",
        "left_armrest_base",
        "right_armrest_top",
        "right_armrest_top (1)",
        "right_armrest_front",
        "right_armrest_base",

        # Seats
        "seat_top",
        "seat_front",
    ]

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

    output_df = (
        scaled_df[scaled_df["body"].isin(scaled_bodies)][output_columns]
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

    output_df.to_csv(
        OUTPUT_CSV,
        index=False,
    )

    # --------------------------------------------------
    # Verification DataFrames
    # --------------------------------------------------

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

    seat_bodies = [
        "seat_top",
        "seat_front",
    ]

    armrest_df = scaled_df[
        scaled_df["body"].isin(armrest_bodies)
    ].copy()

    seat_df = scaled_df[
        scaled_df["body"].isin(seat_bodies)
    ].copy()

    # --------------------------------------------------
    # Verification
    # --------------------------------------------------

    check_scaling(
        component_df,
        armrest_df,
        armrest_info["scale_x"],
        armrest_info["scale_y"],
        armrest_info["scale_z"],
        logical_check=check_armrest_logic,
        title="ARMREST SCALING VERIFICATION",
    )

    check_scaling(
        component_df,
        seat_df,
        seat_info["scale_x"],
        seat_info["scale_y"],
        seat_info["scale_z"],
        logical_check=check_seat_logic,
        title="SEAT SCALING VERIFICATION",
    )

    # --------------------------------------------------
    # Print Summaries
    # --------------------------------------------------

    print_scaling_summary(armrest_info)

    print("\nScaled Armrest Bodies\n")
    print(armrest_verification_df.to_string(index=False))

    print_seat_summary(seat_info)

    print("\nScaled Seat Bodies\n")
    print(seat_verification_df.to_string(index=False))

    print("\n")
    print("=" * 60)
    print("Scaled CSV written to:")
    print(OUTPUT_CSV)
    print("=" * 60)


if __name__ == "__main__":
    main()