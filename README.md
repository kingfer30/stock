# 股市实时监控看板

基于 Vue 3 + Naive UI + Flask 的股票实时监控系统。

## 技术栈

- **前端**: Vue 3 + Vite + Naive UI + Axios
- **后端**: Python Flask + Flask-CORS
- **数据源**: 问财AI、同花顺数据接口

## 功能特性

- ✅ 股市实时数据监控
- ✅ 竞价涨幅和跌幅数据
- ✅ 连板排行榜
- ✅ 热门概念展示
- ✅ 连板数据详情（含次日竞价数据）
- ✅ 自动刷新功能（可配置间隔）
- ✅ 异步加载最大成交量和次日竞价数据
- ✅ 数据导出功能（CSV格式）
- ✅ 响应式布局，支持多种设备

## 快速开始

### 方式一：简化生产部署 ⭐ 推荐

**适用场景**: 通过 IP:端口 直接访问，无需域名

```bash
# 赋予执行权限
chmod +x start_production_simple.sh

# 一键部署
./start_production_simple.sh deploy
```

访问地址: `http://your-server-ip:8000`

特性：
- ✅ 简单快速，一键部署
- ✅ 无需Nginx和域名
- ✅ 支持外网访问
- ✅ Gunicorn生产级服务器
- ✅ Vue生产模式构建
- ✅ 可选systemd服务管理

详细说明请查看 [简化生产部署指南](PRODUCTION_SIMPLE.md)

### 方式二：完整生产部署 🚀 企业级

**适用场景**: 需要域名、HTTPS、高并发

```bash
# 赋予执行权限
chmod +x start_production.sh

# 一键部署（需要root权限）
sudo ./start_production.sh deploy
```

特性：
- ✅ Nginx反向代理和静态文件服务
- ✅ 支持域名和HTTPS
- ✅ 高性能和高并发支持
- ✅ 完善的缓存和压缩
- ✅ systemd服务管理
- ✅ 生产级安全性

详细说明请查看 [完整生产环境部署指南](PRODUCTION_DEPLOY.md)

### 方式三：开发环境 - Debian/Ubuntu

适用于开发和测试：

```bash
# 赋予执行权限
chmod +x start_debian.sh

# 一键启动
./start_debian.sh
```

详细说明请查看 [Debian 部署指南](DEBIAN_INSTALL.md)

### 方式四：Windows 一键启动

双击运行 `start.bat` 文件，或在命令行执行：

```cmd
start.bat
```

详细说明请查看 [快速入门指南](QUICKSTART.md)

### 方式五：打包为EXE（Windows）

**适用场景**: 无需安装依赖，双击即可运行

```cmd
# 一键打包
build_exe.bat

# 或使用高级版本
build_exe_advanced.bat
```

生成文件: `股票监控系统.exe` (40-60MB)

特性：
- ✅ 单文件，无需安装
- ✅ 自动打开浏览器
- ✅ 包含所有依赖
- ✅ 易于分发

详细说明请查看 [EXE打包指南](BUILD_EXE_README.md)

### 方式六：手动启动

#### 后端启动

```bash
cd backend
pip install -r requirements.txt
python app.py
```

后端服务地址: http://localhost:5000

#### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端服务地址: http://localhost:3000

## 部署方式对比

| 特性 | EXE打包 | 简化生产 | 完整生产 | 开发环境 | Windows开发 |
|------|---------|---------|---------|---------|------------|
| 脚本 | `build_exe.bat` | `start_production_simple.sh` | `start_production.sh` | `start_debian.sh` | `start.bat` |
| 平台 | Windows | Linux | Linux | Linux | Windows |
| Web服务器 | Flask | Gunicorn | Nginx + Gunicorn | Vite Dev | Vite Dev |
| 前端模式 | Build | Build | Build | Dev | Dev |
| 安装依赖 | ❌ 无需 | ✅ 需要 | ✅ 需要 | ✅ 需要 | ✅ 需要 |
| 外网访问 | ❌ | ✅ 支持 | ✅ 支持 | ❌ | ❌ |
| HTTPS | ❌ | ❌ | ✅ 支持 | ❌ | ❌ |
| 性能 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 并发能力 | 10-30 | 50-100 | 200+ | 10-50 | 10-50 |
| 文件大小 | 40-60MB | - | - | - | - |
| 启动速度 | 2-3秒 | 快 | 快 | 快 | 快 |
| 分发难度 | ⭐ 极简 | ⭐⭐ 简单 | ⭐⭐⭐ 中等 | ⭐ 简单 | ⭐ 简单 |
| 适用场景 | 演示分发 | 小型生产 | 企业生产 | 开发测试 | 本地开发 |

**推荐选择**：
- 📦 **演示/分发给非技术人员**: 使用 `build_exe.bat`
- ⭐ **小型项目/内部系统**: 使用 `start_production_simple.sh`
- 🚀 **企业级项目**: 使用 `start_production.sh`
- 🔧 **开发测试**: 使用 `start_debian.sh` 或 `start.bat`

## 环境配置

前端环境变量配置文件 `frontend/.env`:

```env
# 自动刷新间隔（秒）
VITE_AUTO_REFRESH_INTERVAL=20
```

## 项目结构

```
stock/
├── backend/                # 后端目录
│   ├── routes/            # API 路由
│   │   ├── trade_dates.py      # 交易日期接口
│   │   ├── market_data.py      # 市场数据接口
│   │   ├── lianban_data.py     # 连板数据接口
│   │   ├── max_volume.py       # 最大成交量接口
│   │   └── next_day_jingjia.py # 次日竞价接口
│   ├── utils.py           # 工具函数
│   ├── app.py             # Flask 应用入口
│   └── requirements.txt   # Python 依赖
├── frontend/              # 前端目录
│   ├── src/
│   │   ├── components/         # Vue 组件
│   │   │   ├── StockMonitor.vue    # 主监控组件
│   │   │   ├── MetricCard.vue      # 指标卡片组件
│   │   │   └── tables/             # 表格组件
│   │   ├── App.vue        # 根组件
│   │   └── main.js        # 应用入口
│   ├── package.json       # Node.js 依赖
│   └── vite.config.js     # Vite 配置
├── start.bat              # Windows 启动脚本
├── start_debian.sh        # Debian/Ubuntu 启动脚本
├── README.md              # 项目说明
├── QUICKSTART.md          # Windows 快速入门
└── DEBIAN_INSTALL.md      # Debian 部署指南

```

## 使用说明

### 主要功能

1. **竞价涨幅**: 显示当日竞价阶段涨幅前十的股票
2. **竞价跌幅**: 显示当日竞价阶段跌幅前十的股票
3. **连板排行**: 显示连续涨停板数最多的股票排行
4. **热门概念**: 展示当前市场热门概念板块
5. **连板数据**: 详细的连板股票数据，包括：
   - 基础信息（代码、名称、连板数等）
   - 最大1分钟成交量
   - 次日竞价数据（涨幅、成交额、成交量）
   - 是否晋级判断

### 数据导出

在"连板数据"标签页中，点击"📊 导出表格"按钮即可导出当前数据为 CSV 文件，可用 Excel 打开。

### 自动刷新

- 系统默认每 20 秒自动刷新一次数据
- 可通过环境变量 `VITE_AUTO_REFRESH_INTERVAL` 配置刷新间隔
- 可手动关闭自动刷新功能

## 常见问题

### 端口被占用

修改配置：
- 后端端口: 修改 `backend/app.py` 中的 `port=5000`
- 前端端口: 修改 `frontend/vite.config.js` 中的 `port: 3000`

### 数据加载失败

1. 检查网络连接
2. 查看后端日志
3. 确认 API 接口是否正常

### 依赖安装失败

```bash
# 清理缓存
pip cache purge
npm cache clean --force

# 重新安装
pip install -r requirements.txt
npm install
```

## 开发说明

### 添加新接口

1. 在 `backend/routes/` 目录下创建新的路由文件
2. 在 `backend/app.py` 中注册新的蓝图
3. 在前端组件中调用新接口

### 修改样式

前端使用 Naive UI 组件库，可通过以下方式自定义样式：
- 修改组件的 `<style scoped>` 部分
- 使用 `:deep()` 选择器修改组件库样式

## 技术支持

- 查看日志文件定位问题
- 提交 Issue 到项目仓库
- 参考详细文档

## License

MIT