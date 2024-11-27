# Python 3.11 tabanlı bir imaj kullanıyoruz
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Gereksinim dosyasını kopyala ve bağımlılıkları yükle
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . /app

# Django server başlatmak için komut
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
