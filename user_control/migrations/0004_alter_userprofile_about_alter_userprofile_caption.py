# Generated by Django 4.0.5 on 2022-06-16 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_control', '0003_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='about',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='caption',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
