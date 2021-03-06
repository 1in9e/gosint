# Generated by Django 3.2.4 on 2021-12-26 16:48

import datetime
from django.db import migrations, models
import django.db.models.deletion
import simplepro.components.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', simplepro.components.fields.CharField(blank=True, max_length=50, null=True, verbose_name='项目名称')),
                ('project_description', simplepro.components.fields.CharField(max_length=500, verbose_name='项目描述')),
                ('create_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(null=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '项目',
                'verbose_name_plural': '项目',
            },
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_type', simplepro.components.fields.CharField(choices=[('domain', '域名'), ('ip', 'ip资产')], default='domain', max_length=50, verbose_name='资产类型')),
                ('target_name', models.TextField(blank=True, null=True, unique=True, verbose_name='资产内容')),
                ('target_description', simplepro.components.fields.CharField(blank=True, default='', max_length=500, null=True, verbose_name='描述')),
                ('target_icp', models.CharField(blank=True, default='', max_length=300, null=True, verbose_name='域名备案')),
                ('last_scan_time', models.DateTimeField(null=True, verbose_name='上次扫描时间')),
                ('create_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(null=True, verbose_name='更新时间')),
                ('project', simplepro.components.fields.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='targetApp.project', verbose_name='工程名')),
            ],
            options={
                'verbose_name': '资产信息',
                'verbose_name_plural': '资产信息',
            },
        ),
    ]
