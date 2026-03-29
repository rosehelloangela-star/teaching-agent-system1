FROM docker.m.daocloud.io/library/python:3.10-slim

WORKDIR /app

# 替换默认镜像源加快安装速度（可选）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 暴露 FastAPI 默认端口
EXPOSE 8000

# 启动服务
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]