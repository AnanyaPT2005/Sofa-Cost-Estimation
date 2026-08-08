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
)
from step_reader import (
    read_step,
    load_metadata,
    get_template_frame,
    get_assembly_dimensions,
    get_body_dimensions,
    get_category_dimensions,
    get_body_axis_map,
    print_global_length_bounds
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
STEP_FILE = r"G:\My Drive\sofa cost estimation\sofa 3d models\master sofa test hollow.step"
OUTPUT_STEP = r"G:\My Drive\sofa cost estimation\scripts\scaling\scaled_step.step"
metadata = load_metadata(r"G:\My Drive\sofa cost estimation\scripts\scaling\master_sofa_metadata.json")
print(type(metadata))
print(metadata)
SCALING_RULES = {
    "length": ["seat"],
    "width": ["seat", "armrest"],
    "height": ["backrest"],
}
def main():

    body_names = get_step_body_names(STEP_FILE)

    # print("\nBodies found:")

    # for i, name in enumerate(body_names, start=1):
    #     print(f"{i}. {name}")

    shape_tool = read_step(STEP_FILE)

    shape = get_reference_shape(shape_tool)

    solids = extract_solids(shape)
    print("\nSeat Body OBB Axes")

    for solid, body_name in zip(solids, body_names):

        if body_name in metadata["seat"]:

            obb = compute_obb(solid)
            axis_map = get_body_axis_map(obb)

            print("Axis Mapping:")
            print(axis_map)

            print("OBB Sizes:")
            print(
                "X:", 2 * obb.XHSize(),
                "Y:", 2 * obb.YHSize(),
                "Z:", 2 * obb.ZHSize()
            )

            print(f"\n{body_name}")

            print(
                "X:",
                obb.XDirection().X(),
                obb.XDirection().Y(),
                obb.XDirection().Z()
            )

            print(
                "Y:",
                obb.YDirection().X(),
                obb.YDirection().Y(),
                obb.YDirection().Z()
            )

            print(
                "Z:",
                obb.ZDirection().X(),
                obb.ZDirection().Y(),
                obb.ZDirection().Z()
            )
    assembly_dimensions = get_assembly_dimensions(
        solids,
    )

    print("\nCurrent Assembly Dimensions")

    for k, v in assembly_dimensions.items():
        print(f"{k}: {v:.2f}")
    

    # ---------------------------------------
    # Find seat category
    # ---------------------------------------

    seat_shape = None

    for solid, body_name in zip(solids, body_names):

        if body_name in metadata["seat"]:
            seat_shape = solid
            break

    seat_obb = compute_obb(seat_shape)
    template_frame = get_template_frame(
        seat_shape,
    )
    for category in metadata:

        dimensions = get_category_dimensions(
            category,
            metadata,
            solids,
            body_names,
            template_frame,
        )

        print(f"\n{category.upper()}")

        for k, v in dimensions.items():
            print(f"{k}: {v:.2f}")

    seat_body_dimensions = get_body_dimensions(
        "seat",
        metadata,
        solids,
        body_names,
    )

    print("\nSeat Body Dimensions")

    for body_name, dimensions in seat_body_dimensions.items():

        print(f"\n{body_name}")

        for dimension, value in dimensions.items():
            print(f"{dimension}: {value:.2f}")
    
    seat_dimensions = get_category_dimensions(
    "seat",
    metadata,
    solids,
    body_names,
    template_frame,
)

    # ---------------------------------------
    # User input
    # ---------------------------------------

    target_length = float(input("Target Length (mm): "))
    target_width = float(input("Target Width (mm): "))
    target_height = float(input("Target Height (mm): "))

    remaining = (
        target_length
        - assembly_dimensions["length"]
    )

    target_seat_length = (
        seat_dimensions["length"]
        + remaining
    )

    length_factor = (
        target_seat_length
        / seat_dimensions["length"]
    )
    width_factor = target_width / seat_dimensions["width"]
    height_factor = target_height / seat_dimensions["height"]

    print("\nScale Factors")
    print(f"Length : {length_factor:.3f}")
    print(f"Width  : {width_factor:.3f}")
    print(f"Height : {height_factor:.3f}")

    processed_solids = solids

    factors = {
        "length": length_factor,
        "width": width_factor,
        "height": height_factor,
    }

    for logical_dimension in [
        "length",
        "width",
        "height",
    ]:

        for category in SCALING_RULES[logical_dimension]:
            targets = {
                "length": target_length,
                "width": target_width,
                "height": target_height,
            }
            category_dimensions = get_category_dimensions(
                category,
                metadata,
                processed_solids,
                body_names,
                template_frame,
            )

            if logical_dimension == "length" and category == "seat":
                factor = length_factor
            else:
                factor = (
                    targets[logical_dimension]
                    /
                    category_dimensions[logical_dimension]
                )
            print_global_length_bounds(
                processed_solids,
                body_names,
            )
            processed_solids = process_dimension(
                solids=processed_solids,
                body_names=body_names,
                logical_dimension=logical_dimension,
                factor=factor,
                reference_category=category,
                metadata=metadata,
            )
            print_global_length_bounds(
                processed_solids,
                body_names,
            )
            

            new_dimensions = get_assembly_dimensions(
                processed_solids,
            )

            print("\nAfter Seat Scaling")
            print(f"Global Length : {new_dimensions['length']:.2f}")

    # ----------------------------------------------------
    # Export STEP
    # ----------------------------------------------------

    export_step(
        processed_solids,
        OUTPUT_STEP,
    )


if __name__ == "__main__":
    main()