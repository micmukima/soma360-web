# Generated by Django 2.0.5 on 2022-11-13 19:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('parent', '0001_initial'),
        ('school', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=255, verbose_name='First Name')),
                ('middlename', models.CharField(max_length=255, verbose_name='Middle Name')),
                ('lastname', models.CharField(max_length=255, verbose_name='Last Name')),
                ('address', models.TextField(max_length=255, verbose_name='Address')),
                ('registration_number', models.CharField(blank=True, max_length=255, verbose_name='Registration Number')),
                ('date_registered', models.DateTimeField(default=django.utils.timezone.now)),
                ('photo', sorl.thumbnail.fields.ImageField(blank=True, default=None, upload_to='images/student_photos/%Y/%m')),
                ('current_academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='school.AcademicYear')),
                ('current_class', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parent_1', to='school.Class')),
                ('current_section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='parent_1', to='school.Section')),
                ('parent_1', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parent_1', to='parent.Parent')),
                ('parent_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='parent_2', to='parent.Parent')),
                ('school', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='school.School')),
            ],
            options={
                'verbose_name': 'Student',
                'verbose_name_plural': 'Students',
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
        ),
        migrations.CreateModel(
            name='StudentPromotion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_promoted', models.DateTimeField(default=django.utils.timezone.now)),
                ('from_academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_academic_year', to='school.AcademicYear')),
                ('from_class', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='from_class', to='school.Class')),
                ('from_section', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='from_section', to='school.Section')),
                ('promoted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='student.Student')),
                ('to_academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_academic_year', to='school.AcademicYear')),
                ('to_class', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='to_class', to='school.Class')),
                ('to_section', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='to_section', to='school.Section')),
            ],
            options={
                'verbose_name': 'Student Promotion',
                'verbose_name_plural': 'Student Promotions',
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
        ),
        migrations.CreateModel(
            name='StudentBulkAdmit',
            fields=[
            ],
            options={
                'verbose_name': 'Student Bulk Admit',
                'verbose_name_plural': 'Student Bulk Admit',
                'proxy': True,
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'indexes': [],
            },
            bases=('student.student',),
        ),
    ]
