# Generated by Django 2.0.5 on 2022-11-13 19:46

import app_core.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('profession', models.CharField(blank=True, max_length=255, verbose_name='Profession')),
                ('code', models.CharField(blank=True, max_length=255, null=True, verbose_name="Parent's Code")),
            ],
            options={
                'verbose_name': 'Parent',
                'verbose_name_plural': 'Parents',
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
            bases=('app_core.user',),
            managers=[
                ('objects', app_core.models.UserManager()),
            ],
        ),
    ]
