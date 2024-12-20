# Generated by Django 5.1.3 on 2024-11-26 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='leave',
            name='reason',
            field=models.TextField(default='N/A'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='leave',
            name='is_approved',
            field=models.BooleanField(default=None),
        ),
    ]
