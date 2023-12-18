# Generated by Django 3.2.16 on 2023-12-18 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_post_comment_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='comment_count',
            field=models.PositiveIntegerField(blank=True, default=0, verbose_name='Количество комментариев'),
        ),
    ]