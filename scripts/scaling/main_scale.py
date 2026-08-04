

"""
Main pipeline for STEP processing.
"""

from body_names import get_step_body_names
from step_reader import read_step
from assembly_parser import get_reference_shape
from body_extractor import extract_solids
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


STEP_FILE = r"C:\Users\DEEPIKA.S\Desktop\sofa_cost\Sofa-Cost-Estimation\scripts\scaling\test_workfloe.step"

OUTPUT_STEP = r"C:\Users\DEEPIKA.S\Desktop\sofa_cost\Sofa-Cost-Estimation\scripts\scaling\scaled_step.step"


def main():

    body_names = get_step_body_names(STEP_FILE)

    print("\nBodies found:")

    for i, name in enumerate(body_names, start=1):
        print(f"{i}. {name}")

    shape_tool = read_step(STEP_FILE)

    shape = get_reference_shape(shape_tool)

    solids = extract_solids(shape)

    processed_solids = []

    all_bodies = []

    scaled_seat = None
    seat_scale_info = None

    right_arm = None

    # ----------------------------------------------------
    # Process all bodies
    # ----------------------------------------------------

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

        # -----------------------------
        # Scale Seat
        # -----------------------------

        if body_name == "seat":

            solid, seat_scale_info = scale_body(
                solid=solid,
                obb=obb,
                body_name="seat",
                logical_dimension="length",
                factor=0.5,
            )

            scaled_seat = solid

            print("\nScale Info")

            for k, v in seat_scale_info.items():
                print(k, ":", v)

        elif body_name == "right_arm":

            right_arm = solid

        all_bodies.append(
            {
                "name": body_name,
                "shape": solid,
            }
        )

        processed_solids.append(solid)
        # ----------------------------------------------------
    # Compute overlap using right arm
    # ----------------------------------------------------

    overlap = get_overlap(
        scaled_seat,
        right_arm,
        seat_scale_info,
    )

    print("\nOverlap :", overlap)

    # ----------------------------------------------------
    # Build attachment map
    # ----------------------------------------------------

    attachment_map = []

    seat_obb = get_obb(scaled_seat)

    x_axis = seat_obb.XDirection()
    y_axis = seat_obb.YDirection()
    z_axis = seat_obb.ZDirection()

    for body in all_bodies:

        if body["name"] == "seat":
            continue

        vec = vector_between(
            scaled_seat,
            body["shape"],
        )

        px = projection_on_axis(
            vec,
            x_axis,
        )

        py = projection_on_axis(
            vec,
            y_axis,
        )

        pz = projection_on_axis(
            vec,
            z_axis,
        )

        sign, axis = classify_attachment(
            px,
            py,
            pz,
        )

        logical = get_logical_dimension(
            "seat",
            axis,
        )

        attachment_map.append(
            {
                "name": body["name"],
                "shape": body["shape"],
                "attachment": f"{sign}{logical}",
            }
        )

    print("\nAttachment Map")

    for item in attachment_map:

        print(
            item["name"],
            "->",
            item["attachment"],
        )

    # ----------------------------------------------------
    # Move attached bodies
    # ----------------------------------------------------

    print("\nMoving Bodies")

    for item in attachment_map:

        attachment = item["attachment"]

        sign = attachment[0]

        logical_dimension = attachment[1:]

        # Move only bodies attached to the scaled dimension
        if logical_dimension != seat_scale_info["logical_dimension"]:
            continue

        if sign == "+":

            item["shape"] = move_body(
                item["shape"],
                seat_scale_info["direction"],
                overlap,
            )

            print(
                item["name"],
                "moved",
                attachment,
            )

        elif sign == "-":

            item["shape"] = move_body(
                item["shape"],
                seat_scale_info["direction"],
                -overlap,
            )

            print(
                item["name"],
                "moved",
                attachment,
            )

    # ----------------------------------------------------
    # Replace moved bodies
    # ----------------------------------------------------

    for i, body_name in enumerate(body_names):

        if body_name == "seat":

            processed_solids[i] = scaled_seat

        else:

            for item in attachment_map:

                if item["name"] == body_name:

                    processed_solids[i] = item["shape"]
                    break

    # ----------------------------------------------------
    # Export STEP
    # ----------------------------------------------------

    export_step(
        processed_solids,
        OUTPUT_STEP,
    )


if __name__ == "__main__":
    main()