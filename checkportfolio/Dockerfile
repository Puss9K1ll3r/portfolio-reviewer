FROM python:3.9-slim

RUN apt update && apt install -y unrar-free

WORKDIR /app

# Создаем директории для БД и медиафайлов
RUN mkdir -p /app/db \
    && mkdir -p /app/media/temp_uploads

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "checkportfolio.wsgi:application"]