# Generated by Django 4.2.1 on 2023-12-08 22:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Consultation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(null=True)),
                ('SYMP_PAT', models.TextField(null=True)),
                ('ANTECEDENTS_PAT', models.TextField(max_length=255, null=True)),
                ('TEMP', models.CharField(max_length=10, null=True)),
                ('FC', models.CharField(max_length=10, null=True)),
                ('PA', models.CharField(max_length=15, null=True)),
                ('ALLERGIES', models.TextField(null=True)),
                ('HANDICAP', models.TextField(null=True)),
                ('POIDS', models.CharField(max_length=10, null=True)),
                ('date_precribed', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmacy.patients')),
            ],
        ),
        migrations.CreateModel(
            name='Ordonance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('NUM_ORD', models.CharField(max_length=255, null=True)),
                ('DATE_ORD', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('consultation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pharmacy.consultation')),
            ],
        ),
    ]
