# Generated by Django 2.2.6 on 2019-10-25 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0006_auto_20191016_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='output',
            field=models.CharField(blank=True, default='', max_length=32768)
        ),
        migrations.RenameField(
            model_name='submission',
            old_name='output',
            new_name='stdout',
        ),
        migrations.AddField(
            model_name='submission',
            name='stderr',
            field=models.CharField(blank=True, default='', max_length=32768),
        ),
        migrations.AlterField(
            model_name='submission',
            name='review_message',
            field=models.CharField(blank=True, default='', max_length=4096),
        ),
    ]