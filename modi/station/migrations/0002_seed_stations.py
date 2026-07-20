import csv
import os
from django.db import migrations


EXCLUDED_LINES = {'9호선(연장)'}


def normalize_line(line_name):
    return line_name.replace('수도권 광역급행철도', 'GTX')


def seed_stations(apps, schema_editor):
    Station = apps.get_model('station', 'Station')
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'stations.csv')

    with open(csv_path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            line_raw = row['호선명칭'].strip()

            # 9호선(연장) 제외
            if line_raw in EXCLUDED_LINES:
                continue

            line = normalize_line(line_raw)

            Station.objects.get_or_create(
                name=row['역한글명칭'],
                line=line,
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