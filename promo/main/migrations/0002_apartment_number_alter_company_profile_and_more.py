# Generated by Django 4.1.5 on 2023-01-08 07:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='apartment',
            name='number',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='company',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.profile'),
        ),
        migrations.AlterField(
            model_name='gate',
            name='house',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.house'),
        ),
        migrations.AlterField(
            model_name='house',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.company'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]