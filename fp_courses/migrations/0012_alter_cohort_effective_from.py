# Generated by Django 4.2.7 on 2024-11-26 16:31

from django.db import migrations, models
import fp_courses.models


class Migration(migrations.Migration):

    dependencies = [
        ('fp_courses', '0011_quiz'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cohort',
            name='effective_from',
            field=models.DateField(default=fp_courses.models.today_date),
        ),
    ]
