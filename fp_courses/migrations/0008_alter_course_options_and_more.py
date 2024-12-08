# Generated by Django 4.2.7 on 2024-11-26 01:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fp_courses', '0007_course_course_seq_alter_cohort_effective_to_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['disp_seq', 'course_code', 'version']},
        ),
        migrations.RenameField(
            model_name='course',
            old_name='course_seq',
            new_name='disp_seq',
        ),
        migrations.AlterField(
            model_name='cohort',
            name='effective_to',
            field=models.DateTimeField(default=datetime.datetime(2025, 11, 26, 1, 3, 26, 525566)),
        ),
        migrations.AlterField(
            model_name='course',
            name='effective_to',
            field=models.DateTimeField(default=datetime.datetime(2034, 11, 26, 1, 3, 26, 524525)),
        ),
    ]
