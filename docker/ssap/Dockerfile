FROM python:3.5.2
LABEL author="Dylan" mail="1214966109@qq.com"
COPY ssap/ /data/ssap/
COPY docker/ssap/config/uwsgi.ini /data/
WORKDIR /data/ssap/
RUN pip install -r requirements.txt -i http://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn && \
    python manage.py makemigrations && python manage.py migrate && \
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell
EXPOSE 8000
CMD ["uwsgi", "/data/uwsgi.ini"]
