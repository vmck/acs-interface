import time
import math

from django.conf import settings


def str_to_time(time_str, format_str=settings.DATE_FORMAT):
    """Interprets time_str as a time value specified by format_str and
    returns that time object"""
    return time.mktime(time.strptime(time_str, format_str))


def compute_penalty(upload_time, deadline, penalty, weights, limit,
                    holiday_start=None, holiday_finish=None):
    """A generic function to compute penalty
    Args:
        penalty - for every day after the deadline the product
                  of the penalty and the weight is added to the
                  penalty_points variable
        weights - the penalty's weight per day (the last weight
                   from the list is used for subsequent computations)
        limit - the limit for the penalty value
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

    sec_upload_time = time.mktime(upload_time)
    sec_deadline = time.mktime(deadline)
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

        for i in range(days_late):
            # the penalty exceeded the limit
            if penalty_points > limit:
                break
            else:
                # for every day late the specific weight is used
                weight = weights[min(i, len(weights) - 1)]
                penalty_points += weight * penalty
    else:
        days_late = 0

    return (min(penalty_points, limit), days_late)
