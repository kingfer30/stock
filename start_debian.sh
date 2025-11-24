#!/bin/bash

# 股票监控系统 - Debian一键启动脚本
# 适用于 Debian/Ubuntu 系统

set -e  # 遇到错误立即退出

echo "================================"
echo "股票监控系统 - 启动脚本"
echo "================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

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

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查并安装系统依赖
check_system_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查 Python3
    if ! command_exists python3; then
        log_warn "未找到 Python3，正在安装..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
    else
        log_info "Python3 已安装: $(python3 --version)"
    fi
    
    # 检查 Node.js
    if ! command_exists node; then
        log_warn "未找到 Node.js，正在安装..."
        # 安装 Node.js 18.x
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    else
        log_info "Node.js 已安装: $(node --version)"
    fi
    
    # 检查 npm
    if ! command_exists npm; then
        log_warn "未找到 npm，正在安装..."
        sudo apt-get install -y npm
    else
        log_info "npm 已安装: $(npm --version)"
    fi
}

# 安装后端依赖
install_backend_deps() {
    log_info "安装后端依赖..."
    cd "$SCRIPT_DIR/backend"
    
    # 创建虚拟环境（如果不存在）
    if [ ! -d "venv" ]; then
        log_info "创建 Python 虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级 pip
    pip install --upgrade pip
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        log_error "未找到 requirements.txt"
        exit 1
    fi
    
    log_info "后端依赖安装完成"
    cd "$SCRIPT_DIR"
}

# 安装前端依赖
install_frontend_deps() {
    log_info "安装前端依赖..."
    cd "$SCRIPT_DIR/frontend"
    
    if [ -f "package.json" ]; then
        npm install
    else
        log_error "未找到 package.json"
        exit 1
    fi
    
    log_info "前端依赖安装完成"
    cd "$SCRIPT_DIR"
}

# 创建环境变量文件
create_env_file() {
    if [ ! -f "$SCRIPT_DIR/frontend/.env" ]; then
        log_info "创建前端环境变量文件..."
        cat > "$SCRIPT_DIR/frontend/.env" << EOF
# 自动刷新间隔（秒）
VITE_AUTO_REFRESH_INTERVAL=20
EOF
        log_info "已创建 frontend/.env 文件"
    fi
}

# 启动后端服务
start_backend() {
    log_info "启动后端服务..."
    cd "$SCRIPT_DIR/backend"
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 后台启动 Flask
    nohup python app.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../logs/backend.pid
    
    log_info "后端服务已启动 (PID: $BACKEND_PID)"
    log_info "后端日志: logs/backend.log"
    log_info "后端地址: http://localhost:5000"
    
    cd "$SCRIPT_DIR"
}

# 启动前端服务
start_frontend() {
    log_info "启动前端服务..."
    cd "$SCRIPT_DIR/frontend"
    
    # 后台启动 Vite
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    
    log_info "前端服务已启动 (PID: $FRONTEND_PID)"
    log_info "前端日志: logs/frontend.log"
    log_info "前端地址: http://localhost:3000"
    
    cd "$SCRIPT_DIR"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    if [ -f "logs/backend.pid" ]; then
        BACKEND_PID=$(cat logs/backend.pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill $BACKEND_PID
            log_info "后端服务已停止 (PID: $BACKEND_PID)"
        fi
        rm -f logs/backend.pid
    fi
    
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill $FRONTEND_PID
            log_info "前端服务已停止 (PID: $FRONTEND_PID)"
        fi
        rm -f logs/frontend.pid
    fi
}

# 检查服务状态
check_status() {
    echo ""
    log_info "检查服务状态..."
    
    if [ -f "logs/backend.pid" ]; then
        BACKEND_PID=$(cat logs/backend.pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} 后端服务运行中 (PID: $BACKEND_PID)"
        else
            echo -e "${RED}✗${NC} 后端服务未运行"
        fi
    else
        echo -e "${RED}✗${NC} 后端服务未运行"
    fi
    
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} 前端服务运行中 (PID: $FRONTEND_PID)"
        else
            echo -e "${RED}✗${NC} 前端服务未运行"
        fi
    else
        echo -e "${RED}✗${NC} 前端服务未运行"
    fi
}

# 主函数
main() {
    # 创建日志目录
    mkdir -p logs
    
    case "${1:-start}" in
        start)
            log_info "开始启动服务..."
            check_system_dependencies
            install_backend_deps
            install_frontend_deps
            create_env_file
            stop_services  # 先停止已存在的服务
            start_backend
            sleep 2
            start_frontend
            echo ""
            echo "================================"
            log_info "启动完成！"
            echo "================================"
            echo ""
            echo "访问地址:"
            echo "  前端: http://localhost:3000"
            echo "  后端: http://localhost:5000"
            echo ""
            echo "查看日志:"
            echo "  后端: tail -f logs/backend.log"
            echo "  前端: tail -f logs/frontend.log"
            echo ""
            echo "停止服务: ./start_debian.sh stop"
            echo "查看状态: ./start_debian.sh status"
            echo ""
            ;;
        stop)
            stop_services
            log_info "服务已停止"
            ;;
        restart)
            stop_services
            sleep 2
            start_backend
            sleep 2
            start_frontend
            log_info "服务已重启"
            ;;
        status)
            check_status
            ;;
        install)
            log_info "仅安装依赖..."
            check_system_dependencies
            install_backend_deps
            install_frontend_deps
            create_env_file
            log_info "依赖安装完成"
            ;;
        *)
            echo "用法: $0 {start|stop|restart|status|install}"
            echo ""
            echo "命令说明:"
            echo "  start   - 启动服务（默认）"
            echo "  stop    - 停止服务"
            echo "  restart - 重启服务"
            echo "  status  - 查看服务状态"
            echo "  install - 仅安装依赖"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"

