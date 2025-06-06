# Generated by Django 5.2 on 2025-05-13 10:29

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('park', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Amenity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('icon', models.CharField(blank=True, max_length=30, null=True)),
                ('number', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VehicleType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Vehicle Type',
                'verbose_name_plural': 'Vehicle Types',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('model', models.CharField(max_length=50)),
                ('year', models.PositiveIntegerField()),
                ('color', models.CharField(blank=True, max_length=30, null=True)),
                ('license_plate', models.CharField(max_length=15, unique=True)),
                ('vin', models.CharField(max_length=17, unique=True)),
                ('total_seats', models.PositiveIntegerField(blank=True, default=1, null=True)),
                ('seats', models.PositiveIntegerField(blank=True, default=1)),
                ('status', models.CharField(choices=[('available', 'Available'), ('in_service', 'In Service'), ('maintenance', 'Under Maintenance'), ('out_of_service', 'Out of Service')], default='available', max_length=20)),
                ('is_departed', models.BooleanField(default=False)),
                ('departure_time', models.DateTimeField(blank=True, null=True)),
                ('is_arrived', models.BooleanField(default=False)),
                ('arrival_time', models.DateTimeField(blank=True, null=True)),
                ('is_available', models.BooleanField(default=True)),
                ('is_booked', models.BooleanField(default=False)),
                ('has_entourage_option', models.BooleanField(default=False)),
                ('has_security_option', models.BooleanField(default=False)),
                ('fuel_type', models.CharField(blank=True, max_length=20)),
                ('fuel_efficiency', models.FloatField(blank=True, null=True)),
                ('trip_amount', models.FloatField(blank=True, null=True)),
                ('trip_count', models.PositiveIntegerField(default=0)),
                ('amenities', models.ManyToManyField(to='vehicle.amenity')),
                ('arrival_park', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='to_park', to='park.park')),
                ('departure_park', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='from_park', to='park.park')),
                ('park_location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='vehicles', to='park.park')),
                ('category', models.ManyToManyField(to='vehicle.vehicletype')),
            ],
            options={
                'verbose_name': 'Vehicle',
                'verbose_name_plural': 'Vehicles',
            },
        ),
        migrations.CreateModel(
            name='VehicleImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='vehicle_images/')),
                ('caption', models.CharField(blank=True, max_length=200, null=True)),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='vehicle.vehicle')),
            ],
        ),
    ]
