# Generated by Django 5.0.1 on 2024-02-19 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_remove_leaderdata_old_rate_delete_cadetprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='cadet',
            name='photo',
            field=models.ImageField(blank=True, default='img/author.jpg', null=True, upload_to='profile_pics/', verbose_name='Фотография'),
        ),
        migrations.DeleteModel(
            name='CadetProfile',
        ),
    ]
