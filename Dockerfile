# 使用官方 Python 3.11 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 复制 requirements.txt（如果没有则创建）
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序文件
COPY 实时看板.py .

# 暴露 Streamlit 默认端口
EXPOSE 8501

# 设置 Streamlit 配置
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# 启动应用
CMD ["streamlit", "run", "实时看板.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]