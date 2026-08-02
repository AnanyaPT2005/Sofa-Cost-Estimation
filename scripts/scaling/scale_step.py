# from OCP.gp import gp_GTrsf, gp_Mat
# from OCP.BRepBuilderAPI import BRepBuilderAPI_GTransform


# def scale_seat(solid, obb):    """
#     Test:
#     Double the seat length along the X direction.
#     """

#     # Scaling matrix
#     mat = gp_Mat(
#         2.0, 0.0, 0.0,
#         0.0, 1.0, 0.0,
#         0.0, 0.0, 1.0,
#     )

#     gtrsf = gp_GTrsf()
#     gtrsf.SetVectorialPart(mat)

#     transformer = BRepBuilderAPI_GTransform(
#         solid,
#         gtrsf,
#         True,
#     )

#     transformed = transformer.Shape()

#     print("Seat scaled 2x along X")

#     return transformed

from OCP.gp import gp_Ax3
from OCP.gp import (
    gp_GTrsf,
    gp_Mat,
    gp_XYZ,
)


def scale_seat(solid, obb):
    """
    Test that the OBB is available inside the scaling function.
    """

    center = obb.Center()

    xdir = obb.XDirection()
    ydir = obb.YDirection()
    zdir = obb.ZDirection()
    basis = gp_Mat(
    xdir.X(), ydir.X(), zdir.X(),
    xdir.Y(), ydir.Y(), zdir.Y(),
    xdir.Z(), ydir.Z(), zdir.Z(),
    )

    print("\nBasis Matrix:")
    print(basis)
    inv_basis = basis.Inverted()
    gtrsf = gp_GTrsf()

    print("\ngp_GTrsf methods:")

    for m in sorted(dir(gtrsf)):
        if not m.startswith("_"):
            print(m)
    print("\nBasis methods:")

    for m in sorted(dir(basis)):
        if not m.startswith("_"):
            print(m)

    print("\nInverse Basis:")
    print(inv_basis)

    print("\n========== SCALE INFO ==========")

    print(
        f"Center : ({center.X():.2f}, "
        f"{center.Y():.2f}, "
        f"{center.Z():.2f})"
    )

    print(
        f"Local X : ({xdir.X():.3f}, "
        f"{xdir.Y():.3f}, "
        f"{xdir.Z():.3f})"
    )

    print(
        f"Local Y : ({ydir.X():.3f}, "
        f"{ydir.Y():.3f}, "
        f"{ydir.Z():.3f})"
    )

    print(
        f"Local Z : ({zdir.X():.3f}, "
        f"{zdir.Y():.3f}, "
        f"{zdir.Z():.3f})"
    )

    print("\nSeat scaling will be implemented next...")

    return solid