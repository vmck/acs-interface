# Generated by Django 2.2.6 on 2019-11-04 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0009_auto_20191104_1433'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assignment',
            old_name='deadline',
            new_name='deadline_soft',
        ),
        migrations.AddField(
            model_name='assignment',
            name='deadline_hard',
            field=models.DateTimeField(null=True),
        ),
    ]
