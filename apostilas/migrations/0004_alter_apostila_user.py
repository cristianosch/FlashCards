# Generated by Django 4.2.9 on 2024-01-21 00:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('apostilas', '0003_alter_apostila_arquivo_alter_apostila_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apostila',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]
