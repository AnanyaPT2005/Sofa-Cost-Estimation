#this is scaling_pipeline
from bbox_engine import (
    compute_obb,
    print_bbox,
)
from OCP.gp import gp_Vec, gp_Pnt
from OCP.gp import gp_Vec
from step_reader import get_category_bounds
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
    make_compound,
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

def get_armrest_side(body_name):

    name = body_name.lower().replace(" ", "_")

    if name.startswith("left_armrest"):
        return "left"

    if name.startswith("right_armrest"):
        return "right"

    return None

def get_global_attachment(reference_shape, body_shape):
    """
    Determine which global direction the body lies from
    the reference category.

    Global convention:
        X = length
        Z = width
        Y = height
    """

    ref_obb = get_obb(reference_shape)
    body_obb = get_obb(body_shape)

    ref = ref_obb.Center()
    body = body_obb.Center()

    dx = body.X() - ref.X()
    dy = body.Y() - ref.Y()
    dz = body.Z() - ref.Z()

    values = {
        "length": dx,
        "width": dz,
        "height": dy,
    }

    logical_dimension = max(
        values,
        key=lambda k: abs(values[k])
    )

    value = values[logical_dimension]

    sign = "+" if value >= 0 else "-"

    return sign, logical_dimension

def process_dimension(
    solids,
    body_names,
    logical_dimension,
    factor,
    metadata,
    reference_category="seat",
):
    old_reference_bounds = get_category_bounds(
        reference_category,
        metadata,
        solids,
        body_names,
    )       
    processed_solids = []
    scaled_reference_bodies = {}

    all_bodies = []

    reference_shapes = []
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
        # print(f"\n{body_name}")
        # print("X:", obb.XDirection().X(), obb.XDirection().Y(), obb.XDirection().Z())
        # print("Y:", obb.YDirection().X(), obb.YDirection().Y(), obb.YDirection().Z())
        # print("Z:", obb.ZDirection().X(), obb.ZDirection().Y(), obb.ZDirection().Z())

        if body_name in metadata[reference_category]:

            solid, scale_info = scale_body(
                solid=solid,
                obb=obb,
                body_name=reference_category,
                logical_dimension=logical_dimension,
                factor=factor,
            )

            scaled_reference_bodies[body_name] = solid

            reference_shapes.append(solid)

            if reference_scale_info is None:
                reference_scale_info = scale_info


        all_bodies.append(
            {
                "name": body_name,
                "shape": solid,
            }
        )

        processed_solids.append(solid)
    new_reference_bounds = get_category_bounds(
        reference_category,
        metadata,
        processed_solids,
        body_names,
    )

    # -----------------------------------------
    # Calculate ACTUAL growth
    # -----------------------------------------

    old_xmin, old_ymin, old_zmin, old_xmax, old_ymax, old_zmax = old_reference_bounds

    new_xmin, new_ymin, new_zmin, new_xmax, new_ymax, new_zmax = new_reference_bounds


    growth = {
        "length": (new_xmax - new_xmin) - (old_xmax - old_xmin),
        "width":  (new_zmax - new_zmin) - (old_zmax - old_zmin),
        "height": (new_ymax - new_ymin) - (old_ymax - old_ymin),
    }

    # print("\nOverlap :", overlap)
    reference_shape = make_compound(reference_shapes)

    # ----------------------------------------------------
    # Build attachment map
    # ----------------------------------------------------

    attachment_map = []

    for body in all_bodies:

        if body["name"] in metadata[reference_category]:
            continue

        sign, logical = get_global_attachment(
            reference_shape,
            body["shape"],
        )

        attachment_map.append(
            {
                "name": body["name"],
                "shape": body["shape"],
                "attachment": f"{sign}{logical}",
            }
        )  
    # print("\nAttachment Map")

    # for item in attachment_map:

    #     print(
    #         item["name"],
    #         "->",
    #         item["attachment"],
    #     )

    # ----------------------------------------------------
    # Move attached bodies
    # ----------------------------------------------------
    # ----------------------------------------------------
    # Move armrests as complete left/right groups
    # ----------------------------------------------------
    if (
        reference_category == "seat"
        and logical_dimension == "length"
    ):

        half_growth = growth["length"] / 2

        for item in attachment_map:

            side = get_armrest_side(item["name"])

            if side == "left":

                item["shape"] = move_body(
                    item["shape"],
                    gp_Vec(1, 0, 0),
                    half_growth,
                )

            elif side == "right":

                item["shape"] = move_body(
                    item["shape"],
                    gp_Vec(1, 0, 0),
                    -half_growth,
                ) 

                
            # print(
            #     item["name"],
            #     "moved",
            #     attachment,
            # )

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