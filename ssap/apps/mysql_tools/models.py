from django.db import models


# 项目
class MysqlProject(models.Model):
    name = models.CharField(max_length=100, verbose_name='项目名称')

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = verbose_name


# 上传文件表
class MysqlUploadFile(models.Model):
    project = models.ForeignKey(MysqlProject, verbose_name='项目', related_name="uploadfile_project",
                                on_delete=models.CASCADE)
    filename = models.CharField(max_length=100, verbose_name='服务器本地文件名')
    filesize = models.FloatField(verbose_name='上传文件大小', null=True, blank=True)
    handle_time = models.FloatField(verbose_name='处理耗时', null=True, blank=True)
    sql_status = models.PositiveSmallIntegerField(verbose_name='SQL处理状态', choices=((0, '失败'), (1, '处理中'), (2, '完成')),
                                                  default=1)
    table_status = models.PositiveSmallIntegerField(verbose_name='数据表处理状态', choices=((0, '失败'), (1, '处理中'), (2, '完成')),
                                                    default=1)

    class Meta:
        verbose_name = '上传文件'
        verbose_name_plural = verbose_name


# SQL 详情表
class MysqlSqlDetail(models.Model):
    filename = models.ForeignKey(MysqlUploadFile, verbose_name='文件名', related_name="detail_filename",
                                 on_delete=models.CASCADE)
    exec_time = models.DateTimeField(verbose_name='操作时间')
    exec_user = models.CharField(max_length=50, verbose_name='执行用户')
    exec_db = models.CharField(max_length=50, verbose_name='操作数据库')
    exec_use_time = models.FloatField(verbose_name='执行耗时')
    exec_rows_examined = models.IntegerField(verbose_name='扫描行数')
    exec_rows_sent = models.IntegerField(verbose_name='返回行数')
    exec_sql = models.TextField(verbose_name='SQL')

    class Meta:
        verbose_name = 'SQL详情'
        verbose_name_plural = verbose_name


# 数据表详情
class MysqlSqlTable(models.Model):
    filename = models.ForeignKey(MysqlUploadFile, verbose_name='文件名', related_name="table_filename",
                                 on_delete=models.CASCADE)
    table_name = models.CharField(max_length=50, verbose_name='表名')
    select_times = models.IntegerField(verbose_name='查询次数')

    class Meta:
        verbose_name = '数据表详情'
        verbose_name_plural = verbose_name
