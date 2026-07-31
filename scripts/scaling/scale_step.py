from OCP.gp import gp_Trsf, gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform


def scale_seat(solid):
    """
    Test transformation.

    Moves the seat +10 mm along X.
    """

    trsf = gp_Trsf()

    trsf.SetTranslation(
        gp_Vec(10, 0, 0)
    )

    transformer = BRepBuilderAPI_Transform(
        solid,
        trsf,
        True
    )

    transformed = transformer.Shape()

    print("Seat translated +10 mm")

    return transformed