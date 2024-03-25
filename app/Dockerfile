# Gebruik Python als image
FROM python:3.8-slim

# Zet de working directory
WORKDIR /app

# Zet de huidige directory in /app
COPY . /app 

# Installeer alle dependencies vanuit requirements.txt
RUN pip install --no-cache-dir -r requirements.txt 

# Zet port 5000 open
EXPOSE 5000 

# Run application.py wanneer de container start
CMD ["python", "application.py"]