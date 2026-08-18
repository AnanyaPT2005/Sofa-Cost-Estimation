"""
STEP reader and metadata utilities.
"""

import json
import re

from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone

from bbox_engine import (
    compute_bbox,
    compute_obb,
)

from position_engine import make_compound


# ---------------------------------------------------------
# NAME NORMALIZATION
# ---------------------------------------------------------

def normalize_body_name(
    name,
):
    """
    Normalize STEP and metadata body names.
    """

    name = str(name)

    name = (
        name
        .strip()
        .lower()
        .replace(" ", "_")
    )

    name = re.sub(
        r"_+",
        "_",
        name,
    )

    return name


# ---------------------------------------------------------
# METADATA
# ---------------------------------------------------------

def load_metadata(
    metadata_file,
):
    """
    Load category metadata.
    """

    with open(
        metadata_file,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ---------------------------------------------------------
# STEP READER
# ---------------------------------------------------------

def read_step(
    step_file,
):
    """
    Read STEP file.
    """

    reader = STEPControl_Reader()

    status = reader.ReadFile(
        step_file
    )

    if status != IFSelect_RetDone:
        raise RuntimeError(
            "STEP reading failed."
        )

    print(
        "STEP file loaded successfully"
    )

    reader.TransferRoots()

    return reader.OneShape()


# ---------------------------------------------------------
# CATEGORY BODY NAMES
# ---------------------------------------------------------

def get_category_body_names(
    category,
    metadata,
):
    """
    Return normalized body names belonging
    to a category.
    """

    if category not in metadata:
        raise ValueError(
            f"Category '{category}' "
            f"not found in metadata."
        )

    return {
        normalize_body_name(name)
        for name in metadata[category]
    }


# ---------------------------------------------------------
# CATEGORY SOLIDS
# ---------------------------------------------------------

def get_category_solids(
    category,
    metadata,
    solids,
    body_names,
):
    """
    Extract all solids belonging to a category.
    """

    expected_names = (
        get_category_body_names(
            category,
            metadata,
        )
    )

    category_solids = []

    for solid, body_name in zip(
        solids,
        body_names,
    ):

        normalized_name = (
            normalize_body_name(
                body_name
            )
        )

        if normalized_name in expected_names:

            category_solids.append(
                solid
            )

    if not category_solids:
        raise ValueError(
            f"No solids found for "
            f"category '{category}'."
        )

    return category_solids


# ---------------------------------------------------------
# CATEGORY SHAPE
# ---------------------------------------------------------

def get_category_shape(
    category,
    metadata,
    solids,
    body_names,
):
    """
    Create a compound from category solids.
    """

    category_solids = (
        get_category_solids(
            category,
            metadata,
            solids,
            body_names,
        )
    )

    return make_compound(
        category_solids
    )


# ---------------------------------------------------------
# TEMPLATE FRAME
# ---------------------------------------------------------

def get_template_frame(
    reference_shape,
):
    """
    Return OBB directions of reference shape.

    Used only for inspection/legacy functionality.
    """

    obb = compute_obb(
        reference_shape
    )

    return {
        "X": obb.XDirection(),
        "Y": obb.YDirection(),
        "Z": obb.ZDirection(),
    }


# ---------------------------------------------------------
# BODY AXIS MAP
# ---------------------------------------------------------

def get_body_axis_map(
    obb,
):
    """
    Determine which OBB axis is closest to
    global X/Y/Z.

    This function is retained for debugging.
    It is NOT used by the new global scaling system.
    """

    obb_axes = {
        "X": obb.XDirection(),
        "Y": obb.YDirection(),
        "Z": obb.ZDirection(),
    }

    global_axes = {
        "length": (1, 0, 0),
        "width": (0, 1, 0),
        "height": (0, 0, 1),
    }

    mapping = {}

    used = set()

    for logical_dimension, global_axis in (
        global_axes.items()
    ):

        best_axis = None
        best_score = -1.0

        for axis_name, direction in (
            obb_axes.items()
        ):

            if axis_name in used:
                continue

            score = abs(
                direction.X()
                * global_axis[0]
                +
                direction.Y()
                * global_axis[1]
                +
                direction.Z()
                * global_axis[2]
            )

            if score > best_score:

                best_score = score
                best_axis = axis_name

        mapping[
            logical_dimension
        ] = best_axis

        used.add(
            best_axis
        )

    return mapping


# ---------------------------------------------------------
# CATEGORY DIMENSIONS
# ---------------------------------------------------------

def get_category_dimensions(
    category,
    metadata,
    solids,
    body_names,
    template_frame=None,
):
    """
    Calculate global AABB dimensions of a category.
    """

    category_names = (
        get_category_body_names(
            category,
            metadata,
        )
    )

    xmin = float("inf")
    ymin = float("inf")
    zmin = float("inf")

    xmax = float("-inf")
    ymax = float("-inf")
    zmax = float("-inf")

    found = False

    for solid, body_name in zip(
        solids,
        body_names,
    ):

        normalized_name = (
            normalize_body_name(
                body_name
            )
        )

        if normalized_name not in category_names:
            continue

        found = True

        box = compute_bbox(
            solid
        )

        bxmin, bymin, bzmin, bxmax, bymax, bzmax = (
            box.Get()
        )

        xmin = min(
            xmin,
            bxmin,
        )

        ymin = min(
            ymin,
            bymin,
        )

        zmin = min(
            zmin,
            bzmin,
        )

        xmax = max(
            xmax,
            bxmax,
        )

        ymax = max(
            ymax,
            bymax,
        )

        zmax = max(
            zmax,
            bzmax,
        )

    if not found:
        raise ValueError(
            f"No bodies found for "
            f"category '{category}'."
        )

    return {
        "length": xmax - xmin,
        "width": ymax - ymin,
        "height": zmax - zmin,
    }


# ---------------------------------------------------------
# BODY DIMENSIONS
# ---------------------------------------------------------

def get_body_dimensions(
    category,
    metadata,
    solids,
    body_names,
):
    """
    Return dimensions for every body
    in a category.
    """

    category_names = (
        get_category_body_names(
            category,
            metadata,
        )
    )

    result = {}

    for solid, body_name in zip(
        solids,
        body_names,
    ):

        normalized_name = (
            normalize_body_name(
                body_name
            )
        )

        if normalized_name not in category_names:
            continue

        box = compute_bbox(
            solid
        )

        xmin, ymin, zmin, xmax, ymax, zmax = (
            box.Get()
        )

        result[body_name] = {
            "length": xmax - xmin,
            "width": ymax - ymin,
            "height": zmax - zmin,
        }

    return result


# ---------------------------------------------------------
# GLOBAL X DEBUG
# ---------------------------------------------------------

def print_global_length_bounds(
    solids,
    body_names,
):
    """
    Print global X bounds.
    """

    xmin_global = float("inf")
    xmax_global = float("-inf")

    print("\nGlobal X Bounds")

    for solid, body_name in zip(
        solids,
        body_names,
    ):

        box = compute_bbox(
            solid
        )

        xmin, ymin, zmin, xmax, ymax, zmax = (
            box.Get()
        )

        xmin_global = min(
            xmin_global,
            xmin,
        )

        xmax_global = max(
            xmax_global,
            xmax,
        )

        print(
            f"{body_name}: "
            f"X = {xmin:.2f} "
            f"to {xmax:.2f}"
        )

    global_length = (
        xmax_global - xmin_global
    )

    print(
        f"\nGLOBAL X = "
        f"{xmin_global:.2f} "
        f"to {xmax_global:.2f}"
    )

    print(
        f"GLOBAL LENGTH = "
        f"{global_length:.2f}"
    )

    return (
        xmin_global,
        xmax_global,
        global_length,
    )