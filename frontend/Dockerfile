FROM oven/bun:1.2-alpine as builder

WORKDIR /app

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

COPY ./bun.lock .
COPY ./package.json .

RUN bun install --frozen-lockfile

COPY . .

RUN bun run build

FROM nginx:stable-alpine as final

COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]
