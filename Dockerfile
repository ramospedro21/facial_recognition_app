FROM python:3.9-slim

# Instale as dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopencv-dev \
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libopenblas-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Instale as dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY src/ .
COPY data/ ./data/
COPY logs/ ./logs/

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"]