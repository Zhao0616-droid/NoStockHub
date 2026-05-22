#!/bin/bash
# ============================================
# NoStockHub 一键部署脚本
# 用法：bash deploy.sh
# ============================================

set -e

echo "============================================"
echo "  NoStockHub 生产环境部署"
echo "============================================"

# 1. 检查依赖
if ! command -v docker &> /dev/null; then
    echo "[错误] 未找到 docker，请先安装 Docker"
    exit 1
fi
if ! docker compose version &> /dev/null; then
    echo "[错误] 未找到 docker compose 插件"
    exit 1
fi

# 2. 检查 .env 文件
if [ ! -f .env ]; then
    echo "[错误] 未找到 .env 文件"
    echo "请先执行：cp .env.example .env 并填入真实值"
    exit 1
fi

# 3. 导出环境变量
set -a
source .env
set +a

# 4. 构建并启动
echo "[1/3] 构建镜像..."
docker compose -f docker-compose.prod.yml build

echo "[2/3] 启动服务..."
docker compose -f docker-compose.prod.yml up -d

echo "[3/3] 等待服务就绪..."
sleep 10

# 5. 创建超级管理员
echo "是否创建 Django 超级管理员？(y/n)"
read -r create_admin
if [ "$create_admin" = "y" ]; then
    docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
fi

echo "============================================"
echo "  部署完成！"
echo "============================================"

SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "你的服务器IP")
echo "  网站：        http://${DOMAIN:-$SERVER_IP}"
echo "  API 文档：    http://${DOMAIN:-$SERVER_IP}/api/docs/"
echo "  Django Admin：http://${DOMAIN:-$SERVER_IP}/admin/"
echo ""
echo "常用命令："
echo "  查看日志：docker compose -f docker-compose.prod.yml logs -f"
echo "  重启服务：docker compose -f docker-compose.prod.yml restart"
echo "  停止服务：docker compose -f docker-compose.prod.yml down"
