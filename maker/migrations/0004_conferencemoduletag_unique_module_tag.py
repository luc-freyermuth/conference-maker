# Generated by Django 5.1 on 2024-09-05 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maker', '0003_tag_tagcategory_conferencemoduletag_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='conferencemoduletag',
            constraint=models.UniqueConstraint(fields=('conference_module', 'tag'), name='unique_module_tag'),
        ),
    ]
