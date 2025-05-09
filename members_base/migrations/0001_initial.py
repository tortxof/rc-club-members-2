# Generated by Django 5.1.6 on 2025-02-19 18:13

import django.db.models.deletion
import members_base.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipClass',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Membership classes',
            },
        ),
        migrations.CreateModel(
            name='Office',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(blank=True, max_length=255)),
                ('ama_number', models.CharField(blank=True, max_length=255)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(blank=True, max_length=255)),
                ('state', models.CharField(blank=True, max_length=255)),
                ('zip_code', models.CharField(blank=True, max_length=255)),
                ('expiration_date', models.DateField(default=members_base.models.get_default_expiration_date)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('membership_class', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='membership_class', to='members_base.membershipclass')),
                ('offices', models.ManyToManyField(blank=True, to='members_base.office')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('phone_number', models.CharField(max_length=255)),
                ('is_primary', models.BooleanField(default=False)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members_base.member')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
