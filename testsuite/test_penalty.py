from interface import penalty

DAILY_PENALTIES = [1, 1, 1, 1, 1, 1, 1]


def test_no_holiday():
    # No late penaly
    penalty_score = penalty.compute_penalty(
        "2019.12.04 10:00:00",
        "2019.12.05 23:55:00",
        DAILY_PENALTIES,
    )
    assert penalty_score == 0

    # random date between soft and hard deadline
    penalty_score = penalty.compute_penalty(
        "2019.12.10 10:00:00",
        "2019.12.05 23:55:00",
        DAILY_PENALTIES,
    )
    assert penalty_score == 5

    # soft deadline
    penalty_score = penalty.compute_penalty(
        "2019.12.05 23:55:01",
        "2019.12.05 23:55:00",
        DAILY_PENALTIES,
    )
    assert penalty_score == 1

    # over the number of days of penalyt
    penalty_score = penalty.compute_penalty(
        "2019.12.15 10:55:01",
        "2019.12.05 23:55:00",
        DAILY_PENALTIES,
    )
    assert penalty_score == 7

    # hard deadline
    penalty_score = penalty.compute_penalty(
        "2019.12.12 10:00:00",
        "2019.12.05 23:55:00",
        DAILY_PENALTIES,
    )
    assert penalty_score == 7

    penalty_score = penalty.compute_penalty(
        "2019.12.10 23:55:00",
        "2019.12.05 23:55:00",
        DAILY_PENALTIES,
    )
    assert penalty_score == 5

    penalty_score = penalty.compute_penalty(
        "2019.12.10 23:55:01",
        "2019.12.05 23:55:00",
        DAILY_PENALTIES,
    )
    assert penalty_score == 6


def test_holiday_at_start():
    penalty_score = penalty.compute_penalty(
        "2019.12.10 10:00:00",
        "2019.12.05 23:55:00",
        DAILY_PENALTIES,
        ["2019.12.05 23:55:00"],
        ["2019.12.09 23:55:00"],
    )
    assert penalty_score == 1

    penalty_score = penalty.compute_penalty(
        "2019.12.10 10:00:00",
        "2019.12.05 23:55:00",
        DAILY_PENALTIES,
        ["2019.12.06 00:00:00"],
        ["2019.12.09 23:55:00"],
    )
    assert penalty_score == 1

    penalty_score = penalty.compute_penalty(
        "2019.12.10 10:00:00",
        "2019.12.05 23:55:00",
        DAILY_PENALTIES,
        ["2019.12.06 00:00:00"],
        ["2019.12.09 10:00:00"],
    )
    assert penalty_score == 2

    penalty_score = penalty.compute_penalty(
        "2019.12.10 10:00:00",
        "2019.12.05 23:55:00",
        DAILY_PENALTIES,
        ["2019.12.04 00:00:00"],
        ["2019.12.09 23:55:00"],
    )
    assert penalty_score == 1


def test_holiday_in_middle_or_end():
    penalty_score = penalty.compute_penalty(
        "2019.12.10 10:00:00",
        "2019.12.05 23:55:00",
        DAILY_PENALTIES,
        ["2019.12.07 00:00:00"],
        ["2019.12.09 00:00:00"],
    )
    assert penalty_score == 3

    penalty_score = penalty.compute_penalty(
        "2019.12.12 00:00:01",
        "2019.12.05 23:55:00",
        DAILY_PENALTIES,
        ["2019.12.11 00:00:00"],
        ["2019.12.12 00:00:00"],
    )
    assert penalty_score == 6


def test_holiday_multiple():
    penalty_score = penalty.compute_penalty(
        "2019.12.15 10:00:00",
        "2019.12.05 23:55:00",
        DAILY_PENALTIES,
        ["2019.12.07 00:00:00", "2019.12.11 00:00:00"],
        ["2019.12.09 00:00:00", "2019.12.13 00:00:00"],
    )
    assert penalty_score == 6
