#!/bin/bash

# 股票监控系统 - 生产环境部署脚本
# 适用于 Debian/Ubuntu 系统

set -e  # 遇到错误立即退出

echo "================================"
echo "股票监控系统 - 生产环境部署"
echo "================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 配置
BACKEND_HOST="0.0.0.0"
BACKEND_PORT="5000"
BACKEND_WORKERS="4"
FRONTEND_PORT="80"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${BLUE}[SUCCESS]${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        log_error "请使用 root 权限运行此脚本"
        log_info "使用命令: sudo ./start_production.sh"
        exit 1
    fi
}

# 检查并安装系统依赖
install_system_dependencies() {
    log_info "检查并安装系统依赖..."
    
    # 更新软件源
    apt-get update
    
    # 安装 Python3
    if ! command_exists python3; then
        log_info "安装 Python3..."
        apt-get install -y python3 python3-pip python3-venv
    fi
    
    # 安装 Node.js
    if ! command_exists node; then
        log_info "安装 Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
        apt-get install -y nodejs
    fi
    
    # 安装 Nginx
    if ! command_exists nginx; then
        log_info "安装 Nginx..."
        apt-get install -y nginx
    fi
    
    log_success "系统依赖安装完成"
}

# 安装后端依赖
install_backend_deps() {
    log_info "安装后端依赖..."
    cd "$SCRIPT_DIR/backend"
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级 pip
    pip install --upgrade pip
    
    # 安装依赖
    pip install -r requirements.txt
    
    # 安装 gunicorn
    pip install gunicorn
    
    log_success "后端依赖安装完成"
    cd "$SCRIPT_DIR"
}

# 构建前端
build_frontend() {
    log_info "构建前端生产版本..."
    cd "$SCRIPT_DIR/frontend"
    
    # 安装依赖
    npm install
    
    # 构建生产版本
    npm run build
    
    log_success "前端构建完成"
    cd "$SCRIPT_DIR"
}

# 配置Nginx
configure_nginx() {
    log_info "配置 Nginx..."
    
    # 获取服务器IP
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    # 创建Nginx配置文件
    cat > /etc/nginx/sites-available/stock << EOF
server {
    listen ${FRONTEND_PORT};
    server_name ${SERVER_IP};
    
    # 前端静态文件
    location / {
        root ${SCRIPT_DIR}/frontend/dist;
        try_files \$uri \$uri/ /index.html;
        
        # 缓存配置
        add_header Cache-Control "public, max-age=31536000" always;
    }
    
    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:${BACKEND_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;
    
    # 日志
    access_log /var/log/nginx/stock_access.log;
    error_log /var/log/nginx/stock_error.log;
}
EOF
    
    # 启用站点
    ln -sf /etc/nginx/sites-available/stock /etc/nginx/sites-enabled/stock
    
    # 删除默认站点（如果存在）
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试配置
    nginx -t
    
    # 重启Nginx
    systemctl restart nginx
    systemctl enable nginx
    
    log_success "Nginx 配置完成"
    log_info "访问地址: http://${SERVER_IP}"
}

# 创建systemd服务
create_systemd_service() {
    log_info "创建 systemd 服务..."
    
    # 后端服务
    cat > /etc/systemd/system/stock-backend.service << EOF
[Unit]
Description=Stock Monitor Backend API
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=${SCRIPT_DIR}/backend
Environment="PATH=${SCRIPT_DIR}/backend/venv/bin"
ExecStart=${SCRIPT_DIR}/backend/venv/bin/gunicorn \\
    --bind ${BACKEND_HOST}:${BACKEND_PORT} \\
    --workers ${BACKEND_WORKERS} \\
    --timeout 120 \\
    --access-logfile ${SCRIPT_DIR}/logs/gunicorn_access.log \\
    --error-logfile ${SCRIPT_DIR}/logs/gunicorn_error.log \\
    app:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
KillSignal=SIGQUIT
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
    
    log_success "systemd 服务创建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 创建日志目录
    mkdir -p "$SCRIPT_DIR/logs"
    
    # 重载 systemd
    systemctl daemon-reload
    
    # 启动并启用后端服务
    systemctl enable stock-backend
    systemctl restart stock-backend
    
    # 检查服务状态
    sleep 2
    if systemctl is-active --quiet stock-backend; then
        log_success "后端服务启动成功"
    else
        log_error "后端服务启动失败"
        systemctl status stock-backend
        exit 1
    fi
    
    # 确保Nginx运行
    systemctl restart nginx
    
    if systemctl is-active --quiet nginx; then
        log_success "Nginx 服务运行正常"
    else
        log_error "Nginx 服务启动失败"
        systemctl status nginx
        exit 1
    fi
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    if systemctl is-active --quiet stock-backend; then
        systemctl stop stock-backend
        log_info "后端服务已停止"
    fi
    
    if systemctl is-active --quiet nginx; then
        systemctl stop nginx
        log_info "Nginx 服务已停止"
    fi
}

# 检查服务状态
check_status() {
    echo ""
    log_info "服务状态检查..."
    echo ""
    
    # 后端服务状态
    if systemctl is-active --quiet stock-backend; then
        echo -e "${GREEN}✓${NC} 后端服务: ${GREEN}运行中${NC}"
        systemctl status stock-backend --no-pager -l | grep -E "Active|Main PID|Memory"
    else
        echo -e "${RED}✗${NC} 后端服务: ${RED}未运行${NC}"
    fi
    
    echo ""
    
    # Nginx状态
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✓${NC} Nginx 服务: ${GREEN}运行中${NC}"
        systemctl status nginx --no-pager -l | grep -E "Active|Main PID|Memory"
    else
        echo -e "${RED}✗${NC} Nginx 服务: ${RED}未运行${NC}"
    fi
    
    echo ""
    
    # 端口监听检查
    log_info "端口监听状态:"
    netstat -tlnp | grep -E ":${BACKEND_PORT}|:${FRONTEND_PORT}" || true
    
    echo ""
    
    # 访问地址
    SERVER_IP=$(hostname -I | awk '{print $1}')
    log_info "访问地址: http://${SERVER_IP}"
}

# 查看日志
view_logs() {
    echo ""
    log_info "最近日志 (按 Ctrl+C 退出)..."
    echo ""
    
    case "${1:-backend}" in
        backend)
            tail -f "$SCRIPT_DIR/logs/gunicorn_error.log"
            ;;
        access)
            tail -f "$SCRIPT_DIR/logs/gunicorn_access.log"
            ;;
        nginx-access)
            tail -f /var/log/nginx/stock_access.log
            ;;
        nginx-error)
            tail -f /var/log/nginx/stock_error.log
            ;;
        *)
            log_error "未知的日志类型: $1"
            echo "可用选项: backend, access, nginx-access, nginx-error"
            exit 1
            ;;
    esac
}

# 显示帮助信息
show_help() {
    cat << EOF
股票监控系统 - 生产环境部署脚本

用法: $0 [命令]

命令:
  deploy      完整部署（默认）- 安装依赖、构建、配置并启动
  start       启动服务
  stop        停止服务
  restart     重启服务
  status      查看服务状态
  logs        查看日志 [backend|access|nginx-access|nginx-error]
  rebuild     重新构建前端
  help        显示此帮助信息

示例:
  $0 deploy              # 完整部署
  $0 start               # 启动服务
  $0 status              # 查看状态
  $0 logs backend        # 查看后端日志
  $0 logs nginx-error    # 查看Nginx错误日志

EOF
}

# 主函数
main() {
    case "${1:-deploy}" in
        deploy)
            check_root
            log_info "开始生产环境部署..."
            install_system_dependencies
            install_backend_deps
            build_frontend
            configure_nginx
            create_systemd_service
            start_services
            echo ""
            echo "================================"
            log_success "部署完成！"
            echo "================================"
            echo ""
            SERVER_IP=$(hostname -I | awk '{print $1}')
            echo "访问地址: ${GREEN}http://${SERVER_IP}${NC}"
            echo ""
            echo "常用命令:"
            echo "  查看状态: sudo ./start_production.sh status"
            echo "  查看日志: sudo ./start_production.sh logs"
            echo "  重启服务: sudo ./start_production.sh restart"
            echo ""
            ;;
        start)
            check_root
            start_services
            check_status
            ;;
        stop)
            check_root
            stop_services
            ;;
        restart)
            check_root
            stop_services
            sleep 2
            start_services
            check_status
            ;;
        status)
            check_status
            ;;
        logs)
            view_logs "$2"
            ;;
        rebuild)
            check_root
            build_frontend
            systemctl restart nginx
            log_success "前端重新构建完成"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"

