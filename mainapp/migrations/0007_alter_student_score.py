# Generated by Django 5.1.7 on 2025-03-11 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0006_testresult_dominant_trait'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='score',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
