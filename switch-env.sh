#!/bin/bash

# 檢查參數
if [ "$1" != "dev" ] && [ "$1" != "prod" ]; then
    echo "Usage: ./switch-env.sh [dev|prod]"
    exit 1
fi

# 停止並完全清理現有容器與數據
echo "Stopping and cleaning up existing containers..."
docker compose down -v
docker rm -f $(docker ps -aq) 2>/dev/null || true
docker volume prune -f

# 等待所有容器完全停止
echo "Waiting for containers to stop..."
sleep 5

# 根據環境啟動
if [ "$1" == "dev" ]; then
    echo "Switching to development environment..."
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    docker compose -f docker-compose.dev.yml up -d --build --remove-orphans
else
    echo "Switching to production environment..."
    export FLASK_ENV=production
    export FLASK_DEBUG=0
    docker compose -f docker-compose.prod.yml up -d --build --remove-orphans
fi

# 等待服務啟動
echo "Waiting for services to start..."
sleep 10

# 顯示容器狀態
docker compose ps

# 顯示日誌
echo "Showing recent logs..."
docker compose logs --tail=50
