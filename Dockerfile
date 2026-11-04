FROM python:3.13-slim

WORKDIR /app

# Copier les dépendances
COPY requirements-prod.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copier uniquement les fichiers nécessaires
COPY app_api.py .
COPY src/api ./src/api
COPY models ./models

# Port utilisé par l'API
EXPOSE 7860

# Port configurable avec la variable PORT
CMD ["sh", "-c", "uvicorn app_api:app --host 0.0.0.0 --port ${PORT:-7860}"]