# Generated by Django 5.1.7 on 2025-04-03 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0010_student_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='student',
            unique_together={('classroom', 'email')},
        ),
    ]
