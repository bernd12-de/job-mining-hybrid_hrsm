# 1. Basis-Image mit Python 3.11
FROM python:3.11-slim

# 2. System-Abhängigkeiten (Postgres, Build-Tools, Curl für Healthchecks)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. Installation der Python-Pakete
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Playwright Browser-Setup (Chromium reicht für Scraper)
RUN playwright install chromium --with-deps

# 5. Code kopieren
COPY . .

# 6. Startbefehl für die API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
