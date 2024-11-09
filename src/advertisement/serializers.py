from rest_framework import serializers

from advertisement.models import Balance


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ("user_id", "total")
