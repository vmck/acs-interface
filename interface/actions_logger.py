from django.utils import timezone
from django.shortcuts import get_object_or_404

from interface.models import ActionLog


def log_action(msg, usr, obj):
    ActionLog.objects.create(
        timestamp=timezone.now(),
        user=usr,
        action=msg,
        content_object=obj,
    )


def log_action_admin(msg):
    def inner(func):
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
