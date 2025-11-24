# 快速开始指南

## 🚀 一键启动（Windows）

双击运行 `start.bat` 文件即可自动启动前后端服务。

## 📦 手动启动

### 方式一：分别启动

**1. 启动后端（在第一个终端）**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**2. 启动前端（在第二个终端）**
```bash
cd frontend
npm install
npm run dev
```

### 方式二：使用启动脚本

**Windows:**
```bash
start.bat
```

## 🌐 访问应用

启动成功后，在浏览器中打开：
```
http://localhost:3000
```

## 📋 系统要求

- **Python**: 3.7 或更高版本
- **Node.js**: 14.0 或更高版本
- **npm**: 6.0 或更高版本

## ⚙️ 端口配置

- **后端端口**: 5000（可在 `backend/app.py` 修改）
- **前端端口**: 3000（可在 `frontend/vite.config.js` 修改）

## 🔧 环境变量配置

在 `frontend` 目录下创建 `.env` 文件（或复制 `.env.example`）：

```bash
# 自动刷新间隔时间（秒），默认20秒
VITE_AUTO_REFRESH_INTERVAL=20
```

**可配置项：**
- `VITE_AUTO_REFRESH_INTERVAL`: 自动刷新间隔（秒）
  - 默认值：20
  - 建议范围：10-60秒

**注意：** 修改 `.env` 文件后需要重启前端服务才能生效。

## 🎯 主要功能

1. **实时监控**: 关键指标卡片展示
2. **竞价数据**: 涨幅和跌幅排行
3. **连板数据**: 支持历史日期查询
4. **热门概念**: 可视化进度条展示
5. **自动刷新**: 每20秒自动更新数据

## 🔧 常见问题

### 1. 后端启动失败
- 检查 Python 版本是否正确
- 确保安装了所有依赖：`pip install -r requirements.txt`
- 检查 5000 端口是否被占用

### 2. 前端启动失败
- 检查 Node.js 版本是否正确
- 删除 `node_modules` 文件夹，重新运行 `npm install`
- 检查 3000 端口是否被占用

### 3. 无法获取数据
- 确保后端服务正在运行
- 检查网络连接
- 查看浏览器控制台和后端日志

### 4. 跨域问题
- 确保后端已安装 `flask-cors`
- 检查 Vite 代理配置是否正确

## 📝 开发建议

### 修改 API 端口
编辑 `frontend/vite.config.js`:
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',  // 修改为你的后端地址
      changeOrigin: true
    }
  }
}
```

### 修改自动刷新时间
编辑 `frontend/src/components/StockMonitor.vue`:
```javascript
const countdown = ref(20)  // 修改刷新间隔（秒）
```

### 添加新的 API 接口
1. 在 `backend/app.py` 中添加路由
2. 在前端组件中使用 `axios` 调用

## 📚 更多文档

详细文档请参阅 `README_VUE.md`

## 💡 技术栈

- 后端：Flask + Python
- 前端：Vue 3 + Naive UI + Vite
- HTTP 客户端：Axios

## 🎨 界面预览

应用包含以下主要模块：
- 📊 关键指标卡片
- 📈 竞价涨幅排行
- 📉 竞价跌幅排行  
- 🏆 连板排行榜
- 🔥 热门概念
- 📊 详细连板数据

祝使用愉快！ 🎉

