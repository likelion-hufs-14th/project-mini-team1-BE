import csv
import os
from django.db import migrations


def seed_stations(apps, schema_editor):
    Station = apps.get_model('station', 'Station')
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'stations.csv')

    with open(csv_path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            Station.objects.get_or_create(
                name=row['역한글명칭'],
                line=row['호선명칭'],
                defaults={
                    'latitude': row['환승역Y좌표'],
                    'longitude': row['환승역X좌표'],
                }
            )


def reverse_seed(apps, schema_editor):
    Station = apps.get_model('station', 'Station')
    Station.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('station', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_stations, reverse_seed),
    ]