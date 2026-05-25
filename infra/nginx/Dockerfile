# Stage 1: Build the Flutter Web application
FROM ghcr.io/cirruslabs/flutter:stable AS builder

WORKDIR /app

COPY frontend/pubspec.* ./
RUN flutter pub get

COPY frontend/ .
RUN flutter build web --release

# Stage 2: Nginx Web Server
FROM nginx:alpine

# Copy custom Nginx configuration
COPY infra/nginx/nginx.conf /etc/nginx/nginx.conf

# Copy compiled Flutter web assets from Stage 1
COPY --from=builder /app/build/web /usr/share/nginx/html

EXPOSE 80 443
