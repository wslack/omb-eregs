# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-27 21:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reqs', '0008_auto_20170127_0039'),
    ]

    operations = [
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('policy_number', models.IntegerField(unique=True)),
                ('title', models.CharField(max_length=1024)),
                ('uri', models.CharField(max_length=256)),
                ('omb_policy_id', models.CharField(blank=True, max_length=16)),
                ('policy_type', models.CharField(choices=[('memorandum', 'Memorandum'), ('circular', 'Circular'), ('strategy', 'Strategy'), ('review', 'Policy Review')], max_length=32)),
                ('issuance', models.DateField()),
                ('sunset', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='requirement',
            name='policy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reqs.Policy'),
        ),
    ]
