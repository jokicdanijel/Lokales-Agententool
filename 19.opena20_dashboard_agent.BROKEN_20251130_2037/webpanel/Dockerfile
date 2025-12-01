FROM nginx:alpine

# Copy web panel files
COPY . /usr/share/nginx/html/

# Create assets directory and basic logo
RUN mkdir -p /usr/share/nginx/html/assets

# Simple SVG logo fallback
RUN echo '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="#58a6ff"><circle cx="12" cy="12" r="10" stroke="#58a6ff" stroke-width="2" fill="none"/><path d="M8 12l2 2 4-4" stroke="#58a6ff" stroke-width="2" fill="none"/></svg>' > /usr/share/nginx/html/assets/logo.svg

# Nginx config for SPA
RUN echo 'server { listen 80; root /usr/share/nginx/html; index index.html; location / { try_files $uri $uri/ /index.html; } }' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]