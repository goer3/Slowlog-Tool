# Generated by Django 2.1 on 2020-03-19 09:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MysqlSqlDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exec_time', models.DateTimeField(verbose_name='操作时间')),
                ('exec_user', models.CharField(max_length=50, verbose_name='执行用户')),
                ('exec_db', models.CharField(max_length=50, verbose_name='操作数据库')),
                ('exec_use_time', models.FloatField(verbose_name='执行耗时')),
                ('exec_rows_examined', models.IntegerField(verbose_name='扫描行数')),
                ('exec_rows_sent', models.IntegerField(verbose_name='返回行数')),
                ('exec_sql', models.TextField(verbose_name='SQL')),
            ],
            options={
                'verbose_name': 'SQL详情',
                'verbose_name_plural': 'SQL详情',
            },
        ),
        migrations.CreateModel(
            name='MysqlSqlTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_name', models.CharField(max_length=50, verbose_name='表名')),
                ('select_times', models.IntegerField(verbose_name='查询次数')),
            ],
            options={
                'verbose_name': '数据表详情',
                'verbose_name_plural': '数据表详情',
            },
        ),
        migrations.CreateModel(
            name='MysqlUploadFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=100, verbose_name='服务器本地文件名')),
                ('sql_status', models.PositiveSmallIntegerField(choices=[(0, '失败'), (1, '处理中'), (2, '完成')], default=1, verbose_name='SQL处理状态')),
                ('table_status', models.PositiveSmallIntegerField(choices=[(0, '失败'), (1, '处理中'), (2, '完成')], default=1, verbose_name='数据表处理状态')),
            ],
            options={
                'verbose_name': '上传文件',
                'verbose_name_plural': '上传文件',
            },
        ),
        migrations.AddField(
            model_name='mysqlsqltable',
            name='filename',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='table_filename', to='mysql_tools.MysqlUploadFile', verbose_name='文件名'),
        ),
        migrations.AddField(
            model_name='mysqlsqldetail',
            name='filename',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detail_filename', to='mysql_tools.MysqlUploadFile', verbose_name='文件名'),
        ),
    ]