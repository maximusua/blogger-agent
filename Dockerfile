FROM python:3.11-slim

WORKDIR /app

# Встановлюємо git
RUN apt-get update && apt-get install -y git

# Встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо файли проекту
COPY . .

# Запускаємо скрипт
CMD ["python", "test_kyiv_blog.py"] 