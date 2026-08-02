from OCP.gp import (
    gp_Trsf,
    gp_Vec,
)

from OCP.BRepBuilderAPI import (
    BRepBuilderAPI_Transform,
)


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