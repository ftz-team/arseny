# Generated by Django 3.2.8 on 2021-10-07 01:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20211007_0128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='city_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='custom_position',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='is_male',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='link',
            field=models.URLField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='offer_education',
            field=models.CharField(blank=True, default='', max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='offer_experience_year_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='operating_schedule',
            field=models.CharField(blank=True, default='', max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='predicted_tag',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.tag'),
        ),
        migrations.AlterField(
            model_name='position',
            name='salary_from',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='salary_to',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
