def update_total_score(sender, instance, **kwargs):
    instance.total_score = instance.calculate_total_score()
