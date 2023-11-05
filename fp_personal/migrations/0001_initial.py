# Generated by Django 3.2.22 on 2023-11-05 17:47

import cloudinary.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('fp_blog', '0005_alter_article_likes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('profile_image', cloudinary.models.CloudinaryField(default='placeholder', max_length=255, verbose_name='image')),
                ('birth_year', models.PositiveIntegerField()),
                ('age_approx', models.PositiveIntegerField()),
                ('age_exact', models.PositiveIntegerField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_action_seq', models.IntegerField(default=10)),
                ('action_desc', models.CharField(default='Action:  ', max_length=200)),
                ('action_taken', models.CharField(default='Taken:  ', max_length=200)),
                ('observation', models.CharField(default='Notes:  ', max_length=200)),
                ('completed', models.BooleanField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('completed_on', models.DateTimeField(auto_now_add=True)),
                ('parent_article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_personal_actions', to='fp_blog.article')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_actions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user', 'user_action_seq'],
            },
        ),
    ]