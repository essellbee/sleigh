# Use the lightweight Nginx Alpine image
FROM nginx:alpine

# Copy your index.html into the directory where Nginx serves files
COPY index.html /usr/share/nginx/html/index.html

# Expose port 80 (Standard for web traffic)
EXPOSE 80
