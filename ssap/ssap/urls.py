# 入口路由
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.views.static import serve

# 用户定义
from apps.mysql_tools.views import IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    # 静态文件
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    # 首页
    path('', IndexView.as_view(), name='index'),
    # mysql 入口
    path('mysql/', include('apps.mysql_tools.urls')),
]
