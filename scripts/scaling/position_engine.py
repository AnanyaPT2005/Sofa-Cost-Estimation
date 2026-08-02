from OCP.gp import (
    gp_Trsf,
    gp_Vec,
)
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

from OCP.BRepBuilderAPI import (
    BRepBuilderAPI_Transform,
)

from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib


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
    dx,
    dy,
    dz,
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
            dx,
            dy,
            dz,
        )
    )

    transformer = BRepBuilderAPI_Transform(
        solid,
        trsf,
        True,
    )

    moved = transformer.Shape()

    print(
        f"Moved body by ({dx}, {dy}, {dz}) mm"
    )

    return moved