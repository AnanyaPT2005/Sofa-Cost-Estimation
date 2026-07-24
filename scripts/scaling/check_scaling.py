import math


TOL = 0.02


def approx_equal(a, b, tol=TOL):
    return abs(a - b) <= tol


def check_scaling(original_df, scaled_df, sx, sy, sz):

    print("\n")
    print("=" * 75)
    print("SCALING VERIFICATION")
    print("=" * 75)

    passed = True

    bodies = scaled_df["body"].tolist()

    for body in bodies:

        old = original_df[original_df["body"] == body].iloc[0]
        new = scaled_df[scaled_df["body"] == body].iloc[0]

        print(f"\n{body}")

        # ---------------------------------------------------
        # Check 1
        # ---------------------------------------------------

        expected = old["L_mm"] * sx

        ok = approx_equal(expected, new["scaled_L_mm"])

        print(
            f"L : {expected:.2f} == {new['scaled_L_mm']:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        # ---------------------------------------------------

        expected = old["W_mm"] * sy

        ok = approx_equal(expected, new["scaled_W_mm"])

        print(
            f"W : {expected:.2f} == {new['scaled_W_mm']:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        # ---------------------------------------------------

        expected = old["H_mm"] * sz

        ok = approx_equal(expected, new["scaled_H_mm"])

        print(
            f"H : {expected:.2f} == {new['scaled_H_mm']:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        # ---------------------------------------------------
        # Bounding boxes
        # ---------------------------------------------------

        L = (
            new["scaled_max_x_mm"]
            - new["scaled_min_x_mm"]
        )

        ok = approx_equal(L, new["scaled_L_mm"])

        print(
            f"Bounding X : {L:.2f} == {new['scaled_L_mm']:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        # ---------------------------------------------------

        W = (
            new["scaled_max_y_mm"]
            - new["scaled_min_y_mm"]
        )

        ok = approx_equal(W, new["scaled_W_mm"])

        print(
            f"Bounding Y : {W:.2f} == {new['scaled_W_mm']:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        # ---------------------------------------------------

        H = (
            new["scaled_max_z_mm"]
            - new["scaled_min_z_mm"]
        )

        ok = approx_equal(H, new["scaled_H_mm"])

        print(
            f"Bounding Z : {H:.2f} == {new['scaled_H_mm']:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        # ---------------------------------------------------
        # Centres
        # ---------------------------------------------------

        cx = (
            new["scaled_min_x_mm"]
            + new["scaled_max_x_mm"]
        ) / 2

        ok = approx_equal(cx, new["scaled_center_x_mm"])

        print(
            f"Center X : {cx:.2f} == {new['scaled_center_x_mm']:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        cy = (
            new["scaled_min_y_mm"]
            + new["scaled_max_y_mm"]
        ) / 2

        ok = approx_equal(cy, new["scaled_center_y_mm"])

        print(
            f"Center Y : {cy:.2f} == {new['scaled_center_y_mm']:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

        cz = (
            new["scaled_min_z_mm"]
            + new["scaled_max_z_mm"]
        ) / 2

        ok = approx_equal(cz, new["scaled_center_z_mm"])

        print(
            f"Center Z : {cz:.2f} == {new['scaled_center_z_mm']:.2f} "
            f"{'PASS' if ok else 'FAIL'}"
        )

        passed &= ok

    # -------------------------------------------------------
    # Logical armrest check
    # -------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("LOGICAL ARMREST CHECK")
    print("=" * 75)

    top = scaled_df[
        scaled_df["body"] == "left_armrest_top"
    ].iloc[0]

    top2 = scaled_df[
        scaled_df["body"] == "left_armrest_top (1)"
    ].iloc[0]

    base = scaled_df[
        scaled_df["body"] == "left_armrest_base"
    ].iloc[0]

    total = (
        top["scaled_L_mm"]
        + top2["scaled_L_mm"]
    )

    diff = abs(total - base["scaled_L_mm"])

    print(f"Top Length     : {total:.2f}")
    print(f"Base Length    : {base['scaled_L_mm']:.2f}")
    print(f"Difference     : {diff:.2f}")

    if diff < 5:
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