from OCP.gp import (
    gp_Trsf,
    gp_Vec,
)
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_OBB
from OCP.BRepBndLib import BRepBndLib
from OCP.gp import gp_Vec
from OCP.gp import gp_Pnt, gp_Vec
from OCP.gp import gp_Dir

from OCP.BRepBuilderAPI import (
    BRepBuilderAPI_Transform,
)

from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

def get_obb(shape):

    obb = Bnd_OBB()

    BRepBndLib.AddOBB_s(
        shape,
        obb,
        True,
        True,
        True,
    )

    return obb

def get_center(shape):

    obb = get_obb(shape)

    return obb.Center()

from OCP.gp import gp_Pnt, gp_Vec

def vector_between(shape1, shape2):

    c1 = get_center(shape1)
    c2 = get_center(shape2)

    p1 = gp_Pnt(
        c1.X(),
        c1.Y(),
        c1.Z(),
    )

    p2 = gp_Pnt(
        c2.X(),
        c2.Y(),
        c2.Z(),
    )

    return gp_Vec(
        p1,
        p2,
    )

def get_bbox(shape):

    box = Bnd_Box()

    BRepBndLib.Add_s(
        shape,
        box,
    )

    return box


def get_bounds(shape):

    box = get_bbox(shape)

    return box.Get()

def get_overlap(
    fixed_body,
    moving_body,
    scale_info,
):
    """
    Returns the overlap distance along
    the scaled direction.
    """

    xmin1, ymin1, zmin1, xmax1, ymax1, zmax1 = get_bounds(fixed_body)

    xmin2, ymin2, zmin2, xmax2, ymax2, zmax2 = get_bounds(moving_body)

    direction = scale_info["direction"]

    # X movement
    if abs(direction.X()) > 0.9:

        return xmax1 - xmin2

    # Y movement
    elif abs(direction.Y()) > 0.9:

        return ymax1 - ymin2

    # Z movement
    else:

        return zmax1 - zmin2


def move_body(
    solid,
    direction,
    distance,
):
    """
    Translate a body.

    Parameters
    ----------
    solid : TopoDS_Shape
    dx, dy, dz : translation in mm
    """

    trsf = gp_Trsf()

    trsf.SetTranslation(
    gp_Vec(
        direction.X() * distance,
        direction.Y() * distance,
        direction.Z() * distance,
    )
    )

    transformer = BRepBuilderAPI_Transform(
        solid,
        trsf,
        True,
    )

    moved = transformer.Shape()

    dx = direction.X() * distance
    dy = direction.Y() * distance
    dz = direction.Z() * distance

    print(
        f"Moved body by ({dx:.2f}, {dy:.2f}, {dz:.2f}) mm"
    )

    return moved

def projection_on_axis(
    vector,
    axis,
):
    """
    Returns the signed projection of
    vector onto axis.
    """

    axis_vec = gp_Vec(
        axis.X(),
        axis.Y(),
        axis.Z(),
    )

    return vector.Dot(axis_vec)

def classify_attachment(
    px,
    py,
    pz,
):

    values = {
        "X": px,
        "Y": py,
        "Z": pz,
    }

    dominant_axis = max(
        values,
        key=lambda k: abs(values[k]),
    )

    if values[dominant_axis] >= 0:
        sign = "+"
    else:
        sign = "-"

    return sign, dominant_axis