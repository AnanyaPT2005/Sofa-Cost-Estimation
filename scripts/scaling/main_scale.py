"""
Main pipeline for exact STEP assembly scaling.

Global convention:

    X -> Length
    Y -> Width
    Z -> Height

The complete assembly is scaled together.
"""

from dotenv import load_dotenv
import os

from body_names import get_step_body_names
from step_reader import read_step
from body_extractor import extract_solids

from scaling_pipeline import process_assembly

from bbox_engine import (
    compute_assembly_bbox,
    get_assembly_dimensions,
)

from export_step import export_step


# ---------------------------------------------------------
# ENVIRONMENT
# ---------------------------------------------------------

load_dotenv()

STEP_FILE = os.getenv(
    "STEP_FILE"
)

OUTPUT_STEP = os.getenv(
    "OUTPUT_STEP"
)

METADATA_FILE = os.getenv(
    "METADATA_FILE"
)


# ---------------------------------------------------------
# VALIDATE PATHS
# ---------------------------------------------------------

def validate_paths():

    print(
        "\n========== PATH CONFIGURATION =========="
    )

    print(
        "STEP_FILE     :",
        STEP_FILE,
    )

    print(
        "OUTPUT_STEP   :",
        OUTPUT_STEP,
    )

    print(
        "METADATA_FILE :",
        METADATA_FILE,
    )

    if not STEP_FILE:
        raise ValueError(
            "STEP_FILE is not configured."
        )

    if not OUTPUT_STEP:
        raise ValueError(
            "OUTPUT_STEP is not configured."
        )

    if not METADATA_FILE:
        raise ValueError(
            "METADATA_FILE is not configured."
        )

    if not os.path.exists(
        STEP_FILE
    ):
        raise FileNotFoundError(
            f"STEP file not found:\n"
            f"{STEP_FILE}"
        )

    if not os.path.exists(
        METADATA_FILE
    ):
        raise FileNotFoundError(
            f"Metadata file not found:\n"
            f"{METADATA_FILE}"
        )

    print(
        "All required input paths exist."
    )


# ---------------------------------------------------------
# PRINT DIMENSIONS
# ---------------------------------------------------------

def print_dimensions(
    title,
    dimensions,
):

    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    print(
        f"Length : "
        f"{dimensions['length']:.6f} mm"
    )

    print(
        f"Width  : "
        f"{dimensions['width']:.6f} mm"
    )

    print(
        f"Height : "
        f"{dimensions['height']:.6f} mm"
    )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    validate_paths()

    # -------------------------------------------------
    # Read STEP
    # -------------------------------------------------

    body_names = get_step_body_names(
        STEP_FILE
    )

    print(
        "\nSTEP BODY COUNT :",
        len(body_names)
    )

    shape = read_step(
        STEP_FILE
    )

    solids = extract_solids(
        shape
    )

    print(
        "\nTOTAL SOLIDS FOUND :",
        len(solids)
    )

    if len(solids) != len(body_names):

        raise RuntimeError(
            "Number of STEP body names does not "
            "match number of extracted solids.\n"
            f"Body names : {len(body_names)}\n"
            f"Solids     : {len(solids)}"
        )

    # -------------------------------------------------
    # Current dimensions
    # -------------------------------------------------

    current_dimensions = (
        get_assembly_dimensions(
            solids
        )
    )

    print_dimensions(
        "ORIGINAL ASSEMBLY DIMENSIONS",
        current_dimensions,
    )

    # -------------------------------------------------
    # User targets
    # -------------------------------------------------

    print(
        "\nEnter target dimensions in millimeters."
    )

    target_length = float(
        input(
            "Target Length (mm): "
        )
    )

    target_width = float(
        input(
            "Target Width (mm): "
        )
    )

    target_height = float(
        input(
            "Target Height (mm): "
        )
    )

    if target_length <= 0:
        raise ValueError(
            "Target length must be > 0."
        )

    if target_width <= 0:
        raise ValueError(
            "Target width must be > 0."
        )

    if target_height <= 0:
        raise ValueError(
            "Target height must be > 0."
        )

    # -------------------------------------------------
    # Scale complete assembly
    # -------------------------------------------------

    processed_solids, factors = (
        process_assembly(
            solids=solids,
            target_length=target_length,
            target_width=target_width,
            target_height=target_height,
        )
    )

    # -------------------------------------------------
    # Final dimensions
    # -------------------------------------------------

    final_dimensions = (
        get_assembly_dimensions(
            processed_solids
        )
    )

    print_dimensions(
        "FINAL ASSEMBLY DIMENSIONS",
        final_dimensions,
    )

    # -------------------------------------------------
    # Target
    # -------------------------------------------------

    print("\n" + "=" * 60)
    print("TARGET DIMENSIONS")
    print("=" * 60)

    print(
        f"Length : "
        f"{target_length:.6f} mm"
    )

    print(
        f"Width  : "
        f"{target_width:.6f} mm"
    )

    print(
        f"Height : "
        f"{target_height:.6f} mm"
    )

    # -------------------------------------------------
    # Errors
    # -------------------------------------------------

    length_error = (
        final_dimensions["length"]
        - target_length
    )

    width_error = (
        final_dimensions["width"]
        - target_width
    )

    height_error = (
        final_dimensions["height"]
        - target_height
    )

    print("\n" + "=" * 60)
    print("DIMENSION ERROR")
    print("=" * 60)

    print(
        f"Length Error : "
        f"{length_error:.9f} mm"
    )

    print(
        f"Width Error  : "
        f"{width_error:.9f} mm"
    )

    print(
        f"Height Error : "
        f"{height_error:.9f} mm"
    )

    # -------------------------------------------------
    # Verification
    # -------------------------------------------------

    tolerance = 0.001

    success = (
        abs(length_error) <= tolerance
        and
        abs(width_error) <= tolerance
        and
        abs(height_error) <= tolerance
    )

    print("\n" + "=" * 60)

    if success:

        print(
            "EXACT DIMENSION TARGET ACHIEVED"
        )

        print(
            f"Tolerance : ±{tolerance} mm"
        )

    else:

        print(
            "WARNING: FINAL DIMENSIONS "
            "ARE OUTSIDE TOLERANCE."
        )

    print("=" * 60)

    # -------------------------------------------------
    # Export
    # -------------------------------------------------

    print(
        "\nExporting scaled STEP..."
    )

    export_step(
        processed_solids,
        OUTPUT_STEP,
    )

    print(
        "\nSTEP exported successfully!"
    )

    print(
        OUTPUT_STEP
    )


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    main()