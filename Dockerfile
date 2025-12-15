FROM python:3.9-slim

WORKDIR /app

# On installe les outils nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# On copie les fichiers de configuration
COPY requirements.txt .

# On installe les librairies
RUN pip3 install -r requirements.txt

# On copie le reste du code
COPY . .

# On lance l'app
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]