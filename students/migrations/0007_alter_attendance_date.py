# Generated by Django 5.2.3 on 2025-06-28 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0006_student_address_student_dob_student_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='date',
            field=models.DateField(),
        ),
    ]
