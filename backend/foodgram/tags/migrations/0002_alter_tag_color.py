# Generated by Django 3.2.3 on 2023-09-22 19:17

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#778899', image_field=None, max_length=25, samples=None, unique=True),
        ),
    ]
