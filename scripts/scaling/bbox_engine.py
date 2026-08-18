"""
Bounding box utilities for STEP assembly processing.
"""

from OCP.Bnd import Bnd_Box, Bnd_OBB
from OCP.BRepBndLib import BRepBndLib


# ---------------------------------------------------------
# AABB
# ---------------------------------------------------------

def compute_bbox(shape):
    """
    Compute the axis-aligned bounding box of a shape.
    """

    box = Bnd_Box()

    BRepBndLib.Add_s(
        shape,
        box,
    )

    return box


# ---------------------------------------------------------
# Assembly AABB
# ---------------------------------------------------------

def compute_assembly_bbox(
    solids,
):
    """
    Compute one global AABB covering the entire assembly.
    """

    box = Bnd_Box()

    for solid in solids:

        BRepBndLib.Add_s(
            solid,
            box,
        )

    return box


# ---------------------------------------------------------
# Dimensions
# ---------------------------------------------------------

def get_bbox_dimensions(
    box,
):
    """
    Convert a Bnd_Box into global Length/Width/Height.

    X -> Length
    Y -> Width
    Z -> Height
    """

    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()

    return {
        "length": xmax - xmin,
        "width": ymax - ymin,
        "height": zmax - zmin,
    }


# ---------------------------------------------------------
# Assembly dimensions
# ---------------------------------------------------------

def get_assembly_dimensions(
    solids,
):
    """
    Calculate complete assembly dimensions.
    """

    box = compute_assembly_bbox(
        solids
    )

    return get_bbox_dimensions(
        box
    )


# ---------------------------------------------------------
# OBB
# ---------------------------------------------------------

def compute_obb(
    solid,
):
    """
    Compute an oriented bounding box.

    Kept for inspection/debugging.
    It is NO LONGER used for scaling.
    """

    obb = Bnd_OBB()

    BRepBndLib.AddOBB_s(
        solid,
        obb,
        True,
        True,
        True,
    )

    return obb


# ---------------------------------------------------------
# Printing
# ---------------------------------------------------------

def print_bbox(
    body_name,
    bbox,
):
    """
    Print AABB information.
    """

    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()

    print("\n" + "=" * 60)
    print(body_name)

    print(
        f"X : {xmin:.6f} -> {xmax:.6f}"
    )

    print(
        f"Y : {ymin:.6f} -> {ymax:.6f}"
    )

    print(
        f"Z : {zmin:.6f} -> {zmax:.6f}"
    )

    print(
        f"L = {xmax - xmin:.6f}"
    )

    print(
        f"W = {ymax - ymin:.6f}"
    )

    print(
        f"H = {zmax - zmin:.6f}"
    )


# ---------------------------------------------------------
# OBB printing
# ---------------------------------------------------------

def print_obb(
    body_name,
    obb,
):
    """
    Print OBB information for debugging.
    """

    print("\n" + "=" * 60)
    print(
        f"OBB for {body_name}"
    )

    center = obb.Center()

    print(
        f"Center : "
        f"({center.X():.6f}, "
        f"{center.Y():.6f}, "
        f"{center.Z():.6f})"
    )

    xdir = obb.XDirection()
    ydir = obb.YDirection()
    zdir = obb.ZDirection()

    print(
        f"Local X : "
        f"({xdir.X():.6f}, "
        f"{xdir.Y():.6f}, "
        f"{xdir.Z():.6f})"
    )

    print(
        f"Local Y : "
        f"({ydir.X():.6f}, "
        f"{ydir.Y():.6f}, "
        f"{ydir.Z():.6f})"
    )

    print(
        f"Local Z : "
        f"({zdir.X():.6f}, "
        f"{zdir.Y():.6f}, "
        f"{zdir.Z():.6f})"
    )

    print(
        f"OBB X Size : "
        f"{2 * obb.XHSize():.6f}"
    )

    print(
        f"OBB Y Size : "
        f"{2 * obb.YHSize():.6f}"
    )

    print(
        f"OBB Z Size : "
        f"{2 * obb.ZHSize():.6f}"
    )