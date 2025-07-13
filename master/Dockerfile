# --- Frontend build ---
FROM node:20 AS frontend-build
WORKDIR /app/frontend
COPY master/frontend/package*.json ./
RUN npm install
COPY master/frontend ./
RUN npm run build

# --- Backend build ---
FROM python:3.11-slim AS backend
WORKDIR /app
COPY master/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY master/app ./app
COPY --from=frontend-build /app/frontend/dist ./frontend-dist

# --- Final image for backend + static frontend ---
FROM python:3.11-slim AS backend-final
WORKDIR /app
COPY --from=backend /app /app
COPY master/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"] 