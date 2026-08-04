from OCP.gp import (
    gp_GTrsf,
    gp_Mat,
    gp_XYZ,
)

from OCP.BRepBuilderAPI import BRepBuilderAPI_GTransform
from OCP.gp import gp_Ax3, gp_Pnt, gp_Dir

BODY_AXIS_MAP = {
    "seat": {
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
    Converts OBB axis back to
    logical dimension.
    """

    mapping = BODY_AXIS_MAP[body_name]

    for logical, axis in mapping.items():

        if axis == obb_axis:
            return logical

    return None

def scale_seat(
    solid,
    obb,
    body_name,
    logical_dimension,
    factor,
):
    """
    Part 1:
    Build the OBB coordinate system.
    No scaling yet.
    """

    # -----------------------------
    # OBB information
    # -----------------------------

    center = obb.Center()

    xdir = obb.XDirection()
    ydir = obb.YDirection()
    zdir = obb.ZDirection()

    obb_axis = BODY_AXIS_MAP[body_name][logical_dimension]

    # ------------------------------------
    # Build the OBB coordinate system
    # ------------------------------------

    obb_frame = gp_Ax3(
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

    print("\nOBB Coordinate System Created")

    print(
        "Origin:",
        obb_frame.Location().X(),
        obb_frame.Location().Y(),
        obb_frame.Location().Z(),
    )

    print(
        "Z Axis:",
        obb_frame.Direction().X(),
        obb_frame.Direction().Y(),
        obb_frame.Direction().Z(),
    )

    print(
        "X Axis:",
        obb_frame.XDirection().X(),
        obb_frame.XDirection().Y(),
        obb_frame.XDirection().Z(),
    )

    print(
        "Y Axis:",
        obb_frame.YDirection().X(),
        obb_frame.YDirection().Y(),
        obb_frame.YDirection().Z(),
    )

    # ------------------------------------
    # Build Rotation Matrix
    # ------------------------------------

    R = gp_Mat(
        xdir.X(), ydir.X(), zdir.X(),
        xdir.Y(), ydir.Y(), zdir.Y(),
        xdir.Z(), ydir.Z(), zdir.Z(),
    )

    R_inv = R.Inverted()

    # ------------------------------------
    # Build Scale Matrix
    # ------------------------------------

    S = gp_Mat()
    S.SetIdentity()

    # Test: Double Local X
    # S.SetValue(1, 1, 2.0)
    axis_map = {
        "X": 1,
        "Y": 2,
        "Z": 3,
    }

    axis_index = axis_map[obb_axis]

    S.SetValue(axis_index, axis_index, factor)

    print("\nScale Matrix:")

    for r in range(1, 4):
        print(
            S.Value(r, 1),
            S.Value(r, 2),
            S.Value(r, 3),
        )

    # ------------------------------------
    # Final Rotation-Scale Matrix
    # ------------------------------------

    RS = R.Multiplied(S)

    FINAL = RS.Multiplied(R_inv)

    # ------------------------------------
    # Compute Translation
    # ------------------------------------

    cx = center.X()
    cy = center.Y()
    cz = center.Z()

    tx = cx - (
        FINAL.Value(1, 1) * cx +
        FINAL.Value(1, 2) * cy +
        FINAL.Value(1, 3) * cz
    )

    ty = cy - (
        FINAL.Value(2, 1) * cx +
        FINAL.Value(2, 2) * cy +
        FINAL.Value(2, 3) * cz
    )

    tz = cz - (
        FINAL.Value(3, 1) * cx +
        FINAL.Value(3, 2) * cy +
        FINAL.Value(3, 3) * cz
    )

    print("\nTranslation:")
    print(tx, ty, tz)

    # ------------------------------------
    # Create General Transformation
    # ------------------------------------

    gtrsf = gp_GTrsf()

    gtrsf.SetVectorialPart(FINAL)

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

    solid = transformer.Shape()

    print("\nTransformation applied successfully.")

    print("\nFinal Matrix:")

    for r in range(1, 4):
        print(
            f"{FINAL.Value(r,1): .3f}",
            f"{FINAL.Value(r,2): .3f}",
            f"{FINAL.Value(r,3): .3f}",
        )
    direction_map = {
            "X": xdir,
            "Y": ydir,
            "Z": zdir,
    }
    size_map = {
    "X": 2 * obb.XHSize(),
    "Y": 2 * obb.YHSize(),
    "Z": 2 * obb.ZHSize(),
    }


    old_size = size_map[obb_axis]

    scale_info = {
        

        "direction": direction_map[obb_axis],
        "logical_dimension": logical_dimension,

        "old_size": old_size,
        "new_size": old_size * factor,

        "factor": factor,
    }

    return solid, scale_info