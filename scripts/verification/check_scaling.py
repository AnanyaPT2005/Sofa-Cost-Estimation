import math

TOL = 0.02
def approx_equal(a, b, tol=TOL):
    return math.isclose(a, b, abs_tol=tol)

def check_scaling(
    original_df,
    scaled_df,
    sx,
    sy,
    sz,
    logical_check=None,
    title="SCALING VERIFICATION",
):

    print("\n")
    print("=" * 75)
    print(title)
    print("=" * 75)

    passed = True

    bodies = scaled_df["body"].tolist()

    for body in bodies:

        old = original_df[
            original_df["body"] == body
        ].iloc[0]

        new = scaled_df[
            scaled_df["body"] == body
        ].iloc[0]

        print(f"\n{body}")

        # ---------------------------------------------------
        # Length
        # ---------------------------------------------------

        expected = old["scaled_L_mm"] * sx if "scaled_L_mm" in old.index else old["L_mm"] * sx

        actual = (
            new["scaled_L_mm"]
            if "scaled_L_mm" in new.index
            else new["L_mm"]
        )

        ok = approx_equal(expected, actual)

        print(
            f"L : {expected:.2f} == {actual:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        # ---------------------------------------------------
        # Width
        # ---------------------------------------------------

        expected = old["scaled_W_mm"] * sy if "scaled_W_mm" in old.index else old["W_mm"] * sy

        actual = (
            new["scaled_W_mm"]
            if "scaled_W_mm" in new.index
            else new["W_mm"]
        )

        ok = approx_equal(expected, actual)

        print(
            f"W : {expected:.2f} == {actual:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        # ---------------------------------------------------
        # Height
        # ---------------------------------------------------

        expected = old["scaled_H_mm"] * sz if "scaled_H_mm" in old.index else old["H_mm"] * sz

        actual = (
            new["scaled_H_mm"]
            if "scaled_H_mm" in new.index
            else new["H_mm"]
        )

        ok = approx_equal(expected, actual)

        print(
            f"H : {expected:.2f} == {actual:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        # ---------------------------------------------------
        # Bounding X
        # ---------------------------------------------------

        min_x = (
            new["scaled_min_x_mm"]
            if "scaled_min_x_mm" in new.index
            else new["min_x_mm"]
        )

        max_x = (
            new["scaled_max_x_mm"]
            if "scaled_max_x_mm" in new.index
            else new["max_x_mm"]
        )

        L = max_x - min_x

        ok = approx_equal(L, actual)

        print(
            f"Bounding X : {L:.2f} == {actual:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        # ---------------------------------------------------
        # Bounding Y
        # ---------------------------------------------------

        actual = (
            new["scaled_W_mm"]
            if "scaled_W_mm" in new.index
            else new["W_mm"]
        )

        min_y = (
            new["scaled_min_y_mm"]
            if "scaled_min_y_mm" in new.index
            else new["min_y_mm"]
        )

        max_y = (
            new["scaled_max_y_mm"]
            if "scaled_max_y_mm" in new.index
            else new["max_y_mm"]
        )

        W = max_y - min_y

        ok = approx_equal(W, actual)

        print(
            f"Bounding Y : {W:.2f} == {actual:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        # ---------------------------------------------------
        # Bounding Z
        # ---------------------------------------------------

        actual = (
            new["scaled_H_mm"]
            if "scaled_H_mm" in new.index
            else new["H_mm"]
        )

        min_z = (
            new["scaled_min_z_mm"]
            if "scaled_min_z_mm" in new.index
            else new["min_z_mm"]
        )

        max_z = (
            new["scaled_max_z_mm"]
            if "scaled_max_z_mm" in new.index
            else new["max_z_mm"]
        )

        H = max_z - min_z

        ok = approx_equal(H, actual)

        print(
            f"Bounding Z : {H:.2f} == {actual:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        # ---------------------------------------------------
        # Centre X
        # ---------------------------------------------------

        center_x = (
            new["scaled_center_x_mm"]
            if "scaled_center_x_mm" in new.index
            else new["center_x_mm"]
        )

        cx = (min_x + max_x) / 2

        ok = approx_equal(cx, center_x)

        print(
            f"Center X : {cx:.2f} == {center_x:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        # ---------------------------------------------------
        # Centre Y
        # ---------------------------------------------------

        center_y = (
            new["scaled_center_y_mm"]
            if "scaled_center_y_mm" in new.index
            else new["center_y_mm"]
        )

        cy = (min_y + max_y) / 2

        ok = approx_equal(cy, center_y)

        print(
            f"Center Y : {cy:.2f} == {center_y:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        # ---------------------------------------------------
        # Centre Z
        # ---------------------------------------------------

        center_z = (
            new["scaled_center_z_mm"]
            if "scaled_center_z_mm" in new.index
            else new["center_z_mm"]
        )

        cz = (min_z + max_z) / 2

        ok = approx_equal(cz, center_z)

        print(
            f"Center Z : {cz:.2f} == {center_z:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

    # -------------------------------------------------------
    # Component-specific logical checks
    # -------------------------------------------------------

    if logical_check is not None:

        print("\n")
        print("=" * 75)
        print("LOGICAL CHECK")
        print("=" * 75)

        if logical_check(scaled_df):
            print("PASS")
        else:
            print("FAIL")
            passed = False

    print("\n")
    print("=" * 75)

    if passed:
        print("OVERALL RESULT : PASS")
    else:
        print("OVERALL RESULT : FAIL")

    print("=" * 75)

    return passed