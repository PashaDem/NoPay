# Generated by Django 5.1.1 on 2024-10-22 12:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("advertisement", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="payout",
            name="balance",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="advertisement.balance",
                verbose_name="Баланс",
            ),
            preserve_default=False,
        ),
    ]