from django.contrib import admin

from feature_toggles.models import FeatureToggle


@admin.register(FeatureToggle)
class FeatureToggleAdmin(admin.ModelAdmin):
    ...
