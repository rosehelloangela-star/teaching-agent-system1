# 构建阶段
FROM docker.m.daocloud.io/library/node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build  

# 运行阶段
FROM docker.m.daocloud.io/library/nginx:alpine
# 将构建好的文件复制到 Nginx 默认目录
COPY --from=build /app/dist /usr/share/nginx/html 

# 🚨🚨🚨 最关键的一步：把自定义的 Nginx 配置复制进去（确保你已经在同级目录下建好了 default.conf）
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]