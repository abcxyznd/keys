FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure data directories exist with write permissions
RUN mkdir -p /app/data/keys /app/data/coupon /app/data/links /app/data/shortenurl && \
    chmod -R 777 /app/data && \
    ls -la /app/data/keys/

EXPOSE 8080

CMD ["python", "app.py", "bot.py"]