# 使用官方 Node.js 映像
FROM node:21-alpine as build-stage

# 設置工作目錄
WORKDIR /app

# 複製前端應用的 package.json 和 package-lock.json
COPY package.json .


# 安裝依賴
RUN npm install

# 複製前端應用的其餘部分到工作目錄
COPY . .
EXPOSE 5173
# 構建應用
RUN npm run build

# # 生產階段
# FROM nginx:stable-alpine as production-stage
# COPY --from=build-stage /app/vue-project/dist /usr/share/nginx/html

# CMD ["nginx", "-g", "daemon off;"]
CMD [ "npm", "run", "dev" ]