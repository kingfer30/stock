# 前端环境变量配置说明

## 📝 配置文件

在 `frontend` 目录下的 `.env` 文件中配置环境变量。

## 🔧 可用配置项

### VITE_AUTO_REFRESH_INTERVAL

**说明：** 自动刷新间隔时间（秒）

**默认值：** 20

**推荐范围：** 10-60 秒

**示例：**
```bash
# 设置为30秒自动刷新一次
VITE_AUTO_REFRESH_INTERVAL=30
```

## 📋 使用步骤

### 1. 创建配置文件

```bash
cd frontend
cp .env.example .env
```

### 2. 编辑配置

使用任意文本编辑器打开 `.env` 文件，修改配置值：

```bash
# 修改为你想要的刷新间隔
VITE_AUTO_REFRESH_INTERVAL=15
```

### 3. 重启前端服务

⚠️ **重要：** 修改 `.env` 文件后必须重启前端开发服务器才能生效。

```bash
# 停止当前服务（Ctrl+C）
# 然后重新启动
npm run dev
```

## 💡 提示

1. **`.env` 文件不会被提交到 Git**
   - 这个文件已被 `.gitignore` 忽略
   - 每个开发者可以有自己的本地配置

2. **`.env.example` 是配置模板**
   - 这个文件会被提交到 Git
   - 用于告诉其他开发者有哪些配置项可用

3. **Vite 环境变量规则**
   - 必须以 `VITE_` 开头
   - 只有以 `VITE_` 开头的变量才会暴露给客户端代码
   - 通过 `import.meta.env.VITE_XXX` 访问

## 🎯 配置示例

### 开发环境（快速刷新）
```bash
VITE_AUTO_REFRESH_INTERVAL=10
```

### 生产环境（节省资源）
```bash
VITE_AUTO_REFRESH_INTERVAL=30
```

### 演示环境（标准刷新）
```bash
VITE_AUTO_REFRESH_INTERVAL=20
```

## 🔍 验证配置

启动前端服务后，可以在浏览器控制台中查看当前配置：

```javascript
console.log(import.meta.env.VITE_AUTO_REFRESH_INTERVAL)
```

## 📚 更多信息

- [Vite 环境变量文档](https://vitejs.dev/guide/env-and-mode.html)
- 项目主文档：`../README_VUE.md`
- 快速开始：`../QUICKSTART.md`

