"""
Main pipeline for STEP processing.

Workflow:
1. Read STEP file
2. Read body names
3. Parse assembly
4. Extract solids
5. Compute OBB
6. Scale selected body
7. (Future) Position dependent bodies
8. Export STEP
"""

from body_names import get_step_body_names
from step_reader import read_step
from assembly_parser import get_reference_shape
from body_extractor import extract_solids
from bbox_engine import compute_bbox, compute_obb, print_bbox, print_obb
from scale_step import scale_body

from export_step import export_step
from position_engine import (
    get_overlap,
    move_body,
    vector_between,
    get_obb,
    projection_on_axis,
    classify_attachment,
)

from scale_step import (
    scale_body,
    get_logical_dimension,
)

STEP_FILE = r"C:\Users\DEEPIKA.S\Desktop\sofa_cost\Sofa-Cost-Estimation\scripts\scaling\test_workfloe.step"

OUTPUT_STEP = r"C:\Users\DEEPIKA.S\Desktop\sofa_cost\Sofa-Cost-Estimation\scripts\scaling\scaled_step.step"


def main():

    # ----------------------------------------
    # Read body names
    # ----------------------------------------

    body_names = get_step_body_names(STEP_FILE)

    print("\nBodies found:")

    for i, name in enumerate(body_names, start=1):
        print(f"{i}. {name}")

    # ----------------------------------------
    # Read STEP file
    # ----------------------------------------

    shape_tool = read_step(STEP_FILE)

    # ----------------------------------------
    # Resolve assembly
    # ----------------------------------------

    shape = get_reference_shape(shape_tool)

    # ----------------------------------------
    # Extract solids
    # ----------------------------------------

    solids = extract_solids(shape)

    processed_solids = []

    # ----------------------------------------
    # Store scaled seat information
    # ----------------------------------------

    scaled_seat = None
    seat_scale_info = None

    # ----------------------------------------
    # Process every body
    # ----------------------------------------
    all_bodies = []
    for solid, body_name in zip(solids, body_names):

        print("\n" + "=" * 60)
        print(body_name)

        bbox = compute_bbox(solid)

        print_bbox(
            body_name,
            bbox,
        )

        obb = compute_obb(solid)

        print_obb(
            body_name,
            obb,
        )

        # ----------------------------------------
        # Scale only seat
        # ----------------------------------------

    if body_name == "seat":

        solid, seat_scale_info = scale_body(
        solid=solid,
        obb=obb,
        body_name=body_name,
        logical_dimension="length",
        factor=2.0,
    )

    scaled_seat = solid

# Store EVERY body (not just the seat)
    all_bodies.append({
    "name": body_name,
    "shape": solid,
})

    processed_solids.append(solid)
    # ----------------------------------------
    # Export
    # ----------------------------------------
    overlap = get_overlap(
    scaled_seat,
    all_bodies[1]["shape"],
    seat_scale_info,
)
    
    
    # ----------------------------------------
# Build attachment map
# ----------------------------------------

attachment_map = []

seat_obb = get_obb(scaled_seat)

for body in all_bodies:

    if body["name"] == "seat":
        continue

    vec = vector_between(
        scaled_seat,
        body["shape"],
    )

    px = projection_on_axis(
        vec,
        seat_obb.XDirection(),
    )

    py = projection_on_axis(
        vec,
        seat_obb.YDirection(),
    )

    pz = projection_on_axis(
        vec,
        seat_obb.ZDirection(),
    )

    sign, axis = classify_attachment(
        px,
        py,
        pz,
    )

    attachment_map.append({

        "name": body["name"],

        "shape": body["shape"],

        "sign": sign,

        "axis": axis,

    })
    
    
    # ----------------------------------------
# Move attached bodies
# ----------------------------------------

for item in attachment_map:

    # Move only bodies attached along
    # the seat length
    if item["axis"] != seat_scale_info["logical_axis"]:
        continue

    overlap = get_overlap(
        scaled_seat,
        item["shape"],
        seat_scale_info,
    )

    # Positive side (right arm)
    if item["sign"] == "+":

        item["shape"] = move_body(
            item["shape"],
            seat_scale_info["direction"],
            overlap,
        )

    # Negative side (left arm)
    else:

        item["shape"] = move_body(
            item["shape"],
            seat_scale_info["direction"],
            -overlap,
        )
        
    
    
    # ----------------------------------------
# Update processed solids
# ----------------------------------------

for i, body_name in enumerate(body_names):

    if body_name == "seat":
        processed_solids[i] = scaled_seat
        continue

    for item in attachment_map:

        if item["name"] == body_name:

            processed_solids[i] = item["shape"]
            break
    export_step(
        processed_solids,
        OUTPUT_STEP,
    )


if __name__ == "__main__":
    main()