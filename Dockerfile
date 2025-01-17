# Базовый образ с Nginx
FROM nginx:latest

# Удаляем стандартные конфиги
RUN rm /etc/nginx/conf.d/default.conf

# Копируем вашу конфигурацию
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем файлы сайта
COPY Artisans-Nook/ /usr/share/nginx/html/

# Копируем конфигурацию SSL
COPY options-ssl-nginx.conf /etc/letsencrypt/options-ssl-nginx.conf

# Открываем порты для работы контейнера
EXPOSE 80
EXPOSE 443
