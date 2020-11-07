from typing import Union, Callable

from django.utils import timezone

from interface.models import ActionLog, User, Course, Assignment, Submission


def log_action(
    msg: str, usr: User, obj: Union[Course, Assignment, Submission]
):
    ActionLog.objects.create(
        timestamp=timezone.now(),
        user=usr,
        action=msg,
        content_object=obj,
    )


def log_action_admin(msg: str):
    def inner(func: Callable[any, any]):
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)

            request = args[1]
            queryset = args[2]

            for item in queryset:
                ActionLog.objects.create(
                    timestamp=timezone.now(),
                    user=request.user,
                    action=msg,
                    content_object=item,
                )

            return res

        return wrapper

    return inner
