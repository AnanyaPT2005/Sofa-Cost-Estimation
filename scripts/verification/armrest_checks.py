def check_armrest_logic(scaled_df):
    """
    Engineering validation for armrests.

    Checks:
    1. top + top(1) length == base length
    """

    top = scaled_df[
        scaled_df["body"] == "left_armrest_top"
    ].iloc[0]

    top2 = scaled_df[
        scaled_df["body"] == "left_armrest_top (1)"
    ].iloc[0]

    base = scaled_df[
        scaled_df["body"] == "left_armrest_base"
    ].iloc[0]

    # Support both renamed verification dataframe
    # and the normal scaled dataframe.

    length_col = (
        "scaled_L_mm"
        if "scaled_L_mm" in scaled_df.columns
        else "L_mm"
    )

    total_length = (
        top[length_col]
        + top2[length_col]
    )

    base_length = base[length_col]

    diff = abs(total_length - base_length)

    print(f"Top Length     : {total_length:.2f}")
    print(f"Base Length    : {base_length:.2f}")
    print(f"Difference     : {diff:.2f}")

    return diff < 5