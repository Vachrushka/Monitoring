# Generated by Django 5.0.1 on 2024-02-11 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_grading_rate_delete_cadetprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaderdata',
            name='old_rate',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='leaderdata',
            name='rate',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='exercisestandard',
            name='koef_up_great',
            field=models.FloatField(default=0.01),
        )
    ]
