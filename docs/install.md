# 软件安装文档

## 1. 系统要求

| 项目 | 最低要求 |
|------|---------|
| 操作系统 | Windows 10+ / macOS 11+ / Linux (Ubuntu 20.04+) |
| 内存 | 4 GB（Docker 环境建议 8 GB） |
| 磁盘 | 10 GB 可用空间 |
| 浏览器 | Chrome 90+ / Edge 90+ / Firefox 88+ |

## 2. 前置软件

### 2.1 Docker 方式（推荐）

| 软件 | 版本 | 说明 |
|------|------|------|
| Docker | 24.0+ | 容器运行时 |
| Docker Compose | 2.20+ | 多容器编排 |
| Git | 2.40+ | 代码拉取 |

- Docker Desktop for Windows/Mac：[https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
- Linux 下需额外安装 `docker-compose-plugin`

### 2.2 手动方式

| 软件 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 后端运行环境 |
| Node.js | 18+ | 前端构建环境（建议 20 LTS） |
| MySQL | 8.0+ | 数据库 |
| Redis | 7.0+ | 缓存与消息队列 |

## 3. 开发环境安装（Docker）

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd NoStockHub

# 2. 复制环境变量文件（使用默认值即可）
cp .env.example .env

# 3. 启动所有服务
docker-compose up -d

# 4. 查看日志确认启动成功
docker-compose logs -f backend

# 5. 访问
# 前端: http://localhost:5173
# 后端 API: http://localhost:8000/api/
# Swagger 文档: http://localhost:8000/api/docs/
```

服务启动后会自动执行数据库迁移和种子数据填充。首次启动需拉取镜像（约 5-10 分钟）。

### 3.1 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend | 5173 | Vue 3 开发服务器（热更新） |
| backend | 8000 | Django REST Framework API |
| db | 3306 | MySQL 8.0 |
| redis | 6379 | Redis 缓存 |
| celery | — | 异步任务 Worker |

### 3.2 常用命令

```bash
# 重新构建并启动
docker-compose up -d --build

# 停止所有服务
docker-compose down

# 停止并删除数据卷（重置数据库）
docker-compose down -v

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh

# 运行 Django 管理命令
docker-compose exec backend python manage.py <command>
```

## 4. 生产环境部署

### 4.1 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入真实值：

```ini
DB_PASSWORD=your_secure_password
DJANGO_SECRET_KEY=随机生成的密钥
DOMAIN=your-domain.com
```

生成 `DJANGO_SECRET_KEY`：

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4.2 启动生产服务

```bash
docker-compose -f docker-compose.prod.yml up -d
```

生产环境架构：

- 前端由 Nginx 反向代理（80 端口），自动处理 `/api/` 转发和 `/media/` 文件服务
- 后端由 Gunicorn（4 workers）运行，不使用 `runserver`
- 数据库和 Redis 均启用健康检查，依赖启动顺序保证
- 媒体文件通过 `media_data` named volume 持久化

### 4.3 更新部署

```bash
git pull
docker-compose -f docker-compose.prod.yml up -d --build
```

## 5. 手动安装（不使用 Docker）

### 5.1 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate    # Linux/Mac
# venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export DJANGO_SETTINGS_MODULE=config.settings.dev
export DB_HOST=127.0.0.1
export DB_PASSWORD=your_db_password
export REDIS_URL=redis://127.0.0.1:6379/0

# 数据库迁移
python manage.py migrate

# 填充种子数据（可选）
python manage.py seed_dev

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 5.2 启动 Celery Worker（可选，用于异步任务）

```bash
cd backend
celery -A tasks worker -l info
```

### 5.3 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 生产构建
npm run build
```

开发模式下 Vite 自动将 `/api/` 和 `/media/` 请求代理到 `http://127.0.0.1:8000`。

## 6. 配置说明

### 6.1 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DB_HOST` | 127.0.0.1 | 数据库地址 |
| `DB_PORT` | 3306 | 数据库端口 |
| `DB_NAME` | project_platform | 数据库名称 |
| `DB_USER` | root | 数据库用户 |
| `DB_PASSWORD` | — | 数据库密码（必填） |
| `REDIS_URL` | redis://127.0.0.1:6379/0 | Redis 连接 |
| `DJANGO_SECRET_KEY` | — | Django 密钥（生产必填） |
| `DJANGO_SETTINGS_MODULE` | config.settings.base | 配置模块 |
| `DEBUG` | false | 调试模式 |
| `ALLOWED_HOSTS` | * | 允许访问的主机 |
| `CORS_ORIGINS` | localhost:5173 | 跨域白名单 |
| `DOMAIN` | — | 生产环境域名 |

### 6.2 Django Settings 模块

| 模块 | 适用场景 | 特点 |
|------|---------|------|
| `config.settings.dev` | 本地开发 | DEBUG=True, SQLite |
| `config.settings.base` | Docker 开发 | DEBUG=True, MySQL |
| `config.settings.prod` | 生产部署 | DEBUG=False, MySQL, 安全配置 |

## 7. 验证安装

安装完成后，验证各服务是否正常：

```bash
# 检查后端 API
curl http://localhost:8000/api/auth/profile/ -H "Authorization: Bearer <token>"

# 检查前端
curl http://localhost:5173

# Docker 环境检查容器状态
docker-compose ps
```

进入系统后，使用种子数据中的测试账号登录（如果执行了 `seed_dev`），或注册新账号开始使用。
