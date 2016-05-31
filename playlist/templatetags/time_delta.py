from django import template
from datetime import timedelta

register = template.Library()


def time_delta(value):
    if isinstance(value, timedelta):
        seconds = value.total_seconds()

        hours = int(seconds // (60 * 60))
        minutes = int((seconds - hours * 60 * 60) // 60)
        second = int(seconds % 60)
        if hours > 0:
            return '{:01d}:{:02d}:{:02d}'.format(hours, minutes, second)

        return '{:01d}:{:02d}'.format(minutes, second)
    else:
        return '0:00'


register.filter('time_delta', time_delta)
