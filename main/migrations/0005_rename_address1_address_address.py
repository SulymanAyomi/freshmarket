# Generated by Django 4.0.4 on 2022-04-18 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_product_rating'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='address1',
            new_name='address',
        ),
    ]
