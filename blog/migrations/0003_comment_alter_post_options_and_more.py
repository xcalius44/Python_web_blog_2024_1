# Generated by Django 5.1.1 on 2024-10-24 14:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_alter_post_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('email', models.EmailField(max_length=254)),
                ('body', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-publish']},
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['-publish'], name='blog_post_publish_bb7600_idx'),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='blog.post'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['created'], name='blog_commen_created_0e6ed4_idx'),
        ),
    ]