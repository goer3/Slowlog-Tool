# MySQL路由
from django.urls import path, include
from . import views

# 用户定义
app_name = 'mysql_tools'

urlpatterns = [
    # 文件上传
    path('file/upload.html', views.MysqlFileUploadView.as_view(), name="mysql_file_upload"),
    # 上传文件列表
    path('file/upload/list.html', views.MysqlFileUploadListView.as_view(), name="mysql_file_upload_list"),
    # 删除记录
    path('file/upload/del/<str:file_id>.html', views.MysqlDelUploadFileView.as_view(), name="mysql_file_upload_del"),
    # SQL 详情
    path('file/upload/detail/<str:file_id>.html', views.MySQLFileSqlDetailView.as_view(), name="mysql_file_upload_detail"),
    # 数据表详情
    path('file/upload/table/<str:file_id>.html', views.MySQLFileTableDetailView.as_view(), name="mysql_file_upload_table"),
]
