from django.core.cache import cache
from django.db import models


class FeatureToggle(models.Model):
    FEATURE_TOGGLE_CACHE_TIMEOUT = 300

    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __bool__(self):
        is_active = cache.get(self.name)
        if is_active is not None:
            return is_active

        toggle, _ = FeatureToggle.objects.get_or_create(name=self.name)
        cache.set(
            self.name, toggle.is_active, timeout=self.FEATURE_TOGGLE_CACHE_TIMEOUT
        )
        return toggle.is_active

    def __str__(self):
        return f"{self.name} Id: ({self.id})"

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        super().save(
            *args, force_insert=force_insert, force_update=force_update, using=using
        )
        cache.set(self.name, self.is_active, timeout=self.FEATURE_TOGGLE_CACHE_TIMEOUT)


class FeatureToggles:
    restrict_old_qrcodes: str = FeatureToggle(name="restrict_old_qrcodes")
