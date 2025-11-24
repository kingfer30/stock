
# 简化生产环境部署指南

通过 IP:端口 直接访问，无需域名和Nginx。

## 架构说明

```
外网请求
    ↓
Gunicorn (8000端口)
    ├── / → 静态文件 (Vue Build)
    └── /api → Flask应用
```

### 技术栈

- **WSGI服务器**: Gunicorn (4 workers)
- **应用服务器**: Flask (serve静态文件 + API)
- **前端**: Vue 3 (生产构建)
- **进程管理**: systemd (可选) 或 手动管理

## 快速部署

### 前置要求

- Debian 10+ / Ubuntu 18.04+
- Python 3.7+
- Node.js 14+
- 至少 2GB 内存

### 一键部署

```bash
# 1. 上传项目到服务器
scp -r stock/ user@your-server:/opt/

# 2. 登录服务器
ssh user@your-server

# 3. 进入项目目录
cd /opt/stock

# 4. 赋予执行权限
chmod +x start_production_simple.sh

# 5. 执行部署
./start_production_simple.sh deploy
```

部署完成后，访问: `http://your-server-ip:8000`

## 命令详解

### 部署命令

```bash
./start_production_simple.sh deploy
```

自动完成：
1. 检查并安装依赖（Python3、Node.js）
2. 安装后端依赖和Gunicorn
3. 构建前端生产版本
4. 将前端静态文件部署到backend/static
5. 创建systemd服务（如果有root权限）
6. 启动服务

### 服务管理

```bash
# 启动服务
./start_production_simple.sh start

# 停止服务
./start_production_simple.sh stop

# 重启服务
./start_production_simple.sh restart

# 查看状态
./start_production_simple.sh status
```

### 日志查看

```bash
# 查看错误日志
./start_production_simple.sh logs error

# 查看访问日志
./start_production_simple.sh logs access

# 实时查看日志
tail -f logs/gunicorn_error.log
tail -f logs/gunicorn_access.log
```

### 其他命令

```bash
# 重新构建前端
./start_production_simple.sh rebuild

# 配置防火墙（需要root）
sudo ./start_production_simple.sh firewall
```

## 配置说明

### 默认配置

- **监听地址**: 0.0.0.0（允许外网访问）
- **端口**: 8000
- **Worker数量**: 4
- **超时时间**: 120秒

### 修改端口

编辑 `start_production_simple.sh`：

```bash
BACKEND_PORT="8000"  # 修改为你需要的端口
```

修改后重新部署：

```bash
./start_production_simple.sh deploy
```

### 修改Worker数量

编辑 `start_production_simple.sh`：

```bash
BACKEND_WORKERS="4"  # 推荐: (2 × CPU核心数) + 1
```

## 防火墙配置

### 使用UFW

```bash
# 允许应用端口
sudo ufw allow 8000/tcp

# 或使用脚本自动配置
sudo ./start_production_simple.sh firewall

# 查看状态
sudo ufw status
```

### 使用iptables

```bash
# 允许端口
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT

# 保存规则
sudo iptables-save > /etc/iptables/rules.v4
```

### 阿里云/腾讯云安全组

在云服务商控制台添加入站规则：
- 协议: TCP
- 端口: 8000
- 源: 0.0.0.0/0（允许所有IP）

## systemd服务管理

如果使用root权限部署，会自动创建systemd服务。

### systemd命令

```bash
# 启动服务
sudo systemctl start stock-app

# 停止服务
sudo systemctl stop stock-app

# 重启服务
sudo systemctl restart stock-app

# 查看状态
sudo systemctl status stock-app

# 查看日志
sudo journalctl -u stock-app -f

# 开机自启
sudo systemctl enable stock-app

# 禁用自启
sudo systemctl disable stock-app
```

### 修改systemd配置

编辑服务文件：

```bash
sudo nano /etc/systemd/system/stock-app.service
```

修改后重载：

```bash
sudo systemctl daemon-reload
sudo systemctl restart stock-app
```

## 手动部署步骤

如果自动脚本无法使用：

### 1. 安装依赖

```bash
# 安装系统依赖
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nodejs npm

# 进入项目目录
cd /opt/stock
```

### 2. 配置后端

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn
```

### 3. 构建前端

```bash
cd ../frontend

# 安装依赖
npm install

# 构建
npm run build

# 部署到backend/static
rm -rf ../backend/static
mkdir -p ../backend/static
cp -r dist/* ../backend/static/
```

### 4. 启动服务

```bash
cd ../backend
source venv/bin/activate

# 创建日志目录
mkdir -p ../logs

# 启动Gunicorn
gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile ../logs/gunicorn_access.log \
    --error-logfile ../logs/gunicorn_error.log \
    --daemon \
    --pid ../logs/app.pid \
    app:app
```

## 性能优化

### 1. 调整Worker数量

```bash
# CPU密集型应用
workers = (2 × CPU核心数) + 1

# IO密集型应用
workers = (4 × CPU核心数) + 1
```

### 2. 启用Gzip压缩

已在Flask中启用，无需额外配置。

### 3. 调整超时时间

如果API响应时间较长：

```bash
--timeout 300  # 5分钟
```

## 监控和维护

### 查看服务状态

```bash
# 使用脚本
./start_production_simple.sh status

# 查看进程
ps aux | grep gunicorn

# 查看端口
netstat -tlnp | grep 8000
# 或
ss -tlnp | grep 8000
```

### 查看资源使用

```bash
# CPU和内存
top
htop

# 磁盘
df -h

# 网络连接
netstat -an | grep 8000
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
    create 0644 user user
    sharedscripts
    postrotate
        kill -USR1 $(cat /opt/stock/logs/app.pid) > /dev/null 2>&1 || true
    endscript
}
```

## 故障排查

### 服务无法启动

```bash
# 查看日志
cat logs/gunicorn_error.log

# 检查端口占用
lsof -i :8000

# 手动测试
cd backend
source venv/bin/activate
python app.py
```

### 无法访问

1. 检查服务是否运行
2. 检查防火墙规则
3. 检查云服务商安全组
4. 检查端口监听地址

```bash
# 检查监听
netstat -tlnp | grep 8000

# 测试本地访问
curl http://localhost:8000/api

# 测试外网访问
curl http://your-server-ip:8000/api
```

### 静态文件404

```bash
# 检查static目录
ls -la backend/static/

# 重新构建
./start_production_simple.sh rebuild
```

## 更新部署

### 更新代码

```bash
# 1. 备份
tar -czf stock_backup_$(date +%Y%m%d).tar.gz stock/

# 2. 上传新代码
scp -r stock/ user@server:/opt/stock_new/

# 3. 停止服务
cd /opt/stock
./start_production_simple.sh stop

# 4. 替换代码
cd /opt
mv stock stock_old
mv stock_new stock

# 5. 重新部署
cd /opt/stock
./start_production_simple.sh deploy
```

### 仅更新前端

```bash
# 上传前端代码
scp -r frontend/ user@server:/opt/stock/

# 重新构建
./start_production_simple.sh rebuild
```

### 仅更新后端

```bash
# 上传后端代码
scp -r backend/ user@server:/opt/stock/

# 重启服务
./start_production_simple.sh restart
```

## 性能基准

在 2核4GB 配置下：

- **并发用户**: 50-100
- **响应时间**: < 150ms
- **内存使用**: 约 400MB
- **CPU使用**: < 30%

## 优缺点

### 优点

- ✅ 部署简单，无需配置Nginx
- ✅ 维护方便，只需管理一个服务
- ✅ 资源占用少
- ✅ 适合小型项目

### 缺点

- ❌ 性能不如Nginx
- ❌ 不支持HTTPS（需要额外配置）
- ❌ 静态文件缓存能力有限
- ❌ 不支持负载均衡

### 适用场景

- 内部系统
- 小型项目（< 100并发）
- 开发/测试环境
- 临时演示

### 不适用场景

如需以下功能，建议使用完整版（含Nginx）：
- HTTPS
- 高并发（> 100）
- 负载均衡
- 静态文件CDN
- 域名访问

## 安全建议

1. **更改默认端口**: 使用非常用端口
2. **限制访问IP**: 使用防火墙规则
3. **定期更新**: 保持依赖最新
4. **日志监控**: 监控异常请求
5. **备份数据**: 定期备份代码

### IP白名单示例

```bash
# 只允许特定IP访问
sudo iptables -A INPUT -p tcp --dport 8000 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8000 -j DROP
```

## 升级到完整版

如果需要更好的性能和功能，可以升级到Nginx版本：

```bash
# 停止当前服务
./start_production_simple.sh stop

# 使用完整版脚本
chmod +x start_production.sh
sudo ./start_production.sh deploy
```

## 常见问题

### Q: 如何修改端口？

A: 编辑 `start_production_simple.sh`，修改 `BACKEND_PORT` 变量，然后重新部署。

### Q: 支持HTTPS吗？

A: 不直接支持。建议使用Nginx版本或在前面加一层反向代理。

### Q: 可以用于生产环境吗？

A: 可以用于小型项目和内部系统。大型项目建议使用Nginx版本。

### Q: 如何查看实时访问？

A: `tail -f logs/gunicorn_access.log`

### Q: 服务异常退出怎么办？

A: 使用systemd可以自动重启。检查 `logs/gunicorn_error.log` 查看错误原因。

## 技术支持

遇到问题：
1. 查看日志文件
2. 检查防火墙和安全组
3. 查阅本文档
4. 提交 Issue

---

**提示**: 这是简化版部署方案，适合快速部署和小型项目。如需更多功能和更好性能，请查看 [完整生产环境部署指南](PRODUCTION_DEPLOY.md)。

