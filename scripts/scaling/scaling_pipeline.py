"""
Assembly scaling pipeline.

The pipeline calculates all three scale factors from the
ORIGINAL assembly bounding box and applies one global
transformation to the complete assembly.
"""

from bbox_engine import (
    compute_assembly_bbox,
    get_bbox_dimensions,
)

from scale_step import scale_assembly


def calculate_scale_factors(
    current_dimensions,
    target_length,
    target_width,
    target_height,
):
    """
    Calculate independent global scale factors for
    X, Y and Z.
    """

    current_length = current_dimensions["length"]
    current_width = current_dimensions["width"]
    current_height = current_dimensions["height"]

    if current_length <= 0:
        raise ValueError(
            "Current assembly length is zero or invalid."
        )

    if current_width <= 0:
        raise ValueError(
            "Current assembly width is zero or invalid."
        )

    if current_height <= 0:
        raise ValueError(
            "Current assembly height is zero or invalid."
        )

    length_factor = (
        target_length / current_length
    )

    width_factor = (
        target_width / current_width
    )

    height_factor = (
        target_height / current_height
    )

    return {
        "length": length_factor,
        "width": width_factor,
        "height": height_factor,
    }


def process_assembly(
    solids,
    target_length,
    target_width,
    target_height,
):
    """
    Scale the entire assembly to the requested dimensions.
    """

    print("\n")
    print("=" * 70)
    print("GLOBAL ASSEMBLY SCALING")
    print("=" * 70)

    # -------------------------------------------------
    # ORIGINAL ASSEMBLY BOUNDING BOX
    # -------------------------------------------------

    bbox = compute_assembly_bbox(
        solids
    )

    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()

    center = bbox_center_from_bounds(
        xmin,
        ymin,
        zmin,
        xmax,
        ymax,
        zmax,
    )

    current_dimensions = get_bbox_dimensions(
        bbox
    )

    print("\nORIGINAL ASSEMBLY")
    print(
        f"Length : {current_dimensions['length']:.6f} mm"
    )
    print(
        f"Width  : {current_dimensions['width']:.6f} mm"
    )
    print(
        f"Height : {current_dimensions['height']:.6f} mm"
    )

    print("\nORIGINAL BOUNDS")
    print(
        f"X : {xmin:.6f} -> {xmax:.6f}"
    )
    print(
        f"Y : {ymin:.6f} -> {ymax:.6f}"
    )
    print(
        f"Z : {zmin:.6f} -> {zmax:.6f}"
    )

    print("\nASSEMBLY CENTER")
    print(
        f"X : {center.X():.6f}"
    )
    print(
        f"Y : {center.Y():.6f}"
    )
    print(
        f"Z : {center.Z():.6f}"
    )

    # -------------------------------------------------
    # SCALE FACTORS
    # -------------------------------------------------

    factors = calculate_scale_factors(
        current_dimensions=current_dimensions,
        target_length=target_length,
        target_width=target_width,
        target_height=target_height,
    )

    print("\nSCALE FACTORS")
    print(
        f"Length / X : {factors['length']:.12f}"
    )
    print(
        f"Width  / Y : {factors['width']:.12f}"
    )
    print(
        f"Height / Z : {factors['height']:.12f}"
    )

    # -------------------------------------------------
    # APPLY ONE GLOBAL TRANSFORMATION
    # -------------------------------------------------

    processed_solids = scale_assembly(
        solids=solids,
        center=center,
        length_factor=factors["length"],
        width_factor=factors["width"],
        height_factor=factors["height"],
    )

    return processed_solids, factors


def bbox_center_from_bounds(
    xmin,
    ymin,
    zmin,
    xmax,
    ymax,
    zmax,
):
    """
    Create a gp_Pnt at the center of the assembly bbox.
    """

    from OCP.gp import gp_Pnt

    return gp_Pnt(
        (xmin + xmax) / 2.0,
        (ymin + ymax) / 2.0,
        (zmin + zmax) / 2.0,
    )