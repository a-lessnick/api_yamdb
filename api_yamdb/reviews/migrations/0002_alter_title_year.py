# Generated by Django 3.2 on 2024-09-10 17:34

from django.db import migrations, models
import reviews.validators


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.SmallIntegerField(db_index=True, validators=[reviews.validators.validate_year], verbose_name='Год выпуска'),
        ),
    ]
