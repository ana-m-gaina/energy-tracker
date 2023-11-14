# Generated by Django 4.1.4 on 2023-03-10 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GeodataJudet',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=125)),
                ('abreviere', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'geodata_geodajudet',
            },
        ),
        migrations.CreateModel(
            name='GeodataLocalitate',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=125)),
                ('latitude', models.CharField(blank=True, max_length=7, null=True)),
                ('longitude', models.CharField(blank=True, max_length=7, null=True)),
                ('judet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='geodata.geodatajudet')),
            ],
            options={
                'db_table': 'geodata_geodalocalitate',
            },
        ),
        migrations.CreateModel(
            name='GeodataTara',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('surogate', models.CharField(max_length=150)),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'db_table': 'geodata_geodatatara',
            },
        ),
        migrations.CreateModel(
            name='GeodataStrada',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=125)),
                ('judet', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='geodata.geodatajudet')),
                ('localitate', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='geodata.geodatalocalitate')),
                ('tara', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='geodata.geodatatara')),
            ],
        ),
        migrations.AddField(
            model_name='geodatalocalitate',
            name='tara',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='geodata.geodatatara'),
        ),
        migrations.AddField(
            model_name='geodatajudet',
            name='tara',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='geodata.geodatatara'),
        ),
    ]