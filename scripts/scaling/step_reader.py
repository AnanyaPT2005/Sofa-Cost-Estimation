#this is a loader.py

import json
from bbox_engine import compute_obb
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

from bbox_engine import compute_bbox
from OCP.gp import gp_Vec

def read_step(step_file):

    reader = STEPControl_Reader()

    status = reader.ReadFile(step_file)

    if status != IFSelect_RetDone:
        raise RuntimeError("STEP reading failed")

    print("STEP file loaded successfully")

    reader.TransferRoots()

    return reader.OneShape()


def load_metadata(metadata_file):

    with open(metadata_file, "r") as f:
        return json.load(f)
    
def get_template_frame(reference_shape):

    obb = compute_obb(reference_shape)

    return {
        "X": obb.XDirection(),
        "Y": obb.YDirection(),
        "Z": obb.ZDirection(),
    }

def get_assembly_dimensions(solids):

    box = Bnd_Box()

    for solid in solids:

        BRepBndLib.Add_s(
            solid,
            box,
        )

    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()

    return {
        "length": xmax - xmin,
        "width": zmax - zmin,
        "height": ymax - ymin,
    }

def get_body_axis_map(obb):
    """
    Determine which OBB axis corresponds to each global logical axis.

    Global coordinate convention:
        X -> length
        Z -> width
        Y -> height
    """

    obb_axes = {
        "X": obb.XDirection(),
        "Y": obb.YDirection(),
        "Z": obb.ZDirection(),
    }

    global_axes = {
        "length": (1, 0, 0),   # global X
        "width":  (0, 0, 1),   # global Z
        "height": (0, 1, 0),   # global Y
    }

    mapping = {}

    used_obb_axes = set()

    for logical_dimension, global_axis in global_axes.items():

        best_axis = None
        best_score = -1

        for obb_axis_name, direction in obb_axes.items():

            if obb_axis_name in used_obb_axes:
                continue

            dx = direction.X()
            dy = direction.Y()
            dz = direction.Z()

            score = abs(
                dx * global_axis[0]
                + dy * global_axis[1]
                + dz * global_axis[2]
            )

            if score > best_score:
                best_score = score
                best_axis = obb_axis_name

        mapping[logical_dimension] = best_axis
        used_obb_axes.add(best_axis)

    return mapping

# -------------------------------------------------
# Body Dimensions
# -------------------------------------------------


def get_body_dimensions(
    category,
    metadata,
    solids,
    body_names,
):
    """
    Returns the logical OBB dimensions
    of every body belonging to a category.
    """

    dimensions = {}

    for solid, body_name in zip(solids, body_names):

        if body_name not in metadata[category]:
            continue

        obb = compute_obb(solid)

        axis_sizes = {
            "X": 2 * obb.XHSize(),
            "Y": 2 * obb.YHSize(),
            "Z": 2 * obb.ZHSize(),
        }
        # axis_map = get_body_axis_map(obb)
        # obb_axis = axis_map[logical_dimension]

        mapping = get_body_axis_map(obb)

        body_dimensions = {}

        for logical_dimension, obb_axis in mapping.items():

            body_dimensions[logical_dimension] = axis_sizes[obb_axis]

        dimensions[body_name] = body_dimensions

    return dimensions


def get_category_dimensions(
    category,
    metadata,
    solids,
    body_names,
    template_frame=None,
):
    """
    Compute the enclosing bounding box of all bodies
    belonging to a category.

    For the current company STEP model:
        X -> logical length
        Z -> logical width
        Y -> logical height
    """

    xmin = float("inf")
    ymin = float("inf")
    zmin = float("inf")

    xmax = float("-inf")
    ymax = float("-inf")
    zmax = float("-inf")

    found = False

    for solid, body_name in zip(solids, body_names):

        if body_name not in metadata[category]:
            continue

        found = True

        box = compute_bbox(solid)

        bxmin, bymin, bzmin, bxmax, bymax, bzmax = box.Get()

        xmin = min(xmin, bxmin)
        ymin = min(ymin, bymin)
        zmin = min(zmin, bzmin)

        xmax = max(xmax, bxmax)
        ymax = max(ymax, bymax)
        zmax = max(zmax, bzmax)

    if not found:
        raise ValueError(
            f"No bodies found for category '{category}'"
        )

    # -----------------------------------------
    # Logical dimensions for company STEP model
    # -----------------------------------------

    dimensions = {
        "length": xmax - xmin,   # X
        "width":  zmax - zmin,   # Z
        "height": ymax - ymin,   # Y
    }

    return dimensions

def print_global_length_bounds(solids, body_names):
    print("\nGlobal X Bounds")

    xmin_global = float("inf")
    xmax_global = float("-inf")

    for solid, body_name in zip(solids, body_names):

        box = compute_bbox(solid)

        xmin, ymin, zmin, xmax, ymax, zmax = box.Get()

        if xmin < xmin_global:
            xmin_global = xmin

        if xmax > xmax_global:
            xmax_global = xmax

        print(
            f"{body_name}: "
            f"X = {xmin:.2f} to {xmax:.2f}"
        )

    print(
        f"\nGLOBAL X = "
        f"{xmin_global:.2f} to {xmax_global:.2f}"
    )

    print(
        f"GLOBAL LENGTH = "
        f"{xmax_global - xmin_global:.2f}"
    )

def get_category_bounds(
    category,
    metadata,
    solids,
    body_names,
):
    """
    Returns the global AABB of all bodies in a category.
    """

    box = Bnd_Box()

    found = False

    for solid, body_name in zip(solids, body_names):

        if body_name not in metadata[category]:
            continue

        BRepBndLib.Add_s(
            solid,
            box,
        )

        found = True

    if not found:
        raise ValueError(
            f"No bodies found for category '{category}'"
        )

    return box.Get()