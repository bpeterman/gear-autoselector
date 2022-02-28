# Generated by Django 4.0.2 on 2022-02-28 01:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('selector', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='activity_id',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='auth',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='selector.user'),
        ),
        migrations.AlterField(
            model_name='gear',
            name='gear_id',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]