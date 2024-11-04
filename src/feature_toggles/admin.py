from django.contrib import admin

from .models import FeatureToggle


@admin.register(FeatureToggle)
class FeatureToggleAdmin(admin.ModelAdmin):
    ...
