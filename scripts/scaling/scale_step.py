print("Loading scale_step.py")
from OCP.gp import (
    gp_Ax3,
    gp_Pnt,
    gp_Dir,
    gp_Mat,
    gp_GTrsf,
    gp_XYZ,
    
)

from bbox_engine import compute_obb
from OCP.BRepBuilderAPI import (
    BRepBuilderAPI_GTransform,
   
)


BODY_AXIS_MAP = {
    "seat": {
        "length": "Z",
        "width": "Y",
        "height": "X",
    },
    "armrest": {
        "length": "Z",
        "width": "Y",
        "height": "X",
    },
    "backrest": {
        "length": "Z",
        "width": "Y",
        "height": "X",
    },
}

def get_logical_dimension(
    body_name,
    obb_axis,
):
    """
    Convert OBB axis back to logical dimension.
    """

    mapping = BODY_AXIS_MAP[body_name]

    for logical, axis in mapping.items():

        if axis == obb_axis:
            return logical

    return None


# -------------------------------------------------
# Fusion 360 Orientation Correction
# -------------------------------------------------





# -------------------------------------------------
# Build OBB Coordinate System
# -------------------------------------------------

def build_obb_frame(obb):

    center = obb.Center()

    xdir = obb.XDirection()
    ydir = obb.YDirection()
    zdir = obb.ZDirection()


    frame = gp_Ax3(
        gp_Pnt(
            center.X(),
            center.Y(),
            center.Z(),
        ),

        gp_Dir(
            zdir.X(),
            zdir.Y(),
            zdir.Z(),
        ),

        gp_Dir(
            xdir.X(),
            xdir.Y(),
            xdir.Z(),
        ),
    )


    return frame



# -------------------------------------------------
# Rotation Matrix
# -------------------------------------------------

def build_rotation_matrix(obb):

    xdir = obb.XDirection()
    ydir = obb.YDirection()
    zdir = obb.ZDirection()


    R = gp_Mat(
        xdir.X(), ydir.X(), zdir.X(),
        xdir.Y(), ydir.Y(), zdir.Y(),
        xdir.Z(), ydir.Z(), zdir.Z(),
    )


    return R, R.Inverted()



# -------------------------------------------------
# Scale Matrix
# -------------------------------------------------

def build_scale_matrix(
    logical_axis,
    factor,
):

    axis_map = {

        "X": 1,
        "Y": 2,
        "Z": 3,
    }


    S = gp_Mat()

    S.SetIdentity()


    axis = axis_map[logical_axis]


    S.SetValue(
        axis,
        axis,
        factor,
    )


    return S



# -------------------------------------------------
# Final Matrix
# -------------------------------------------------

def build_final_matrix(
    R,
    R_inv,
    S,
):

    RS = R.Multiplied(S)

    FINAL = RS.Multiplied(R_inv)

    return FINAL

# -------------------------------------------------
# Translation
# -------------------------------------------------

def compute_translation(
    center,
    FINAL,
):

    cx = center.X()
    cy = center.Y()
    cz = center.Z()


    tx = cx - (
        FINAL.Value(1,1) * cx +
        FINAL.Value(1,2) * cy +
        FINAL.Value(1,3) * cz
    )


    ty = cy - (
        FINAL.Value(2,1) * cx +
        FINAL.Value(2,2) * cy +
        FINAL.Value(2,3) * cz
    )


    tz = cz - (
        FINAL.Value(3,1) * cx +
        FINAL.Value(3,2) * cy +
        FINAL.Value(3,3) * cz
    )


    return tx, ty, tz



# -------------------------------------------------
# Apply Transformation
# -------------------------------------------------

def apply_transform(
    solid,
    FINAL,
    tx,
    ty,
    tz,
):

    gtrsf = gp_GTrsf()


    gtrsf.SetVectorialPart(
        FINAL
    )


    gtrsf.SetTranslationPart(
        gp_XYZ(
            tx,
            ty,
            tz,
        )
    )


    transformer = BRepBuilderAPI_GTransform(
        solid,
        gtrsf,
        True,
    )


    return transformer.Shape()



# -------------------------------------------------
# Scale Body
# -------------------------------------------------

def scale_body(
    solid,
    obb,
    body_name,
    logical_dimension,
    factor,
):
    obb_axis = BODY_AXIS_MAP[body_name][logical_dimension]

    # -----------------------------------------
    # Correct Fusion 360 orientation first
    # -----------------------------------------

    build_obb_frame(obb)


    # -----------------------------------------
    # OBB scaling
    # -----------------------------------------

   


    R, R_inv = build_rotation_matrix(
        obb
    )


    S = build_scale_matrix(
    obb_axis,
    factor,
)


    FINAL = build_final_matrix(
        R,
        R_inv,
        S,
    )


    tx, ty, tz = compute_translation(
        obb.Center(),
        FINAL,
    )


    scaled = apply_transform(
        solid,
        FINAL,
        tx,
        ty,
        tz,
    )


    direction_map = {

        "X": obb.XDirection(),
        "Y": obb.YDirection(),
        "Z": obb.ZDirection(),
    }


    size_map = {

        "X": 2 * obb.XHSize(),
        "Y": 2 * obb.YHSize(),
        "Z": 2 * obb.ZHSize(),
    }


    old_size = size_map[obb_axis]


    scale_info = {

    # OBB axis
    "logical_axis": obb_axis,

    # Unit direction of scaling
    "direction": direction_map[obb_axis],

    # User-selected logical dimension
    "logical_dimension": logical_dimension,

    # Sizes
    "old_size": old_size,
    "new_size": old_size * factor,

    # Amount added during scaling
    "growth": (old_size * factor) - old_size,

    # Scale factor
    "factor": factor,

    # OBB itself (needed later)
    "obb": obb,
}


    return scaled, scale_info

# -------------------------------------------------
# Body Dimensions
# -------------------------------------------------

def get_body_dimensions(
    body_name,
    obb,
):
    """
    Returns the logical dimensions of a body
    using its OBB.
    """

    axis_sizes = {
        "X": 2 * obb.XHSize(),
        "Y": 2 * obb.YHSize(),
        "Z": 2 * obb.ZHSize(),
    }

    mapping = BODY_AXIS_MAP[body_name]

    dimensions = {}

    for logical_dimension, obb_axis in mapping.items():

        dimensions[logical_dimension] = axis_sizes[obb_axis]

    return dimensions

from bbox_engine import compute_bbox
from OCP.gp import gp_Vec

def get_category_dimensions(
    category,
    metadata,
    solids,
    body_names,
    template_frame,
):

    mins = {
        "X": float("inf"),
        "Y": float("inf"),
        "Z": float("inf"),
    }

    maxs = {
        "X": float("-inf"),
        "Y": float("-inf"),
        "Z": float("-inf"),
    }

    for solid, body_name in zip(solids, body_names):

        if body_name not in metadata[category]:
            continue

        obb = compute_obb(solid)

        center = obb.Center()

        centers = {
            "X": center.X(),
            "Y": center.Y(),
            "Z": center.Z(),
        }

        half_sizes = {
            "X": obb.XHSize(),
            "Y": obb.YHSize(),
            "Z": obb.ZHSize(),
        }

        for axis_name in ["X", "Y", "Z"]:

            mins[axis_name] = min(
                mins[axis_name],
                centers[axis_name] - half_sizes[axis_name],
            )

            maxs[axis_name] = max(
                maxs[axis_name],
                centers[axis_name] + half_sizes[axis_name],
            )

    axis_sizes = {
        "X": maxs["X"] - mins["X"],
        "Y": maxs["Y"] - mins["Y"],
        "Z": maxs["Z"] - mins["Z"],
    }

    mapping = BODY_AXIS_MAP[category]

    dimensions = {}

    for logical_dimension, obb_axis in mapping.items():

        dimensions[logical_dimension] = axis_sizes[obb_axis]

    return dimensions