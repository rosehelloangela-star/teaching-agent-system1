# 构建阶段
FROM docker.m.daocloud.io/library/node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build  # 如果你用的是 vite，打包产物通常在 dist 目录

# 运行阶段
FROM docker.m.daocloud.io/library/nginx:alpine
# 将构建好的文件复制到 Nginx 默认目录 (注意：如果是 create-react-app 则是 build 目录)
COPY --from=build /app/dist /usr/share/nginx/html 
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]