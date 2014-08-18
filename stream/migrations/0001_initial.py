# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='timestamp')),
                ('verb', models.CharField(verbose_name='verb', max_length=200)),
                ('join', models.CharField(null=True, verbose_name='join', max_length=50, blank=True)),
                ('target_object_id', models.CharField(null=True, max_length=200, blank=True)),
                ('action_object_object_id', models.CharField(null=True, max_length=200, blank=True)),
                ('action_object_content_type', models.ForeignKey(to='contenttypes.ContentType', null=True, blank=True)),
                ('target_content_type', models.ForeignKey(to='contenttypes.ContentType', null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'ordering': ['-timestamp'],
                'verbose_name_plural': 'actions',
                'verbose_name': 'action',
            },
            bases=(models.Model,),
        ),
    ]
