import time
import math

DATE_FORMAT = "%Y.%m.%d %H:%M:%S"


def str_to_time(time_str, format_str=DATE_FORMAT):
    """Interprets time_str as a time value specified by format_str and
    returns that time object"""
    return time.mktime(time.strptime(time_str, format_str))


def compute_penalty(upload_time, deadline, penalty,
                    holiday_start=None, holiday_finish=None):
    """A generic function to compute penalty
    Args:
        penalty - for every day after the deadline the penalty
                  is added to the penalty_points variable
    Returns:
        Number of penalty points.
    Note: time interval between deadline and upload time (seconds)
    is time.mktime(upload_time) - time.mktime(deadline)
    """
    if holiday_start is None:
        holiday_start = []

    if holiday_finish is None:
        holiday_finish = []

    # XXX refactor such that instead of holiday_start and holiday_finish
    # only one list (of intervals) is used

    sec_upload_time = str_to_time(upload_time)
    sec_deadline = str_to_time(deadline)
    interval = sec_upload_time - sec_deadline
    penalty_points = 0

    if interval > 0:
        # compute the interval representing the intersection between
        # (deadline, upload_time) and (holiday_start[i], holiday_finish[i])

        if holiday_start != []:
            for i in range(len(holiday_start)):
                sec_start = str_to_time(holiday_start[i])
                sec_finish = str_to_time(holiday_finish[i])
                maxim = max(sec_start, sec_deadline)
                minim = min(sec_finish, sec_upload_time)
                if minim > maxim:
                    interval -= (minim - maxim)

    # only if the number of days late is positive (deadline exceeded)
    if interval > 0:
        days_late = int(math.ceil(interval / (3600 * 24)))

        for i in range(min(days_late, len(penalty))):
            penalty_points += penalty[i]
    else:
        days_late = 0

    return penalty_points
