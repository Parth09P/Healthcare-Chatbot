# Generated by Django 5.1.1 on 2024-09-21 22:29

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare_bot', '0002_chatmessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConversationSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary', models.TextField()),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='healthcare_bot.patient')),
            ],
        ),
    ]
