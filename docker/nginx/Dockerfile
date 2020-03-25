FROM nginx:1.17.9
LABEL author="Dylan" mail="1214966109@qq.com"
COPY ssap/ /data/ssap/
COPY docker/ssap/config/uwsgi.ini /data/
RUN cd /etc/nginx/ && mv nginx.conf nginx.conf_bak
COPY docker/nginx/config/nginx.conf /etc/nginx/
EXPOSE 10000
CMD ["nginx", "-g", "daemon off;"]
