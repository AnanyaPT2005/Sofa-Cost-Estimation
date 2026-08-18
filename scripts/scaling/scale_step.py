"""
Global STEP assembly scaling.

The complete assembly is scaled using the global coordinate system:

    Global X -> Length
    Global Y -> Width
    Global Z -> Height

All bodies are transformed around the SAME assembly center.
This preserves the relative position of all sofa components.
"""

from OCP.gp import gp_GTrsf, gp_Mat, gp_XYZ
from OCP.BRepBuilderAPI import BRepBuilderAPI_GTransform


# ---------------------------------------------------------
# Build anisotropic global scale matrix
# ---------------------------------------------------------

def build_global_scale_matrix(
    length_factor,
    width_factor,
    height_factor,
):
    """
    Create a diagonal 3D scaling matrix.

    X -> Length
    Y -> Width
    Z -> Height
    """

    matrix = gp_Mat()

    matrix.SetIdentity()

    matrix.SetValue(
        1,
        1,
        length_factor,
    )

    matrix.SetValue(
        2,
        2,
        width_factor,
    )

    matrix.SetValue(
        3,
        3,
        height_factor,
    )

    return matrix


# ---------------------------------------------------------
# Calculate translation so scaling happens around center
# ---------------------------------------------------------

def compute_centered_translation(
    center,
    matrix,
):
    """
    Calculate translation required to keep the given
    center fixed while applying the scale matrix.
    """

    cx = center.X()
    cy = center.Y()
    cz = center.Z()

    new_x = (
        matrix.Value(1, 1) * cx
        + matrix.Value(1, 2) * cy
        + matrix.Value(1, 3) * cz
    )

    new_y = (
        matrix.Value(2, 1) * cx
        + matrix.Value(2, 2) * cy
        + matrix.Value(2, 3) * cz
    )

    new_z = (
        matrix.Value(3, 1) * cx
        + matrix.Value(3, 2) * cy
        + matrix.Value(3, 3) * cz
    )

    tx = cx - new_x
    ty = cy - new_y
    tz = cz - new_z

    return tx, ty, tz


# ---------------------------------------------------------
# Apply global transformation
# ---------------------------------------------------------

def apply_global_transform(
    solid,
    matrix,
    center,
):
    """
    Apply the same global transformation to a solid.

    The transformation is performed around the common
    assembly center.
    """

    tx, ty, tz = compute_centered_translation(
        center,
        matrix,
    )

    gtrsf = gp_GTrsf()

    gtrsf.SetVectorialPart(
        matrix
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

    if not transformer.IsDone():
        raise RuntimeError(
            "Global geometric transformation failed."
        )

    return transformer.Shape()


# ---------------------------------------------------------
# Scale complete assembly
# ---------------------------------------------------------

def scale_assembly(
    solids,
    center,
    length_factor,
    width_factor,
    height_factor,
):
    """
    Scale the complete assembly using ONE global
    anisotropic transformation.

    Every body receives exactly the same transformation.
    """

    matrix = build_global_scale_matrix(
        length_factor,
        width_factor,
        height_factor,
    )

    processed_solids = []

    for index, solid in enumerate(solids):

        print(
            f"Scaling body {index + 1}/{len(solids)}..."
        )

        scaled = apply_global_transform(
            solid=solid,
            matrix=matrix,
            center=center,
        )

        processed_solids.append(
            scaled
        )

    return processed_solids