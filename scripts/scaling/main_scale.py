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

def main():

    body_names = get_step_body_names(STEP_FILE)

    print("\nBodies found:")

    for i, name in enumerate(body_names, start=1):
        print(f"{i}. {name}")

    shape_tool = read_step(STEP_FILE)

    shape = get_reference_shape(shape_tool)

    solids = extract_solids(shape)

    processed_solids = process_dimension(
        solids=solids,
        body_names=body_names,
        logical_dimension="length",
        factor=0.5,
        reference_body="seat",
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