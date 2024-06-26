# Generated by Django 5.0.1 on 2024-02-08 05:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_alter_departament_options_and_more'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exercisestandard',
            old_name='koef_down_fine',
            new_name='koef_down_great',
        ),
        migrations.RenameField(
            model_name='exercisestandard',
            old_name='koef_up_fine',
            new_name='koef_up_great',
        ),
        migrations.RemoveField(
            model_name='exercisestandard',
            name='value',
        ),
        migrations.CreateModel(
            name='LeaderData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('position_delta', models.IntegerField(default=0)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        )
    ]
