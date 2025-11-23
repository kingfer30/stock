# 股市实时监控看板 - Vue + Naive UI 版本

这是使用 Vue 3 + Naive UI + Flask 重构的股市监控看板应用。

## 项目结构

```
stock/
├── backend/                 # Flask 后端 API
│   ├── app.py              # 主应用文件
│   └── requirements.txt    # Python 依赖
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── components/    # Vue 组件
│   │   │   ├── StockMonitor.vue
│   │   │   └── MetricCard.vue
│   │   ├── App.vue        # 主组件
│   │   └── main.js        # 入口文件
│   ├── index.html         # HTML 模板
│   ├── package.json       # Node.js 依赖
│   └── vite.config.js     # Vite 配置
└── README_VUE.md          # 本文件
```

## 技术栈

### 后端
- **Flask**: 轻量级 Python Web 框架
- **Flask-CORS**: 处理跨域请求
- **Requests**: HTTP 请求库

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **Naive UI**: 优雅的 Vue 3 组件库
- **Vite**: 下一代前端构建工具
- **Axios**: HTTP 客户端

## 安装和运行

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
cd backend
python app.py
```

后端将运行在 `http://localhost:5000`

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动前端开发服务器

```bash
cd frontend
npm run dev
```

前端将运行在 `http://localhost:3000`

## API 接口说明

### 1. 获取交易日期列表
- **URL**: `/api/trade-dates`
- **方法**: `GET`
- **响应**: 
```json
{
  "success": true,
  "data": [
    {"raw": "20251122", "display": "2025-11-22"},
    ...
  ]
}
```

### 2. 获取市场数据
- **URL**: `/api/market-data`
- **方法**: `POST`
- **请求体**:
```json
{
  "selected_date": "20251122"  // 可选，不传则为当前交易日
}
```
- **响应**: 返回市场主数据、竞价涨跌幅数据

### 3. 获取连板数据
- **URL**: `/api/lianban-data`
- **方法**: `POST`
- **请求体**:
```json
{
  "selected_date": "20251122",  // 可选
  "query_date": "20251122"      // 查询日期
}
```
- **响应**: 返回连板股票列表

### 4. 获取分时最大成交量
- **URL**: `/api/max-volume`
- **方法**: `POST`
- **请求体**:
```json
{
  "stock_name": "长安汽车",
  "query_date": "20251122"
}
```
- **响应**: 
```json
{
  "success": true,
  "volume": "123.45"
}
```

## 功能特性

✅ **实时数据监控**: 实时获取股市数据，支持自动刷新（20秒）  
✅ **历史数据查询**: 支持选择历史交易日期查询  
✅ **多维度展示**: 包含竞价涨跌幅、连板排行、热门概念等多个维度  
✅ **响应式设计**: 适配各种屏幕尺寸  
✅ **优雅的UI**: 使用 Naive UI 组件库，界面美观易用  
✅ **异步加载**: 分时最大成交量数据异步加载，不阻塞主界面  

## 相比 Streamlit 的优势

1. **更好的用户体验**: 
   - 无需等待页面重新加载
   - 流畅的动画和交互效果
   - 更快的响应速度

2. **更灵活的定制**: 
   - 完全控制 UI 样式和布局
   - 可以添加复杂的交互逻辑
   - 易于集成第三方库

3. **更好的性能**: 
   - 前后端分离，减少服务器压力
   - 数据缓存和增量更新
   - 异步加载，提高加载速度

4. **易于部署**: 
   - 前端可以部署到任何静态托管服务
   - 后端可以独立部署和扩展

## 构建生产版本

### 构建前端
```bash
cd frontend
npm run build
```

构建后的文件将在 `frontend/dist` 目录中。

### 部署
1. 将 `frontend/dist` 目录部署到任何静态托管服务（Nginx, Vercel, Netlify 等）
2. 将后端部署到云服务器（Railway, Render, 腾讯云等）
3. 配置前端的 API 地址指向后端服务

## 开发建议

- 使用 Vue DevTools 进行调试
- 后端 API 可以添加缓存机制提高性能
- 考虑添加 WebSocket 实现真正的实时推送
- 可以添加用户认证和数据持久化功能

## 许可证

MIT License

