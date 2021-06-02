from interface.scoring import calculate_total_score


def update_total_score(sender, instance, **kwargs):
    instance.total_score = calculate_total_score(instance)
