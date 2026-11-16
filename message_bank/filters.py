from django.utils import timezone

import django_filters

from message_bank.models import Message


class MessagesFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(field_name="type", lookup_expr="icontains")
    current = django_filters.BooleanFilter(method="filter_current")

    class Meta:
        model = Message
        fields = ["type"]

    def filter_current(self, queryset, name, value):
        if value is True:
            return queryset.filter(expirydate__gte=timezone.localdate())

        return queryset
