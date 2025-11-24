#!/bin/bash

# 股票监控系统 - 简化生产环境部署脚本
# 不使用Nginx，直接通过 IP:端口 访问

set -e  # 遇到错误立即退出

echo "================================"
echo "股票监控系统 - 简化生产部署"
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
BACKEND_PORT="8000"
BACKEND_WORKERS="4"

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

# 检查并安装系统依赖
install_system_dependencies() {
    log_info "检查并安装系统依赖..."
    
    # 检查是否为root
    if [ "$EUID" -eq 0 ]; then
        # root用户，可以安装系统包
        apt-get update || true
        
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
    else
        # 非root用户，检查依赖是否已安装
        if ! command_exists python3; then
            log_error "未找到 Python3，请先安装: sudo apt-get install python3 python3-pip python3-venv"
            exit 1
        fi
        
        if ! command_exists node; then
            log_error "未找到 Node.js，请先安装: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash - && sudo apt-get install -y nodejs"
            exit 1
        fi
    fi
    
    log_success "系统依赖检查完成"
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
    
    # 将构建产物移动到backend/static目录
    log_info "部署前端静态文件..."
    rm -rf "$SCRIPT_DIR/backend/static"
    mkdir -p "$SCRIPT_DIR/backend/static"
    cp -r dist/* "$SCRIPT_DIR/backend/static/"
    
    log_success "前端构建并部署完成"
    cd "$SCRIPT_DIR"
}

# 创建systemd服务
create_systemd_service() {
    log_info "创建 systemd 服务..."
    
    # 检查是否为root
    if [ "$EUID" -ne 0 ]; then
        log_warn "非root用户，跳过systemd服务创建"
        log_info "如需开机自启和自动重启，请以root权限运行"
        return
    fi
    
    # 后端服务
    cat > /etc/systemd/system/stock-app.service << EOF
[Unit]
Description=Stock Monitor Application
After=network.target

[Service]
Type=notify
User=${SUDO_USER:-$USER}
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
    
    # 检查是否使用systemd
    if [ "$EUID" -eq 0 ] && command_exists systemctl; then
        # 使用systemd管理
        systemctl daemon-reload
        systemctl enable stock-app
        systemctl restart stock-app
        
        sleep 2
        if systemctl is-active --quiet stock-app; then
            log_success "服务启动成功（systemd管理）"
        else
            log_error "服务启动失败"
            systemctl status stock-app
            exit 1
        fi
    else
        # 手动后台启动
        cd "$SCRIPT_DIR/backend"
        source venv/bin/activate
        
        # 停止旧进程
        if [ -f "$SCRIPT_DIR/logs/app.pid" ]; then
            OLD_PID=$(cat "$SCRIPT_DIR/logs/app.pid")
            if ps -p $OLD_PID > /dev/null 2>&1; then
                kill $OLD_PID
                sleep 2
            fi
        fi
        
        # 启动新进程
        nohup gunicorn \
            --bind ${BACKEND_HOST}:${BACKEND_PORT} \
            --workers ${BACKEND_WORKERS} \
            --timeout 120 \
            --access-logfile "$SCRIPT_DIR/logs/gunicorn_access.log" \
            --error-logfile "$SCRIPT_DIR/logs/gunicorn_error.log" \
            --daemon \
            --pid "$SCRIPT_DIR/logs/app.pid" \
            app:app
        
        sleep 2
        if [ -f "$SCRIPT_DIR/logs/app.pid" ]; then
            PID=$(cat "$SCRIPT_DIR/logs/app.pid")
            if ps -p $PID > /dev/null 2>&1; then
                log_success "服务启动成功 (PID: $PID)"
            else
                log_error "服务启动失败"
                exit 1
            fi
        fi
        
        cd "$SCRIPT_DIR"
    fi
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    if [ "$EUID" -eq 0 ] && command_exists systemctl; then
        # 使用systemd停止
        if systemctl is-active --quiet stock-app; then
            systemctl stop stock-app
            log_info "服务已停止（systemd）"
        fi
    else
        # 手动停止
        if [ -f "$SCRIPT_DIR/logs/app.pid" ]; then
            PID=$(cat "$SCRIPT_DIR/logs/app.pid")
            if ps -p $PID > /dev/null 2>&1; then
                kill $PID
                log_info "服务已停止 (PID: $PID)"
            fi
            rm -f "$SCRIPT_DIR/logs/app.pid"
        else
            # 尝试通过进程名停止
            pkill -f "gunicorn.*app:app" && log_info "服务已停止" || log_warn "未找到运行中的服务"
        fi
    fi
}

# 检查服务状态
check_status() {
    echo ""
    log_info "服务状态检查..."
    echo ""
    
    if [ "$EUID" -eq 0 ] && command_exists systemctl && systemctl list-units --full -all | grep -q stock-app.service; then
        # 使用systemd检查
        if systemctl is-active --quiet stock-app; then
            echo -e "${GREEN}✓${NC} 服务状态: ${GREEN}运行中${NC}"
            systemctl status stock-app --no-pager -l | grep -E "Active|Main PID|Memory"
        else
            echo -e "${RED}✗${NC} 服务状态: ${RED}未运行${NC}"
        fi
    else
        # 手动检查
        if [ -f "$SCRIPT_DIR/logs/app.pid" ]; then
            PID=$(cat "$SCRIPT_DIR/logs/app.pid")
            if ps -p $PID > /dev/null 2>&1; then
                echo -e "${GREEN}✓${NC} 服务状态: ${GREEN}运行中${NC} (PID: $PID)"
                ps -p $PID -o pid,ppid,cmd,%cpu,%mem
            else
                echo -e "${RED}✗${NC} 服务状态: ${RED}未运行${NC} (PID文件存在但进程不存在)"
            fi
        else
            # 尝试查找gunicorn进程
            if pgrep -f "gunicorn.*app:app" > /dev/null; then
                echo -e "${YELLOW}⚠${NC} 服务状态: ${YELLOW}运行中${NC} (但无PID文件)"
                ps aux | grep -E "gunicorn.*app:app" | grep -v grep
            else
                echo -e "${RED}✗${NC} 服务状态: ${RED}未运行${NC}"
            fi
        fi
    fi
    
    echo ""
    
    # 端口监听检查
    log_info "端口监听状态:"
    if command_exists netstat; then
        netstat -tlnp 2>/dev/null | grep ":${BACKEND_PORT}" || echo "端口 ${BACKEND_PORT} 未监听"
    elif command_exists ss; then
        ss -tlnp 2>/dev/null | grep ":${BACKEND_PORT}" || echo "端口 ${BACKEND_PORT} 未监听"
    else
        log_warn "无法检查端口状态（netstat或ss命令不可用）"
    fi
    
    echo ""
    
    # 访问地址
    SERVER_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")
    log_info "访问地址: http://${SERVER_IP}:${BACKEND_PORT}"
}

# 查看日志
view_logs() {
    echo ""
    log_info "最近日志 (按 Ctrl+C 退出)..."
    echo ""
    
    case "${1:-error}" in
        error)
            tail -f "$SCRIPT_DIR/logs/gunicorn_error.log"
            ;;
        access)
            tail -f "$SCRIPT_DIR/logs/gunicorn_access.log"
            ;;
        *)
            log_error "未知的日志类型: $1"
            echo "可用选项: error, access"
            exit 1
            ;;
    esac
}

# 配置防火墙
configure_firewall() {
    if [ "$EUID" -ne 0 ]; then
        log_warn "非root用户，跳过防火墙配置"
        return
    fi
    
    log_info "配置防火墙..."
    
    if command_exists ufw; then
        # 使用UFW
        ufw allow ${BACKEND_PORT}/tcp
        log_success "UFW: 已允许端口 ${BACKEND_PORT}"
    elif command_exists iptables; then
        # 使用iptables
        iptables -A INPUT -p tcp --dport ${BACKEND_PORT} -j ACCEPT
        log_success "iptables: 已允许端口 ${BACKEND_PORT}"
    else
        log_warn "未找到防火墙工具，请手动配置"
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
股票监控系统 - 简化生产环境部署脚本

用法: $0 [命令]

命令:
  deploy      完整部署（默认）- 安装依赖、构建、配置并启动
  start       启动服务
  stop        停止服务
  restart     重启服务
  status      查看服务状态
  logs        查看日志 [error|access]
  rebuild     重新构建前端
  firewall    配置防火墙（需要root）
  help        显示此帮助信息

示例:
  $0 deploy              # 完整部署
  $0 start               # 启动服务
  $0 status              # 查看状态
  $0 logs error          # 查看错误日志
  sudo $0 firewall       # 配置防火墙

访问地址: http://your-server-ip:${BACKEND_PORT}

EOF
}

# 主函数
main() {
    case "${1:-deploy}" in
        deploy)
            log_info "开始简化生产环境部署..."
            install_system_dependencies
            install_backend_deps
            build_frontend
            create_systemd_service
            start_services
            echo ""
            echo "================================"
            log_success "部署完成！"
            echo "================================"
            echo ""
            SERVER_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")
            echo "访问地址: ${GREEN}http://${SERVER_IP}:${BACKEND_PORT}${NC}"
            echo ""
            echo "常用命令:"
            echo "  查看状态: $0 status"
            echo "  查看日志: $0 logs"
            echo "  重启服务: $0 restart"
            echo "  配置防火墙: sudo $0 firewall"
            echo ""
            log_warn "重要: 请确保防火墙允许端口 ${BACKEND_PORT}"
            echo ""
            ;;
        start)
            start_services
            check_status
            ;;
        stop)
            stop_services
            ;;
        restart)
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
            build_frontend
            stop_services
            sleep 1
            start_services
            log_success "前端重新构建完成"
            ;;
        firewall)
            configure_firewall
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

