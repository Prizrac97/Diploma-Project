#!/bin/bash

# Перейти в директорию с проектом
cd /path/to/your/project || exit

# Обновить репозиторий
git pull origin main

# Остановить и удалить старый контейнер, если он существует
docker stop artisans-nook-container || true
docker rm artisans-nook-container || true

# Отладочный вывод для проверки переменной
echo "Using Docker username: $DOCKER_USERNAME"

# Скачивать последний образ с DockerHub
docker pull $DOCKER_USERNAME/artisans-nook:latest

# Запустить новый контейнер с дополнительными параметрами
docker run -d \
  --name artisans-nook-container \
  -p 80:80 \
  -p 443:443 \
  --restart always \
  -v /etc/letsencrypt:/etc/letsencrypt \
  $DOCKER_USERNAME/artisans-nook:latest
