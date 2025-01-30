#!/bin/bash

# Перейти в директорию с проектом
cd /home/ubuntu/Diploma-Project || exit

# Обновить проект из репозитория
echo "Pulling latest changes..."
git reset --hard  # Сбросить любые локальные изменения
git clean -fd     # Удалить лишние файлы
git pull origin main || exit

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

echo "Waiting 30 seconds for container initialization..."
sleep 30


# Проверка доступности приложения
echo "Checking application health..."
for i in {1..10}; do
  RESPONSE=$(curl -k -s -o /dev/null -w "%{http_code}" https://localhost)

  if [ "$RESPONSE" -eq 200 ] || [ "$RESPONSE" -eq 301 ]; then
    echo "Application is ready!"
    break
  else
    echo "Attempt $i/10 - Got HTTP $RESPONSE, retrying in 15s..."
    sleep 15
  fi
done

if [[ "$RESPONSE" -ne 200 && "$RESPONSE" -ne 301 ]]; then
  echo "Health check failed! Last response: $RESPONSE"
  echo "Container logs:"
  docker logs artisans-nook-container
  exit 1
fi