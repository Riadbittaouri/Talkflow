# Generated by Django 5.1.7 on 2025-03-08 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0004_testresult"),
    ]

    operations = [
        migrations.AddField(
            model_name="classroom",
            name="group_size",
            field=models.PositiveIntegerField(blank=True, default=4, null=True),
        ),
    ]
