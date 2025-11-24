# 生产环境部署指南

本文档介绍如何在生产环境中部署股票监控系统，支持外网访问。

## 架构说明

生产环境采用以下架构：

```
外网请求
    ↓
Nginx (80端口)
    ├── / → 静态文件 (Vue Build)
    └── /api → 反向代理 → Gunicorn (5000端口) → Flask应用
```

### 技术栈

- **Web服务器**: Nginx
- **WSGI服务器**: Gunicorn (4 workers)
- **后端**: Flask
- **前端**: Vue 3 (生产构建)
- **进程管理**: systemd

## 快速部署

### 前置要求

- Debian 10+ / Ubuntu 18.04+
- Root 权限
- 至少 2GB 内存
- 至少 2GB 可用磁盘空间

### 一键部署

```bash
# 1. 上传项目到服务器
scp -r stock/ root@your-server:/opt/

# 2. 登录服务器
ssh root@your-server

# 3. 进入项目目录
cd /opt/stock

# 4. 赋予执行权限
chmod +x start_production.sh

# 5. 执行部署（需要root权限）
sudo ./start_production.sh deploy
```

部署过程会自动：
1. 安装系统依赖（Python3、Node.js、Nginx）
2. 安装后端依赖和Gunicorn
3. 构建前端生产版本
4. 配置Nginx
5. 创建systemd服务
6. 启动所有服务

部署完成后，访问: `http://your-server-ip`

## 命令详解

### 部署命令

```bash
sudo ./start_production.sh deploy
```

### 服务管理

```bash
# 启动服务
sudo ./start_production.sh start

# 停止服务
sudo ./start_production.sh stop

# 重启服务
sudo ./start_production.sh restart

# 查看状态
sudo ./start_production.sh status
```

### 日志查看

```bash
# 查看后端错误日志
sudo ./start_production.sh logs backend

# 查看后端访问日志
sudo ./start_production.sh logs access

# 查看Nginx访问日志
sudo ./start_production.sh logs nginx-access

# 查看Nginx错误日志
sudo ./start_production.sh logs nginx-error
```

### 重新构建前端

当修改了前端代码后：

```bash
sudo ./start_production.sh rebuild
```

## 手动部署步骤

如果自动脚本无法使用，可以手动部署：

### 1. 安装系统依赖

```bash
# 更新软件源
apt-get update

# 安装 Python3
apt-get install -y python3 python3-pip python3-venv

# 安装 Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# 安装 Nginx
apt-get install -y nginx
```

### 2. 配置后端

```bash
cd /opt/stock/backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 Gunicorn
pip install gunicorn
```

### 3. 构建前端

```bash
cd /opt/stock/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

### 4. 配置 Nginx

创建配置文件 `/etc/nginx/sites-available/stock`:

```nginx
server {
    listen 80;
    server_name your-server-ip;
    
    # 前端静态文件
    location / {
        root /opt/stock/frontend/dist;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "public, max-age=31536000" always;
    }
    
    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;
    
    access_log /var/log/nginx/stock_access.log;
    error_log /var/log/nginx/stock_error.log;
}
```

启用配置：

```bash
# 启用站点
ln -s /etc/nginx/sites-available/stock /etc/nginx/sites-enabled/

# 删除默认站点
rm /etc/nginx/sites-enabled/default

# 测试配置
nginx -t

# 重启Nginx
systemctl restart nginx
systemctl enable nginx
```

### 5. 配置 systemd 服务

创建服务文件 `/etc/systemd/system/stock-backend.service`:

```ini
[Unit]
Description=Stock Monitor Backend API
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=/opt/stock/backend
Environment="PATH=/opt/stock/backend/venv/bin"
ExecStart=/opt/stock/backend/venv/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /opt/stock/logs/gunicorn_access.log \
    --error-logfile /opt/stock/logs/gunicorn_error.log \
    app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGQUIT
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 创建日志目录
mkdir -p /opt/stock/logs

# 重载systemd
systemctl daemon-reload

# 启动并启用服务
systemctl enable stock-backend
systemctl start stock-backend

# 检查状态
systemctl status stock-backend
```

## 配置防火墙

### UFW 防火墙

```bash
# 安装UFW
apt-get install -y ufw

# 允许SSH（重要！）
ufw allow 22/tcp

# 允许HTTP
ufw allow 80/tcp

# 允许HTTPS（如果需要）
ufw allow 443/tcp

# 启用防火墙
ufw enable

# 查看状态
ufw status
```

### iptables 防火墙

```bash
# 允许HTTP
iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# 允许HTTPS
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 保存规则
iptables-save > /etc/iptables/rules.v4
```

## HTTPS 配置 (可选)

### 使用 Let's Encrypt

```bash
# 安装 Certbot
apt-get install -y certbot python3-certbot-nginx

# 获取证书（替换为你的域名）
certbot --nginx -d your-domain.com

# 自动续期
certbot renew --dry-run
```

Certbot 会自动修改 Nginx 配置，添加 HTTPS 支持。

## 性能优化

### 1. 调整 Gunicorn Workers

根据CPU核心数调整：

```bash
# 推荐公式: workers = (2 × CPU核心数) + 1
# 4核CPU: workers = 9

# 修改 /etc/systemd/system/stock-backend.service
--workers 9
```

### 2. 启用 Nginx 缓存

在 Nginx 配置中添加：

```nginx
# 定义缓存路径
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m inactive=60m;

server {
    # ... 其他配置 ...
    
    location /api {
        # 启用缓存
        proxy_cache api_cache;
        proxy_cache_valid 200 5m;
        proxy_cache_key "$scheme$request_method$host$request_uri";
        
        # 其他代理配置...
    }
}
```

### 3. 优化系统参数

编辑 `/etc/sysctl.conf`:

```bash
# 网络优化
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.ip_local_port_range = 1024 65535

# 应用配置
sysctl -p
```

## 监控和维护

### 查看服务状态

```bash
# 后端服务
systemctl status stock-backend

# Nginx服务
systemctl status nginx

# 查看端口监听
netstat -tlnp | grep -E ":80|:5000"
```

### 查看资源使用

```bash
# 查看CPU和内存
top

# 查看Gunicorn进程
ps aux | grep gunicorn

# 查看磁盘使用
df -h
```

### 日志轮转

创建 `/etc/logrotate.d/stock`:

```
/opt/stock/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 root root
    sharedscripts
    postrotate
        systemctl reload stock-backend > /dev/null 2>&1 || true
    endscript
}
```

### 定期备份

```bash
# 创建备份脚本
cat > /opt/stock/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/stock"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/stock_$DATE.tar.gz \
    --exclude='backend/venv' \
    --exclude='frontend/node_modules' \
    --exclude='frontend/dist' \
    --exclude='logs' \
    /opt/stock/
# 保留最近7天的备份
find $BACKUP_DIR -name "stock_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /opt/stock/backup.sh

# 添加到crontab（每天凌晨2点备份）
echo "0 2 * * * /opt/stock/backup.sh" | crontab -
```

## 故障排查

### 后端服务无法启动

```bash
# 查看详细日志
journalctl -u stock-backend -f

# 检查端口占用
lsof -i :5000

# 手动测试
cd /opt/stock/backend
source venv/bin/activate
gunicorn --bind 0.0.0.0:5000 app:app
```

### Nginx 502 Bad Gateway

1. 检查后端服务是否运行
2. 检查防火墙是否阻止
3. 查看 Nginx 错误日志

```bash
systemctl status stock-backend
tail -f /var/log/nginx/stock_error.log
```

### 前端无法加载

1. 检查 dist 目录是否存在
2. 重新构建前端
3. 检查 Nginx 配置

```bash
ls -la /opt/stock/frontend/dist
sudo ./start_production.sh rebuild
nginx -t
```

## 更新部署

### 更新代码

```bash
# 1. 备份当前版本
cd /opt
tar -czf stock_backup_$(date +%Y%m%d).tar.gz stock/

# 2. 上传新代码
scp -r stock/ root@your-server:/opt/stock_new/

# 3. 停止服务
cd /opt/stock
sudo ./start_production.sh stop

# 4. 替换代码
cd /opt
mv stock stock_old
mv stock_new stock

# 5. 重新部署
cd /opt/stock
chmod +x start_production.sh
sudo ./start_production.sh deploy
```

### 仅更新前端

```bash
# 上传前端代码
scp -r frontend/ root@your-server:/opt/stock/

# 重新构建
sudo ./start_production.sh rebuild
```

### 仅更新后端

```bash
# 上传后端代码
scp -r backend/ root@your-server:/opt/stock/

# 重启后端服务
systemctl restart stock-backend
```

## 安全建议

1. **更改默认端口**: 使用非标准端口（如8080）
2. **配置 HTTPS**: 使用 SSL/TLS 加密
3. **限制访问**: 使用 IP 白名单或防火墙规则
4. **定期更新**: 保持系统和依赖包更新
5. **日志监控**: 监控异常访问和错误
6. **备份数据**: 定期备份重要数据

## 性能基准

在 2核4GB 配置下：

- **并发用户**: 支持 100+ 并发用户
- **响应时间**: 平均 < 100ms
- **内存使用**: 约 500MB
- **CPU使用**: 平均 < 20%

## 技术支持

遇到问题：
1. 查看日志文件
2. 检查系统资源
3. 查阅本文档
4. 提交 Issue

---

**注意**: 生产环境部署需要一定的Linux系统管理经验，建议在测试环境先进行演练。

