from collections.abc import Callable
from functools import wraps

from django.db.models import QuerySet


def order_by_payment_datetime(get_queryset: Callable) -> Callable:
    """Return queryset filtered by payment date and time in descending order or None."""

    @wraps(get_queryset)
    def inner(self) -> QuerySet | None:
        qs = get_queryset(self)
        if qs is None:
            return
        return qs.order_by("-payment_date", "-payment_time")

    return inner
