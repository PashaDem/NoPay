# Generated by Django 5.1.1 on 2024-11-10 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("qrcode_app", "0003_qrcodeprocessingstatus"),
    ]

    operations = [
        migrations.AddField(
            model_name="qrcodeprocessingstatus",
            name="was_seen_by_user",
            field=models.BooleanField(
                default=False, verbose_name="Видел ли пользователь это уведомление?"
            ),
        ),
    ]