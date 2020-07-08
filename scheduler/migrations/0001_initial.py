# Generated by Django 3.0.8 on 2020-07-08 06:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('monitoring', '0003_auto_20200708_0645'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inspection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('FINISHED', 'FINISHED')], default='PENDING', max_length=16)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('finished_at', models.DateTimeField(default=None, null=True)),
                ('took', models.PositiveIntegerField(default=None, null=True)),
                ('endpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monitoring.Endpoint')),
            ],
        ),
        migrations.CreateModel(
            name='InspectionTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('SUCCEED', 'SUCCEED'), ('FAILED', 'FAILED')], default='PENDING', max_length=16)),
                ('error', models.TextField(default='')),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('finished_at', models.DateTimeField(default=None, null=True)),
                ('took', models.PositiveIntegerField(default=None, null=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monitoring.Agent')),
                ('inspection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.Inspection')),
            ],
        ),
        migrations.CreateModel(
            name='HTTPInspectionResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('successful_connection', models.BooleanField()),
                ('status_code', models.CharField(max_length=4)),
                ('dns_lookup_time', models.DecimalField(decimal_places=3, max_digits=6, null=True)),
                ('connect_time', models.DecimalField(decimal_places=3, max_digits=6, null=True)),
                ('response_time', models.DecimalField(decimal_places=3, max_digits=6, null=True)),
                ('byte_received', models.PositiveIntegerField(null=True)),
                ('inspection_task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='http_result', to='scheduler.InspectionTask')),
            ],
        ),
    ]