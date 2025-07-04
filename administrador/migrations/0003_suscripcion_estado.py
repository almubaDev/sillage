# Generated by Django 5.2 on 2025-05-07 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("administrador", "0002_suscripcion_flow_customer_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="suscripcion",
            name="estado",
            field=models.CharField(
                choices=[
                    ("pendiente", "Pendiente"),
                    ("activa", "Activa"),
                    ("cancelada", "Cancelada"),
                    ("expirada", "Expirada"),
                ],
                default="pendiente",
                help_text="Estado general del ciclo de suscripción",
                max_length=10,
            ),
        ),
    ]
