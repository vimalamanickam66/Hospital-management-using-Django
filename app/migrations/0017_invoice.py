# Generated by Django 5.1.5 on 2025-04-06 16:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_rename_created_at_billing_invoice_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icd10_code', models.CharField(max_length=20)),
                ('cpt_code', models.CharField(max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('paid', 'Paid'), ('unpaid', 'Unpaid'), ('pending', 'Pending')], default='pending', max_length=10)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='app.patient')),
            ],
        ),
    ]
