"""
Main pipeline for STEP processing.
"""
from dotenv import load_dotenv
import os
from body_names import get_step_body_names
from step_reader import read_step
from assembly_parser import get_reference_shape
from body_extractor import extract_solids
from scaling_pipeline import process_dimension
from step_reader import load_metadata
from scale_step import (
    scale_body,
    get_logical_dimension,
    get_body_dimensions,
)
from bbox_engine import (
    compute_bbox,
    compute_obb,
    print_bbox,
    print_obb,
)

from scale_step import (
    scale_body,
    get_logical_dimension,
)

from position_engine import (
    get_overlap,
    move_body,
    vector_between,
    get_obb,
    projection_on_axis,
    classify_attachment,
)

from export_step import export_step

load_dotenv()
STEP_FILE = os.getenv("STEP_FILE")
OUTPUT_STEP = os.getenv("OUTPUT_STEP")
metadata = load_metadata(os.getenv("METADATA_FILE"))
def main():

    body_names = get_step_body_names(STEP_FILE)

    print("\nBodies found:")

    for i, name in enumerate(body_names, start=1):
        print(f"{i}. {name}")

    shape_tool = read_step(STEP_FILE)

    shape = get_reference_shape(shape_tool)

    solids = extract_solids(shape)

    # ---------------------------------------
    # Find seat category
    # ---------------------------------------

    seat_shape = None

    for solid, body_name in zip(solids, body_names):

        if body_name in metadata["seat"]:
            seat_shape = solid
            break

    seat_obb = compute_obb(seat_shape)

    seat_dimensions = get_body_dimensions(
        "seat",
        seat_obb,
    )

    print("\nCurrent Seat Dimensions")

    for k, v in seat_dimensions.items():
        print(f"{k}: {v:.2f}")

    # ---------------------------------------
    # User input
    # ---------------------------------------

    target_length = float(input("Target Length (mm): "))
    target_width = float(input("Target Width (mm): "))
    target_height = float(input("Target Height (mm): "))

    length_factor = target_length / seat_dimensions["length"]
    width_factor = target_width / seat_dimensions["width"]
    height_factor = target_height / seat_dimensions["height"]

    print("\nScale Factors")
    print(f"Length : {length_factor:.3f}")
    print(f"Width  : {width_factor:.3f}")
    print(f"Height : {height_factor:.3f}")

    processed_solids = process_dimension(
        solids=solids,
        body_names=body_names,
        logical_dimension="length",
        factor=length_factor,
        reference_category="seat",
        metadata=metadata,
    )
    processed_solids = process_dimension(
        solids=processed_solids,
        body_names=body_names,
        logical_dimension="width",
        factor=width_factor,
        metadata=metadata,
        reference_category="seat",
    )
    processed_solids = process_dimension(
        solids=processed_solids,
        body_names=body_names,
        logical_dimension="height",
        factor=height_factor,
        metadata=metadata,
        reference_category="seat",
    )

    # ----------------------------------------------------
    # Export STEP
    # ----------------------------------------------------

    export_step(
        processed_solids,
        OUTPUT_STEP,
    )


if __name__ == "__main__":
    main()