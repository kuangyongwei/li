# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-22 07:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sm_order', '0002_auto_20180818_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='ordermoney',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='订单金额'),
        ),
    ]
