import time
import math
import configparser
import decimal
import re
import logging

DATE_FORMAT = "%Y.%m.%d %H:%M:%S"

log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def str_to_time(time_str, format_str=DATE_FORMAT):
    """Interprets time_str as a time value specified by format_str and
    returns that time object"""
    return time.mktime(time.strptime(time_str, format_str))


def get_penalty_info(submission):
    config_data = submission.get_config_ini()

    config = configparser.ConfigParser()
    config.read_string(config_data.text)

    penalty_info = dict(config['PENALTY'])

    penalty = [int(x) for x in penalty_info['penaltyweights'].split(',')]
    holiday_s = [x for x in penalty_info.get('holidaystart', '').split(',')]
    holiday_f = [x for x in penalty_info.get('holidayfinish', '').split(',')]

    return (penalty, holiday_s, holiday_f)


def compute_penalty(upload_time, deadline, penalty,
                    holiday_start=[''], holiday_finish=['']):
    """A generic function to compute penalty
    Args:
        penalty - for every day after the deadline the penalty
                  is added to the penalty_points variable
    Returns:
        Number of penalty points.
    Note: time interval between deadline and upload time (seconds)
    is time.mktime(upload_time) - time.mktime(deadline)
    """
    if holiday_start[0] == '':
        holiday_start = []

    if holiday_finish[0] == '':
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


def compute_review_score(submission):
    marks = re.findall(
        r'^([+-]\d+\.*\d*):',
        submission.review_message,
        re.MULTILINE,
    )
    log.debug('Marks found: ' + str(marks))

    return sum([decimal.Decimal(mark) for mark in marks])


def calculate_total_score(submission):
    score = submission.score if submission.score else 0
    submission.review_score = compute_review_score(submission)
    if submission.penalty is None:
        submission.penalty = submission.compute_penalty()
    penalty = submission.penalty

    total_score = score + submission.review_score - penalty

    return total_score if total_score >= 0 else 0
