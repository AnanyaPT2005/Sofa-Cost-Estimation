# import os
# import json
# import pandas as pd

# from armrest_scaler import scale_armrests
# from backrest_scaler import scale_backrest


# def main():

#     print("\n========== STEP 1 : READ INPUT FILES ==========")

#     # ----------------------------------
#     # Project Paths
#     # ----------------------------------

#     CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

#     # scripts/scaling -> project root
#     BASE_DIR = os.path.abspath(
#         os.path.join(CURRENT_DIR, "..", "..")
#     )

#     COMPONENT_CSV = os.path.join(
#         BASE_DIR, "data", "renamed_sofa_component.csv"
#     )

#     METADATA_CSV = os.path.join(
#         BASE_DIR, "data", "sofa_metadata.csv"
#     )

#     PHASE3_JSON = os.path.join(
#         BASE_DIR, "input", "phase3.json"
#     )

#     OUTPUT_CSV = os.path.join(
#         BASE_DIR, "outputs", "scaled_components.csv"
#     )

#     # ----------------------------------
#     # Load Files
#     # ----------------------------------

#     component_df = pd.read_csv(COMPONENT_CSV)
#     sofa_metadata_df = pd.read_csv(METADATA_CSV)

#     with open(PHASE3_JSON, "r") as f:
#         phase3 = json.load(f)

#     # ----------------------------------
#     # User Input
#     # ----------------------------------

#     user_length = float(input("Overall Length (mm): "))
#     user_depth = float(input("Overall Depth (mm): "))
#     user_height = float(input("Overall Height (mm): "))

#     # ----------------------------------
#     # Armrest Scaling
#     # ----------------------------------

#     scaled_df, armrest_info = scale_armrests(
#         component_df,
#         phase3,
#         sofa_metadata_df,
#         user_length,
#         user_depth,
#         user_height,
#     )

#     # ----------------------------------
#     # Backrest Scaling
#     # ----------------------------------

#     scaled_df, backrest_info = scale_backrest(
#         scaled_df,
#         phase3,
#         sofa_metadata_df,
#     )

#     # ----------------------------------
#     # Save only scaled bodies
#     # ----------------------------------

#     scaled_bodies = [
#         "left_armrest_base",
#         "left_armrest_front",
#         "right_armrest_base",
#         "right_armrest_front",
#         "backrest_front",
#         "backrest_back",
#     ]

#     columns = [
#         "body",
#         "scaled_L_mm",
#         "scaled_W_mm",
#         "scaled_H_mm",
#         "scaled_min_x_mm",
#         "scaled_min_y_mm",
#         "scaled_min_z_mm",
#         "scaled_max_x_mm",
#         "scaled_max_y_mm",
#         "scaled_max_z_mm",
#         "scaled_center_x_mm",
#         "scaled_center_y_mm",
#         "scaled_center_z_mm",
#     ]

#     output_df = (
#         scaled_df[scaled_df["body"].isin(scaled_bodies)][columns]
#         .reset_index(drop=True)
#     )

#     output_df.to_csv(OUTPUT_CSV, index=False)

#     # ----------------------------------
#     # Armrest Summary
#     # ----------------------------------

#     print("\n========== ARMREST ==========")

#     print(f"Template Length : {armrest_info['template_length']:.2f} mm")
#     print(f"Template Depth  : {armrest_info['template_depth']:.2f} mm")
#     print(f"Template Height : {armrest_info['template_height']:.2f} mm")

#     print()

#     print(f"Target Length   : {armrest_info['target_length']:.2f} mm")
#     print(f"Target Depth    : {armrest_info['target_depth']:.2f} mm")
#     print(f"Target Height   : {armrest_info['target_height']:.2f} mm")

#     print()

#     print(f"Scale X : {armrest_info['scale_x']:.4f}")
#     print(f"Scale Y : {armrest_info['scale_y']:.4f}")
#     print(f"Scale Z : {armrest_info['scale_z']:.4f}")

#     # ----------------------------------
#     # Backrest Summary
#     # ----------------------------------

#     print("\n========== BACKREST ==========")

#     print(f"Template Width  : {backrest_info['template_width']:.2f} mm")
#     print(f"Template Height : {backrest_info['template_height']:.2f} mm")

#     print()

#     print(f"Target Width    : {backrest_info['target_width']:.2f} mm")
#     print(f"Target Height   : {backrest_info['target_height']:.2f} mm")

#     print()

#     print(f"Scale X : {backrest_info['scale_x']:.4f}")
#     print(f"Scale Y : {backrest_info['scale_y']:.4f}")

#     print(f"\nScaled CSV saved to: {OUTPUT_CSV}")


# if __name__ == "__main__":
#     main()


import os
import json
import pandas as pd

from armrest_scaler import scale_armrests
from backrest_scaler import scale_backrest
from seat_scaler import scale_seats

def main():

    print("\n========== STEP 1 : READ INPUT FILES ==========")

    # ----------------------------------
    # Project Paths
    # ----------------------------------

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

    # scripts/scaling -> project root
    BASE_DIR = os.path.abspath(
        os.path.join(CURRENT_DIR, "..", "..")
    )

    COMPONENT_CSV = os.path.join(
        BASE_DIR, "data", "renamed_sofa_component.csv"
    )

    METADATA_CSV = os.path.join(
        BASE_DIR, "data", "sofa_metadata.csv"
    )

    PHASE3_JSON = os.path.join(
        BASE_DIR, "input", "phase3.json"
    )

    OUTPUT_CSV = os.path.join(
        BASE_DIR, "outputs", "scaled_components.csv"
    )

    # ----------------------------------
    # Load Files
    # ----------------------------------

    component_df = pd.read_csv(COMPONENT_CSV)
    sofa_metadata_df = pd.read_csv(METADATA_CSV)

    with open(PHASE3_JSON, "r") as f:
        phase3 = json.load(f)

    # ----------------------------------
    # User Input
    # ----------------------------------

    user_length = float(input("Overall Length (mm): "))
    user_depth = float(input("Overall Depth (mm): "))
    user_height = float(input("Overall Height (mm): "))

    # ----------------------------------
    # Armrest Scaling
    # ----------------------------------

    scaled_df, armrest_info = scale_armrests(
        component_df,
        phase3,
        sofa_metadata_df,
        user_length,
        user_depth,
        user_height,
    )

    

    # print("\nAFTER ARMREST SCALING")

    # for body in [
    #     "left_armrest_base",
    #     "left_armrest_front",
    #     "right_armrest_base",
    #     "right_armrest_front",
    # ]:
    #     row = scaled_df[scaled_df["body"] == body].iloc[0]
    #     print(
    #         body,
    #         row["scaled_L_mm"],
    #         row["scaled_W_mm"],
    #         row["scaled_H_mm"],
    #     )

    # ----------------------------------
    # Backrest Scaling
    # ----------------------------------

    scaled_df, backrest_info = scale_backrest(
        scaled_df,
        phase3,
        sofa_metadata_df,
    )
    # ---------------------------------------------------------
    # Seat Scaling
    # ---------------------------------------------------------

    scaled_df, seat_info = scale_seats(
    scaled_df,
    phase3,
    sofa_metadata_df,
    user_length,
    user_depth,
    user_height,
    )

    # print_seat_summary(seat_info)
    # ----------------------------------
    # Save only scaled bodies
    # ----------------------------------

    scaled_bodies = [
        "left_armrest_base",
        "left_armrest_front",
        "right_armrest_base",
        "right_armrest_front",
        "backrest_front",
        "backrest_back",
        "seat_top",
        "seat_front",
    ]

    columns = [
        "body",
        "scaled_L_mm",
        "scaled_W_mm",
        "scaled_H_mm",
        "scaled_min_x_mm",
        "scaled_min_y_mm",
        "scaled_min_z_mm",
        "scaled_max_x_mm",
        "scaled_max_y_mm",
        "scaled_max_z_mm",
        "scaled_center_x_mm",
        "scaled_center_y_mm",
        "scaled_center_z_mm",
    ]

    output_df = (
        scaled_df[scaled_df["body"].isin(scaled_bodies)][columns]
        .reset_index(drop=True)
    )

    output_df.to_csv(OUTPUT_CSV, index=False)

    # ---------------------------------------------------------
    # Print Scaling Summaries
    # ---------------------------------------------------------

    print_scaling_summary(
        "ARMREST",
        armrest_info,
        scaled_df,
        [
            "left_armrest_base",
            "left_armrest_front",
            "right_armrest_base",
            "right_armrest_front",
        ],
    )

    print_scaling_summary(
        "BACKREST",
        backrest_info,
        scaled_df,
        [
            "backrest_front",
            "backrest_back",
        ],
    )

    print_scaling_summary(
        "SEAT",
        seat_info,
        scaled_df,
        [
            "seat_top",
            "seat_front",
        ],
    )

    print(f"\nScaled CSV saved to:\n{OUTPUT_CSV}")


#     # ----------------------------------
#     # Armrest Summary
#     # ----------------------------------

#     print("\n========== ARMREST ==========")

#     print(f"Template Length : {armrest_info['template_length']:.2f} mm")
#     print(f"Template Depth  : {armrest_info['template_depth']:.2f} mm")
#     print(f"Template Height : {armrest_info['template_height']:.2f} mm")

#     print()

#     print(f"Target Length   : {armrest_info['target_length']:.2f} mm")
#     print(f"Target Depth    : {armrest_info['target_depth']:.2f} mm")
#     print(f"Target Height   : {armrest_info['target_height']:.2f} mm")

#     print()

#     print(f"Scale X : {armrest_info['scale_x']:.4f}")
#     print(f"Scale Y : {armrest_info['scale_y']:.4f}")
#     print(f"Scale Z : {armrest_info['scale_z']:.4f}")

#     # ----------------------------------
# # Backrest Summary
# # ----------------------------------

#     print("\n========== BACKREST ==========")

#     print(f"Template Length : {backrest_info['template_length']:.2f} mm")
#     print(f"Template Depth  : {backrest_info['template_depth']:.2f} mm")
#     print(f"Template Height : {backrest_info['template_height']:.2f} mm")

#     print()

#     print(f"Target Length   : {backrest_info['target_length']:.2f} mm")
#     print(f"Target Depth    : {backrest_info['target_depth']:.2f} mm")
#     print(f"Target Height   : {backrest_info['target_height']:.2f} mm")

#     print()

#     print(f"Scale X : {backrest_info['scale_x']:.4f}")
#     print(f"Scale Y : {backrest_info['scale_y']:.4f}")
#     print(f"Scale Z : {backrest_info['scale_z']:.4f}")
#     print(f"\nScaled CSV saved to: {OUTPUT_CSV}")

#     # ----------------------------------
#     # Scaled Body Dimensions
#     # ----------------------------------

#     print("\n========== SCALED BODY DIMENSIONS ==========")

#     scaled_bodies = [
#         "left_armrest_base",
#         "left_armrest_front",
#         "right_armrest_base",
#         "right_armrest_front",
#         "backrest_front",
#         "backrest_back",
#     ]

#     for body in scaled_bodies:

#         row = scaled_df[scaled_df["body"] == body].iloc[0]

#         print(f"\n{body}")
#         print(f"  Length : {row['scaled_L_mm']:.2f} mm")
#         print(f"  Depth  : {row['scaled_W_mm']:.2f} mm")
#         print(f"  Height : {row['scaled_H_mm']:.2f} mm")



# ---------------------------------------------------------
# Print Scaling Summary 
# ---------------------------------------------------------

def print_scaling_summary(
    title,
    info,
    scaled_df,
    bodies,
):
    print("\n")
    print("=" * 60)
    print(f"{title} SCALING SUMMARY")
    print("=" * 60)

    print("\nTemplate Dimensions")

    print(f"Length : {info['template_length']:.2f} mm")
    print(f"Depth  : {info['template_depth']:.2f} mm")
    print(f"Height : {info['template_height']:.2f} mm")

    print("\nTarget Dimensions")

    print(f"Length : {info['target_length']:.2f} mm")
    print(f"Depth  : {info['target_depth']:.2f} mm")
    print(f"Height : {info['target_height']:.2f} mm")

    print("\nScale Factors")

    print(f"Scale X : {info['scale_x']:.4f}")
    print(f"Scale Y : {info['scale_y']:.4f}")
    print(f"Scale Z : {info['scale_z']:.4f}")

    print("\nScaled Body Dimensions")

    for body in bodies:

        row = scaled_df[scaled_df["body"] == body].iloc[0]

        print(f"\n{body}")
        print(f"  Length : {row['scaled_L_mm']:.2f} mm")
        print(f"  Depth  : {row['scaled_W_mm']:.2f} mm")
        print(f"  Height : {row['scaled_H_mm']:.2f} mm")

    print("=" * 60)


if __name__ == "__main__":
    main()