#!/bin/bash

# Перейти в директорию проекта
cd /var/www/Artisans-Nook || exit

# Остановить старый контейнер (если он существует)
docker stop artisans-nook-container || true
docker rm artisans-nook-container || true

# Сборка нового Docker образа
docker build -t artisans-nook .

# Запуск нового контейнера
sudo docker run -d --name artisans-nook-container \
  -p 80:80 -p 443:443 \
  -v /etc/letsencrypt:/etc/letsencrypt \
  artisans-nook

