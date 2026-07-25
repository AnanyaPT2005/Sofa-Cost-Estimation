TOL = 0.02


def check_seat_logic(scaled_df):
    """
    Engineering validation for seats.

    Checks:
    1. seat_top length == seat_front length
    2. seat_top depth > seat_front depth
    3. seat_front height > seat_top height
    """

    top = scaled_df[
        scaled_df["body"] == "seat_top"
    ].iloc[0]

    front = scaled_df[
        scaled_df["body"] == "seat_front"
    ].iloc[0]

    # Support both verification dataframe
    # and normal scaled dataframe.

    length_col = (
        "scaled_L_mm"
        if "scaled_L_mm" in scaled_df.columns
        else "L_mm"
    )

    depth_col = (
        "scaled_W_mm"
        if "scaled_W_mm" in scaled_df.columns
        else "W_mm"
    )

    height_col = (
        "scaled_H_mm"
        if "scaled_H_mm" in scaled_df.columns
        else "H_mm"
    )

    passed = True

    # --------------------------------------------------
    # Length
    # --------------------------------------------------

    length_diff = abs(
        top[length_col] - front[length_col]
    )

    print(f"Top Length     : {top[length_col]:.2f}")
    print(f"Front Length   : {front[length_col]:.2f}")
    print(f"Difference     : {length_diff:.2f}")

    if length_diff <= TOL:
        print("Length Check   : PASS")
    else:
        print("Length Check   : FAIL")
        passed = False

    # --------------------------------------------------
    # Depth
    # --------------------------------------------------

    print(f"\nTop Depth      : {top[depth_col]:.2f}")
    print(f"Front Depth    : {front[depth_col]:.2f}")

    if top[depth_col] > front[depth_col]:
        print("Depth Check    : PASS")
    else:
        print("Depth Check    : FAIL")
        passed = False

    # --------------------------------------------------
    # Height
    # --------------------------------------------------

    print(f"\nTop Height     : {top[height_col]:.2f}")
    print(f"Front Height   : {front[height_col]:.2f}")

    if front[height_col] > top[height_col]:
        print("Height Check   : PASS")
    else:
        print("Height Check   : FAIL")
        passed = False

    return passed