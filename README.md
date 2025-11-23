# 股市实时监控看板

## Docker 构建和运行

### 构建镜像
```bash
docker build -t stock-dashboard .
```

### 运行容器
```bash
docker run -p 8501:8501 stock-dashboard
```

### 访问应用
容器启动后，在浏览器中访问：
```
http://localhost:8501
```

### 后台运行
```bash
docker run -d -p 8501:8501 --name stock-dashboard stock-dashboard
```

### 查看日志
```bash
docker logs stock-dashboard
```

### 停止容器
```bash
docker stop stock-dashboard
```

### 删除容器
```bash
docker rm stock-dashboard
```

## 功能特性
- 股市实时数据监控
- 竞价涨幅和跌幅数据
- 连板排行榜
- 热门概念展示
- 自动刷新功能