# 快速参考手册

## EXE打包（Windows）

### 一键打包
```cmd
# 基础版本
build_exe.bat

# 高级版本（推荐）
build_exe_advanced.bat
```

### 打包输出
```
dist_app\
  ├── 股票监控系统.exe    # 主程序（40-60MB）
  └── 使用说明.txt         # 使用说明
```

### 使用打包后的程序
```cmd
# 双击运行
股票监控系统.exe

# 或命令行运行
.\股票监控系统.exe
```

### 访问地址
```
http://127.0.0.1:8000
（程序会自动打开浏览器）
```

---

## 简化生产环境（推荐）

### 一键部署
```bash
chmod +x start_production_simple.sh
./start_production_simple.sh deploy
```

### 常用命令
```bash
# 服务管理
./start_production_simple.sh start      # 启动服务
./start_production_simple.sh stop       # 停止服务
./start_production_simple.sh restart    # 重启服务
./start_production_simple.sh status     # 查看状态

# 日志查看
./start_production_simple.sh logs error     # 错误日志
./start_production_simple.sh logs access    # 访问日志

# 其他操作
./start_production_simple.sh rebuild        # 重新构建前端
sudo ./start_production_simple.sh firewall  # 配置防火墙
```

### 访问地址
```
http://your-server-ip:8000
```

---

## 完整生产环境（Nginx版）

### 一键部署
```bash
chmod +x start_production.sh
sudo ./start_production.sh deploy
```

### 常用命令
```bash
# 服务管理
sudo ./start_production.sh start      # 启动服务
sudo ./start_production.sh stop       # 停止服务
sudo ./start_production.sh restart    # 重启服务
sudo ./start_production.sh status     # 查看状态

# 日志查看
sudo ./start_production.sh logs backend        # 后端错误日志
sudo ./start_production.sh logs access         # 后端访问日志
sudo ./start_production.sh logs nginx-error    # Nginx错误日志
sudo ./start_production.sh logs nginx-access   # Nginx访问日志

# 重新构建
sudo ./start_production.sh rebuild    # 重新构建前端
```

### 访问地址
```
http://your-server-ip
```

---

## 开发环境 (Debian/Ubuntu)

### 一键启动
```bash
chmod +x start_debian.sh
./start_debian.sh
```

### 常用命令
```bash
./start_debian.sh start     # 启动服务
./start_debian.sh stop      # 停止服务
./start_debian.sh restart   # 重启服务
./start_debian.sh status    # 查看状态
./start_debian.sh install   # 仅安装依赖
```

### 访问地址
```
前端: http://localhost:3000
后端: http://localhost:5000
```

---

## 开发环境 (Windows)

### 一键启动
```cmd
双击 start.bat
或
start.bat
```

### 访问地址
```
前端: http://localhost:3000
后端: http://localhost:5000
```

---

## 系统服务管理

### systemd 命令 (生产环境)
```bash
# 后端服务
sudo systemctl start stock-backend      # 启动
sudo systemctl stop stock-backend       # 停止
sudo systemctl restart stock-backend    # 重启
sudo systemctl status stock-backend     # 状态
sudo systemctl enable stock-backend     # 开机自启
sudo systemctl disable stock-backend    # 禁用自启

# Nginx服务
sudo systemctl restart nginx            # 重启
sudo systemctl status nginx             # 状态
sudo systemctl reload nginx             # 重载配置
```

---

## 日志文件路径

### 生产环境
```bash
# 后端日志
/opt/stock/logs/gunicorn_access.log     # Gunicorn访问日志
/opt/stock/logs/gunicorn_error.log      # Gunicorn错误日志

# Nginx日志
/var/log/nginx/stock_access.log         # Nginx访问日志
/var/log/nginx/stock_error.log          # Nginx错误日志

# 查看实时日志
tail -f /opt/stock/logs/gunicorn_error.log
tail -f /var/log/nginx/stock_error.log
```

### 开发环境
```bash
logs/backend.log     # 后端日志
logs/frontend.log    # 前端日志

# 查看实时日志
tail -f logs/backend.log
tail -f logs/frontend.log
```

---

## 配置文件路径

### 后端配置
```bash
backend/app.py              # Flask主应用
backend/requirements.txt    # Python依赖
backend/.env (可选)         # 环境变量
```

### 前端配置
```bash
frontend/vite.config.js     # Vite配置
frontend/package.json       # Node.js依赖
frontend/.env               # 环境变量
```

### Nginx配置 (生产环境)
```bash
/etc/nginx/sites-available/stock    # 站点配置
/etc/nginx/sites-enabled/stock      # 启用的站点
/etc/nginx/nginx.conf                # 主配置

# 测试配置
sudo nginx -t

# 重载配置
sudo nginx -s reload
```

### systemd服务配置 (生产环境)
```bash
/etc/systemd/system/stock-backend.service    # 后端服务

# 重载配置
sudo systemctl daemon-reload
```

---

## 环境变量

### 前端 (frontend/.env)
```env
# 自动刷新间隔（秒）
VITE_AUTO_REFRESH_INTERVAL=20
```

修改后需要重启前端服务。

---

## 防火墙设置

### UFW
```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable            # 启用防火墙
sudo ufw status            # 查看状态
```

### iptables
```bash
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT     # 允许HTTP
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT    # 允许HTTPS
sudo iptables-save > /etc/iptables/rules.v4            # 保存规则
```

---

## 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| Nginx | 80 | HTTP (生产环境) |
| Nginx | 443 | HTTPS (可选) |
| Gunicorn/Flask | 5000 | 后端API (内部) |
| Vite Dev | 3000 | 前端开发服务器 |

---

## 故障排查

### 后端无法启动
```bash
# 查看服务状态
sudo systemctl status stock-backend

# 查看详细日志
sudo journalctl -u stock-backend -f

# 检查端口占用
sudo lsof -i :5000

# 手动测试
cd /opt/stock/backend
source venv/bin/activate
python app.py
```

### Nginx 502错误
```bash
# 检查后端是否运行
sudo systemctl status stock-backend

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/stock_error.log

# 检查Nginx配置
sudo nginx -t

# 重启服务
sudo systemctl restart stock-backend
sudo systemctl restart nginx
```

### 前端无法访问
```bash
# 检查dist目录
ls -la /opt/stock/frontend/dist/

# 重新构建
cd /opt/stock/frontend
npm run build

# 检查Nginx配置
sudo nginx -t
sudo systemctl restart nginx
```

---

## 更新代码

### 更新前端
```bash
# 上传新代码
scp -r frontend/src root@server:/opt/stock/frontend/

# 重新构建
sudo ./start_production.sh rebuild
```

### 更新后端
```bash
# 上传新代码
scp -r backend/ root@server:/opt/stock/

# 重启服务
sudo systemctl restart stock-backend
```

### 更新依赖
```bash
# 后端依赖
cd /opt/stock/backend
source venv/bin/activate
pip install -r requirements.txt

# 前端依赖
cd /opt/stock/frontend
npm install

# 重启服务
sudo systemctl restart stock-backend
sudo ./start_production.sh rebuild
```

---

## 性能监控

### 查看系统资源
```bash
# CPU和内存
top
htop

# 磁盘使用
df -h

# 网络连接
netstat -tunlp
ss -tunlp

# 进程
ps aux | grep gunicorn
ps aux | grep nginx
```

### 查看访问日志统计
```bash
# 访问次数最多的IP
cat /var/log/nginx/stock_access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -10

# 访问次数最多的URL
cat /var/log/nginx/stock_access.log | awk '{print $7}' | sort | uniq -c | sort -rn | head -10

# HTTP状态码统计
cat /var/log/nginx/stock_access.log | awk '{print $9}' | sort | uniq -c | sort -rn
```

---

## 备份与恢复

### 备份
```bash
# 备份整个项目
tar -czf stock_backup_$(date +%Y%m%d).tar.gz \
    --exclude='backend/venv' \
    --exclude='frontend/node_modules' \
    --exclude='frontend/dist' \
    --exclude='logs' \
    /opt/stock/

# 备份配置文件
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
    /etc/nginx/sites-available/stock \
    /etc/systemd/system/stock-backend.service \
    /opt/stock/frontend/.env \
    /opt/stock/backend/.env
```

### 恢复
```bash
# 停止服务
sudo ./start_production.sh stop

# 恢复文件
tar -xzf stock_backup_20250124.tar.gz -C /

# 重新部署
cd /opt/stock
sudo ./start_production.sh deploy
```

---

## 安全检查清单

- [ ] 配置防火墙，只开放必要端口
- [ ] 启用HTTPS（Let's Encrypt）
- [ ] 定期更新系统和依赖包
- [ ] 配置日志轮转
- [ ] 设置自动备份
- [ ] 监控系统资源使用
- [ ] 定期检查日志文件
- [ ] 使用强密码和SSH密钥
- [ ] 禁用root SSH登录
- [ ] 配置fail2ban防暴力破解

---

## 常用脚本

### 自动备份脚本
```bash
#!/bin/bash
# /opt/stock/backup.sh
BACKUP_DIR="/opt/backups/stock"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/stock_$DATE.tar.gz \
    --exclude='backend/venv' \
    --exclude='frontend/node_modules' \
    --exclude='frontend/dist' \
    --exclude='logs' \
    /opt/stock/
find $BACKUP_DIR -name "stock_*.tar.gz" -mtime +7 -delete
```

### 监控脚本
```bash
#!/bin/bash
# /opt/stock/monitor.sh
if ! systemctl is-active --quiet stock-backend; then
    echo "Backend service is down, restarting..."
    systemctl restart stock-backend
fi
if ! systemctl is-active --quiet nginx; then
    echo "Nginx is down, restarting..."
    systemctl restart nginx
fi
```

---

## 获取帮助

- 📖 [生产环境部署指南](PRODUCTION_DEPLOY.md)
- 📖 [Debian部署指南](DEBIAN_INSTALL.md)
- 📖 [快速入门指南](QUICKSTART.md)
- 📖 [主README](README.md)

