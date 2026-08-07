#this is scaling_pipeline
from bbox_engine import (
    compute_obb,
    print_bbox,
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

SCALING_RULES = {
    "length": [
        "seat",
    ],
    "width": [
        "seat",
        "armrest",
    ],
    "height": [
        "backrest",
    ],
}

def process_dimension(
    solids,
    body_names,
    logical_dimension,
    factor,
    metadata,
    reference_category="seat",
):       
    processed_solids = []
    scaled_reference_bodies = {}

    all_bodies = []

    reference_shape = None
    reference_scale_info = None

   

    # ----------------------------------------------------
    # Process all bodies
    # ----------------------------------------------------

    for solid, body_name in zip(solids, body_names):

        # print("\n" + "=" * 60)
        # print(body_name)

        # print_bbox(
        #     body_name,
        #     bbox,
        # )

        obb = compute_obb(solid)

        # print_obb(
        #     body_name,
        #     obb,
        # )
        print(f"\n{body_name}")
        print("X:", obb.XDirection().X(), obb.XDirection().Y(), obb.XDirection().Z())
        print("Y:", obb.YDirection().X(), obb.YDirection().Y(), obb.YDirection().Z())
        print("Z:", obb.ZDirection().X(), obb.ZDirection().Y(), obb.ZDirection().Z())

        # -----------------------------
        # Scale Seat
        # -----------------------------

        if body_name in metadata[reference_category]:

            solid, scale_info = scale_body(
                solid=solid,
                obb=obb,
                body_name=reference_category,
                logical_dimension=logical_dimension,
                factor=factor,
            )

            scaled_reference_bodies[body_name] = solid

            if reference_shape is None:
                reference_shape = solid
                reference_scale_info = scale_info


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

    # overlap = get_overlap(
    #     reference_shape,
    #     right_arm,
    #     seat_scale_info,
    # )

    # print("\nOverlap :", overlap)

    # ----------------------------------------------------
    # Build attachment map
    # ----------------------------------------------------

    attachment_map = []

    reference_obb = get_obb(reference_shape)

    x_axis = reference_obb.XDirection()
    y_axis = reference_obb.YDirection()
    z_axis = reference_obb.ZDirection()

    for body in all_bodies:

        if body["name"] in metadata[reference_category]:
            continue

        vec = vector_between(
           reference_shape,
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
            reference_category,
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

        attachment_dimension = attachment[1:]

        # Move only bodies attached to the scaled dimension
        if attachment_dimension != reference_scale_info["logical_dimension"]:
            continue

        overlap = get_overlap(
            reference_shape,
            item["shape"],
            reference_scale_info,
        )

        if sign == "+":

            item["shape"] = move_body(
                item["shape"],
                reference_scale_info["direction"],
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
                reference_scale_info["direction"],
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

        if body_name in metadata[reference_category]:

            processed_solids[i] = scaled_reference_bodies[body_name]

        else:

            for item in attachment_map:

                if item["name"] == body_name:

                    processed_solids[i] = item["shape"]
                    break
    return processed_solids