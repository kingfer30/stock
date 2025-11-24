# Debian/Ubuntu 系统一键部署指南

本文档介绍如何在 Debian/Ubuntu 系统上一键部署股票监控系统。

## 系统要求

- **操作系统**: Debian 10+ / Ubuntu 18.04+
- **架构**: x86_64 / amd64
- **内存**: 建议 2GB+
- **磁盘**: 建议 1GB+ 可用空间

## 快速开始

### 1. 下载项目

```bash
# 如果使用 git
git clone <your-repo-url>
cd stock

# 或者解压压缩包
unzip stock.zip
cd stock
```

### 2. 赋予执行权限

```bash
chmod +x start_debian.sh
```

### 3. 一键启动

```bash
./start_debian.sh
```

首次运行会自动：
1. 检查并安装系统依赖（Python3、Node.js）
2. 创建 Python 虚拟环境
3. 安装后端依赖
4. 安装前端依赖
5. 创建环境配置文件
6. 启动后端服务（Flask）
7. 启动前端服务（Vite）

### 4. 访问系统

启动完成后，在浏览器中访问：

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:5000

## 命令详解

### 启动服务

```bash
./start_debian.sh start
# 或者
./start_debian.sh
```

### 停止服务

```bash
./start_debian.sh stop
```

### 重启服务

```bash
./start_debian.sh restart
```

### 查看状态

```bash
./start_debian.sh status
```

### 仅安装依赖

```bash
./start_debian.sh install
```

## 日志查看

### 实时查看后端日志

```bash
tail -f logs/backend.log
```

### 实时查看前端日志

```bash
tail -f logs/frontend.log
```

### 查看历史日志

```bash
cat logs/backend.log
cat logs/frontend.log
```

## 环境变量配置

前端环境变量文件位于 `frontend/.env`：

```env
# 自动刷新间隔（秒）
VITE_AUTO_REFRESH_INTERVAL=20
```

修改配置后需要重启前端服务：

```bash
./start_debian.sh restart
```

## 常见问题

### 1. 端口被占用

**问题**: 提示端口 3000 或 5000 被占用

**解决方案**:

```bash
# 查找占用端口的进程
sudo lsof -i :3000
sudo lsof -i :5000

# 结束进程
sudo kill -9 <PID>

# 重新启动
./start_debian.sh start
```

### 2. Python 虚拟环境问题

**问题**: 虚拟环境创建失败

**解决方案**:

```bash
# 删除旧的虚拟环境
rm -rf backend/venv

# 重新安装
./start_debian.sh install
```

### 3. Node.js 版本过低

**问题**: npm 安装失败，提示 Node.js 版本不兼容

**解决方案**:

```bash
# 卸载旧版本
sudo apt-get remove nodejs npm

# 安装 Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证版本
node --version  # 应该显示 v18.x.x
npm --version

# 重新安装依赖
./start_debian.sh install
```

### 4. 权限不足

**问题**: 提示权限不足

**解决方案**:

```bash
# 赋予脚本执行权限
chmod +x start_debian.sh

# 如果需要安装系统依赖，使用 sudo
sudo ./start_debian.sh
```

### 5. 依赖安装失败

**问题**: pip 或 npm 安装依赖失败

**解决方案**:

```bash
# 更新系统软件源
sudo apt-get update

# 清理 pip 缓存
pip cache purge

# 清理 npm 缓存
npm cache clean --force

# 重新安装
./start_debian.sh install
```

## 手动安装步骤

如果自动脚本无法运行，可以按以下步骤手动安装：

### 1. 安装系统依赖

```bash
# 更新软件源
sudo apt-get update

# 安装 Python3
sudo apt-get install -y python3 python3-pip python3-venv

# 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 2. 安装后端依赖

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd ../frontend

# 安装依赖
npm install
```

### 4. 启动服务

```bash
# 启动后端（在 backend 目录）
cd ../backend
source venv/bin/activate
python app.py &

# 启动前端（在 frontend 目录）
cd ../frontend
npm run dev &
```

## 生产环境部署

### 使用 systemd 管理服务

创建后端服务文件 `/etc/systemd/system/stock-backend.service`:

```ini
[Unit]
Description=Stock Monitor Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/stock/backend
Environment="PATH=/path/to/stock/backend/venv/bin"
ExecStart=/path/to/stock/backend/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

创建前端服务文件 `/etc/systemd/system/stock-frontend.service`:

```ini
[Unit]
Description=Stock Monitor Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/stock/frontend
ExecStart=/usr/bin/npm run dev
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable stock-backend stock-frontend
sudo systemctl start stock-backend stock-frontend
sudo systemctl status stock-backend stock-frontend
```

### 使用 Nginx 反向代理

安装 Nginx:

```bash
sudo apt-get install -y nginx
```

配置文件 `/etc/nginx/sites-available/stock`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/stock /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 性能优化

### 1. 使用生产模式

前端构建生产版本：

```bash
cd frontend
npm run build
```

### 2. 使用 Gunicorn 运行后端

```bash
cd backend
source venv/bin/activate
pip install gunicorn

# 启动
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 安全建议

1. **更改默认端口**: 修改配置文件中的端口号
2. **使用 HTTPS**: 配置 SSL 证书
3. **设置防火墙**: 只开放必要的端口
4. **定期更新**: 保持依赖包更新

```bash
# 更新 Python 依赖
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt

# 更新 Node.js 依赖
cd ../frontend
npm update
```

## 卸载

```bash
# 停止服务
./start_debian.sh stop

# 删除项目目录
cd ..
rm -rf stock
```

## 技术支持

如遇到问题，请查看：
- 后端日志: `logs/backend.log`
- 前端日志: `logs/frontend.log`

或提交 Issue 到项目仓库。

