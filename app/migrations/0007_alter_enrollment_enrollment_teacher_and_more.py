# Generated by Django 5.1 on 2024-09-25 06:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_enrollment_enrollment_teacher_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='enrollment_teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.employee'),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='intended_course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.course'),
        ),
    ]
