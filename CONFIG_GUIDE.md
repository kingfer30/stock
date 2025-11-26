# 📝 配置文件使用指南

## 📌 概述

打包成EXE后，您可以通过修改 `config.json` 配置文件来自定义应用程序的行为，无需重新编译。

## 🎉 自动创建

**重要**: 配置文件会在首次运行时**自动创建**，无需手动操作！

### 创建时机
1. **程序启动时** - 启动器会自动检测并创建配置文件
2. **首次访问API时** - 如果启动时创建失败，API请求时会再次尝试

### 控制台提示
运行EXE后，您会看到以下提示之一：

```
✅ 已创建配置文件: C:\xxx\股票监控系统\config.json
```
或
```
✅ 配置文件已存在: C:\xxx\股票监控系统\config.json
```

### 验证创建
访问: `http://127.0.0.1:8000/api/config` 查看配置文件路径和内容。

💡 **详细创建机制说明**: 请参考 [CONFIG_AUTO_CREATE.md](./CONFIG_AUTO_CREATE.md)

## 📂 配置文件位置

### 🖥️ EXE打包后
配置文件 `config.json` 位于 **EXE可执行文件的同一目录**下。

```
股票监控系统/
├── 股票监控系统.exe      ← EXE可执行文件
└── config.json          ← 配置文件（与EXE在同一目录）
```

### 🛠️ 开发环境
配置文件 `config.json` 位于 **项目根目录**。

```
E:\Project\stock/
├── backend/
├── frontend/
├── config.json          ← 配置文件
└── ...
```

## ⚙️ 配置项说明

### 📄 config.json 格式

```json
{
  "auto_refresh_interval": 20,
  "max_retries": 3,
  "request_timeout": 10
}
```

### 🔧 配置项详解

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `auto_refresh_interval` | 整数 | `20` | 自动刷新间隔时间（秒） |
| `max_retries` | 整数 | `3` | API请求失败时的最大重试次数 |
| `request_timeout` | 整数 | `10` | API请求超时时间（秒） |

## 🚀 使用步骤

### 方法1：首次运行自动创建

1. **运行EXE程序**
   - 双击 `股票监控系统.exe`
   - 程序会在同目录下自动创建 `config.json`（如果不存在）

2. **修改配置**
   - 关闭程序
   - 用记事本或其他文本编辑器打开 `config.json`
   - 修改配置项（例如将刷新时间改为30秒）：
   ```json
   {
     "auto_refresh_interval": 30,
     "max_retries": 3,
     "request_timeout": 10
   }
   ```
   - 保存文件

3. **重新运行**
   - 再次运行 `股票监控系统.exe`
   - 新的配置会自动生效

### 方法2：手动创建配置文件

1. **创建配置文件**
   - 在EXE同目录下新建文本文件
   - 命名为 `config.json`
   - 复制以下内容：
   ```json
   {
     "auto_refresh_interval": 20,
     "max_retries": 3,
     "request_timeout": 10
   }
   ```

2. **修改配置并保存**

3. **运行程序**

## 💡 常见使用场景

### 场景1：修改自动刷新时间

**需求**：将自动刷新时间从20秒改为60秒

**操作**：
```json
{
  "auto_refresh_interval": 60,
  "max_retries": 3,
  "request_timeout": 10
}
```

### 场景2：关闭自动刷新

**需求**：关闭自动刷新功能

**操作**：
- 方式1：将 `auto_refresh_interval` 设置为一个很大的值（如3600秒=1小时）
- 方式2：在程序界面中关闭"自动刷新"开关

### 场景3：网络较慢，增加超时时间

**需求**：网络环境较差，需要更长的请求超时时间

**操作**：
```json
{
  "auto_refresh_interval": 20,
  "max_retries": 5,
  "request_timeout": 30
}
```

## ⚠️ 注意事项

### ✅ 正确示例

```json
{
  "auto_refresh_interval": 30,
  "max_retries": 3,
  "request_timeout": 10
}
```

### ❌ 错误示例

```json
{
  "auto_refresh_interval": "30",  ❌ 值应该是数字，不要加引号
  "max_retries": 3.5,             ❌ 应该是整数，不要用小数
  "request_timeout": 10,          ❌ 最后一项后面不要加逗号
}
```

### 📋 JSON格式要求

1. ✅ **使用英文符号**：`{}` `[]` `:` `,` 等
2. ✅ **键名用双引号**：`"auto_refresh_interval"`
3. ✅ **数值不加引号**：`20` 而不是 `"20"`
4. ✅ **最后一项不加逗号**
5. ✅ **检查语法**：使用 [JSONLint](https://jsonlint.com/) 验证

## 🔍 验证配置是否生效

### 方法1：查看控制台输出

运行EXE后，查看黑色命令窗口，应该看到：

```
✅ 已加载配置: 自动刷新间隔 30 秒
```

### 方法2：访问配置接口

在浏览器中访问：
```
http://127.0.0.1:8000/api/config
```

返回示例：
```json
{
  "success": true,
  "config": {
    "auto_refresh_interval": 30,
    "max_retries": 3,
    "request_timeout": 10
  },
  "config_file": "C:\\Users\\xxx\\Desktop\\股票监控系统\\config.json"
}
```

### 方法3：观察倒计时

查看网页右上角的倒计时，应该从您设置的秒数开始倒数。

## 🆘 故障排查

### 问题1：配置不生效

**可能原因**：
- JSON格式错误
- 文件编码不是UTF-8
- 文件名错误（必须是 `config.json`）
- 文件位置错误（必须与EXE在同一目录）

**解决方法**：
1. 使用 [JSONLint](https://jsonlint.com/) 验证JSON格式
2. 删除配置文件，重新运行程序让其自动生成
3. 检查文件扩展名是否正确（不要是 `config.json.txt`）

### 问题2：程序无法启动

**可能原因**：
- JSON格式严重错误导致解析失败

**解决方法**：
1. 删除 `config.json`
2. 重新运行程序（会使用默认配置）

### 问题3：不知道配置文件在哪里

**解决方法**：
- 访问 `http://127.0.0.1:8000/api/config`
- 查看返回的 `config_file` 字段，显示完整路径

## 📚 相关文档

- [BUILD_EXE_README.md](./BUILD_EXE_README.md) - EXE打包说明
- [README.md](./README.md) - 项目总览
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - 快速参考

## 🎯 快速参考卡片

```plaintext
┌─────────────────────────────────────────┐
│  🚀 快速修改刷新时间                      │
├─────────────────────────────────────────┤
│  1. 找到EXE文件                          │
│  2. 同目录打开 config.json               │
│  3. 修改 auto_refresh_interval 的值      │
│  4. 保存并重启程序                        │
└─────────────────────────────────────────┘
```

---

**💡 提示**：修改配置后需要重启程序才能生效！

