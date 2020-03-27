from django.shortcuts import render, HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.conf import settings
import time
import re
import os
from collections import Counter
from threading import Thread
from pure_pagination import PageNotAnInteger, Paginator, EmptyPage

# 用户定义
from . import models


# 首页
class IndexView(View):
    def get(self, request):
        context = {}
        return render(request, "index.html", context=context)


# 文件上传
class MysqlFileUploadView(View):
    def get(self, request):
        project_list = models.MysqlProject.objects.all()
        context = {
            'project_list': project_list,
        }
        return render(request, 'mysql_tools/upload-file.html', context=context)

    def post(self, request):
        # 数据库类型选择
        fileType = request.POST.get("fileType", None)
        project = request.POST.get("project", None)

        if fileType is None:
            return HttpResponse("上传数据库类型选择错误，类型不能为空，请检查!")
        if int(fileType) != 1:
            return HttpResponse("上传数据库类型选择错误，目前仅支持 MySQL，请检查!")

        # 接收文件
        uploadFile = request.FILES.get('uploadFile')

        # 获取文件大小
        fileSize = (uploadFile.size / 1024 / 1024)
        fileSize = float('%.2f' % fileSize)

        if uploadFile is None:
            return HttpResponse("上传文件发生错误，文件不能为空，请检查!")

        # 保存保存文件到服务器
        newFileName = "MySQLSlowLog-" + time.strftime("%Y%m%d-%H%M%S") + ".log"
        try:
            f = open(settings.UPLOAD_FILE_PATH + newFileName, 'wb')
            for data in uploadFile.chunks():
                f.write(data)
            f.close()
        except Exception as e:
            return HttpResponse("上传文件本地写入发生错误:" + e)

        # 保存文件名字到数据库
        uploadFile_obj = models.MysqlUploadFile()
        uploadFile_obj.project = models.MysqlProject.objects.get(id=int(project))
        uploadFile_obj.filename = newFileName
        uploadFile_obj.filesize = fileSize
        uploadFile_obj.save()

        # 异步处理
        th1 = Thread(target=MysqlUploadFileSQLHandle, args=(newFileName,), name='thread1')
        th1.start()

        return HttpResponseRedirect(reverse('mysql_tools:mysql_file_upload_list'))


# 文件 SQL 处理
def MysqlUploadFileSQLHandle(Filename):
    start_str = "# Time"
    data_str = ''
    start_str_flag = 0
    start_time = time.time()
    table_counter = Counter(list())
    print('------------------------------ 开始处理数据 ------------------------------ ')

    try:
        f = open(settings.UPLOAD_FILE_PATH + Filename, 'r')
        while True:
            # 逐行读取
            each_line = f.readline()

            # 判断是否读取完文件
            if not each_line:
                break

            '''
            如果分隔符出现在当前行并且这是第一次出现，不管之前有哪些数据都全部清除掉，只开始从当前行开始处理。因为前面即使有数据也不完整。
            '''
            if (start_str in each_line) and (start_str_flag == 0):
                data_str = each_line
                start_str_flag += 1
                continue

            '''
            如果改行不包含分隔符，则将本行数据和之前的数据进行拼接，并进入下一行。
            '''
            if (start_str not in each_line):
                data_str = data_str + each_line + ' '
                continue

            '''
            如果分隔符号出现在当前行，且不是第一次出现，则表示之前的数据已经是一条完整的数据，则开始对该数据进行处理。
            '''
            if (start_str in each_line) and (start_str_flag != 0):
                # 替换换行符等
                data_str = data_str.replace("\n", " ").replace("\t", " ")
                # 去掉首尾空格
                data_str = data_str.strip()
                # 逗号处理
                data_str = re.sub(' ,', ',', data_str)
                data_str = re.sub(',', ', ', data_str)
                # 替换多个空格为一个
                data_str = re.sub('\s+', ' ', data_str)
                '''
                开始进行数据处理
                '''
                # 执行时间
                re_exec_time = re.compile(r'# Time: ([0-9A-Z:\-]+)\.', re.I)
                exec_time = re_exec_time.findall(data_str)[0]
                exec_time = exec_time.replace('T', ' ')

                # 执行用户
                re_exec_user = re.compile(r'# User@Host:\s*([a-zA-Z0-9_]+)\[', re.I)
                exec_user = re_exec_user.findall(data_str)[0]

                # 操作数据库
                re_exec_db = re.compile(r'# Schema:\s*([a-zA-Z0-9_]+)\s*Last_errno', re.I)
                exec_db = re_exec_db.findall(data_str)[0]

                # 执行耗时
                re_exec_use_time = re.compile(r'# Query_time:\s*([0-9.]+)\s*Lock_time', re.I)
                exec_use_time = re_exec_use_time.findall(data_str)[0]

                # 发送数据行
                re_exec_rows_sent = re.compile(r'Rows_sent: (\d+)', re.I)
                exec_rows_sent = re_exec_rows_sent.findall(data_str)[0]

                # 扫描数据行
                re_exec_rows_examined = re.compile(r'Rows_examined: (\d+)', re.I)
                exec_rows_examined = re_exec_rows_examined.findall(data_str)[0]

                # SQL
                sql = re.split('SET timestamp=\d+;\s', data_str)[1]
                exec_sql = re.sub('\s+', ' ', sql)

                # 保存到数据库
                sqlDetail_obj = models.MysqlSqlDetail()
                sqlDetail_obj.filename = models.MysqlUploadFile.objects.get(filename=Filename)
                sqlDetail_obj.exec_user = exec_user
                sqlDetail_obj.exec_db = exec_db
                sqlDetail_obj.exec_time = exec_time
                sqlDetail_obj.exec_use_time = exec_use_time
                sqlDetail_obj.exec_rows_examined = exec_rows_examined
                sqlDetail_obj.exec_rows_sent = exec_rows_sent
                sqlDetail_obj.exec_sql = exec_sql
                sqlDetail_obj.save()

                '''
                通过 from 关键字查找后面跟的数据表，以此对查询的数据表进行统计。
                '''
                re_pattern = re.compile(r'FROM\s*([a-zA-Z0-9_]+)\s*', re.I)
                result = re_pattern.findall(data_str)
                # 统计查询次数
                table_times = Counter(result)
                table_counter = (table_counter + table_times)

                # 重新开始新一条数据
                data_str = each_line
                print(data_str)
        # 关闭文件
        f.close()

        # 保存表记录
        for table_name in dict(table_counter):
            table_obj = models.MysqlSqlTable()
            table_obj.filename = models.MysqlUploadFile.objects.get(filename=Filename)
            table_obj.table_name = table_name
            table_obj.select_times = table_counter[table_name]
            table_obj.save()

        # 处理时间
        stop_time = time.time()
        handle_time = (stop_time - start_time)
        handle_time = float('%.2f' % handle_time)

        # 修改处理状态
        uploadFile_obj = models.MysqlUploadFile.objects.get(filename=Filename)
        uploadFile_obj.sql_status = 2
        uploadFile_obj.table_status = 2
        uploadFile_obj.handle_time = handle_time
        uploadFile_obj.save()
        print('------------------------------ 数据处理完成 ------------------------------ ')
    except Exception as e:
        # 修改处理状态
        uploadFile_obj = models.MysqlUploadFile.objects.get(filename=Filename)
        uploadFile_obj.sql_status = 1
        uploadFile_obj.table_status = 1
        uploadFile_obj.save()
        print(e)


# 文件上传列表
class MysqlFileUploadListView(View):
    def get(self, request):
        uploadFile_list = models.MysqlUploadFile.objects.all().order_by('-filename')
        context = {
            'uploadFile_list': uploadFile_list,
        }
        return render(request, 'mysql_tools/upload-file-list.html', context=context)


# 删除记录
class MysqlDelUploadFileView(View):
    def get(self, request, file_id):
        if file_id.isalnum():
            # 清空数据
            if int(file_id) == 0:
                uploadFile_obj = models.MysqlUploadFile.objects.all()
                uploadFile_obj.delete()
                # 删除所有上传的文件
                for file in os.listdir(settings.UPLOAD_FILE_PATH):
                    if file.endswith('.log'):
                        os.remove(os.path.join(settings.UPLOAD_FILE_PATH, file))
            # 删除指定数据
            else:
                uploadFile_obj = models.MysqlUploadFile.objects.get(id=int(file_id))
                uploadFile_obj.delete()
                filePath = os.path.join(settings.UPLOAD_FILE_PATH, uploadFile_obj.filename)
                # 删除指定文件
                if os.path.isfile(filePath):
                    os.remove(filePath)
                else:
                    return HttpResponse("删除记录传递参数存在问题!")
        return HttpResponseRedirect(reverse('mysql_tools:mysql_file_upload_list'))


# SQL 详情页
class MySQLFileSqlDetailView(View):
    def get(self, request, file_id):
        # 系统信息
        sever_name = request.get_host()
        exec_user_value = ''
        exec_db_value = ''
        exec_use_time_value = ''
        sort_rule_value = ''

        print(1)
        # 查询数据
        if file_id.isalnum():
            print(2)
            # 文件
            sqlFile = models.MysqlUploadFile.objects.get(id=int(file_id))

            # 详情
            sqlDetail_list = models.MysqlSqlDetail.objects.filter(filename_id=int(file_id))

            # 生成筛选条件列表
            user_list = sqlDetail_list.values_list('exec_user', flat=True).distinct()
            db_list = sqlDetail_list.values_list('exec_db', flat=True).distinct()

            # 判断是否按照用户筛选
            if request.GET.get('exec_user'):
                exec_user_value = request.GET.get('exec_user')
                sqlDetail_list = sqlDetail_list.filter(exec_user=exec_user_value)

            # 判断是否按照数据库筛选
            if request.GET.get('exec_db'):
                exec_db_value = request.GET.get('exec_db')
                sqlDetail_list = sqlDetail_list.filter(exec_db=exec_db_value)

            # 判断是否按照时间筛选
            if request.GET.get('exec_use_time'):
                exec_use_time_value = int(request.GET.get('exec_use_time'))
                sqlDetail_list = sqlDetail_list.filter(exec_use_time__gt=exec_use_time_value)

            # 判断排序规则
            if request.GET.get('sort_rule'):
                sort_rule_value = request.GET.get('sort_rule')
                # 用户排序
                if sort_rule_value == 'exec_user':
                    sqlDetail_list = sqlDetail_list.order_by('exec_user')

                # 数据库排序
                if sort_rule_value == 'exec_db':
                    sqlDetail_list = sqlDetail_list.order_by('exec_db')

                # 执行时间升序
                if sort_rule_value == 'exec_use_time_up':
                    sqlDetail_list = sqlDetail_list.order_by('exec_use_time')

                # 执行时间降序
                if sort_rule_value == 'exec_use_time_down':
                    sqlDetail_list = sqlDetail_list.order_by('-exec_use_time')

                # 扫描行数升序
                if sort_rule_value == 'exec_rows_examined_up':
                    sqlDetail_list = sqlDetail_list.order_by('exec_rows_examined')

                # 扫描行数降序
                if sort_rule_value == 'exec_rows_examined_down':
                    sqlDetail_list = sqlDetail_list.order_by('-exec_rows_examined')

            print(3)
            # 记录数量
            record_nums = sqlDetail_list.count()

            # 判断页码
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1

            # 对取到的数据进行分页，记得定义每页的数量
            p = Paginator(sqlDetail_list, 20, request=request)

            # 分页处理后的 QuerySet
            sqlDetail_list = p.page(page)

            context = {
                'server_name': sever_name,
                'sqlFile': sqlFile,
                'exec_user_value': exec_user_value,
                'exec_db_value': exec_db_value,
                'exec_use_time_value': exec_use_time_value,
                'sort_rule_value': sort_rule_value,
                'sqlDetail_list': sqlDetail_list,
                'user_list': user_list,
                'db_list': db_list,
                'record_nums': record_nums,
            }

            return render(request, 'mysql_tools/slow-sql-list.html', context=context)
        else:
            return HttpResponse('查询文件ID存在错误!')


# 数据表查询统计
class MySQLFileTableDetailView(View):
    def get(self, request, file_id):
        # 查询数据
        if file_id.isalnum():
            # 文件
            sqlFile = models.MysqlUploadFile.objects.get(id=int(file_id))
            # 记录
            table_list = models.MysqlSqlTable.objects.filter(filename_id=int(file_id))
            context = {
                'sqlFile': sqlFile,
                'table_list': table_list,
            }

            return render(request, 'mysql_tools/slow-table-list.html', context=context)
