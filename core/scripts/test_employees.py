import os
import sys
from datetime import datetime
import django

# Proje kök dizinini Python yoluna ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from core.models import CustomUser, Attendance

# Çalışan ekleme ve giriş kaydı
# 1. Çalışan oluştur
employee1 = CustomUser.objects.create_user(
    username="sevval",
    password="123456",
    email="sevval@gmail.com",
    is_manager=False  # Yönetici olmayan bir çalışan
)

print(f"Yeni Çalışan: {employee1.username}, İzin Günleri: {employee1.annual_leave_days}")

# 2. Çalışan oluştur
employee2 = CustomUser.objects.create_user(
    username="utku",
    password="123456",
    email="utku@gmail.com",
    is_manager=False  # Yönetici olmayan bir çalışan
)

print(f"Yeni Çalışan: {employee2.username}, İzin Günleri: {employee2.annual_leave_days}")

# 1. Çalışanın giriş kaydını oluştur
attendance1 = Attendance.objects.create(
    employee=employee1,
    date=datetime(2025, 1, 1),
    check_in=datetime.strptime("08:15", "%H:%M").time(),  # Giriş zamanı
    check_out=datetime.strptime("18:00", "%H:%M").time()  # Çıkış zamanı
)

print(f"1. Çalışanın Giriş Kaydı: {attendance1.employee.username}, Tarih: {attendance1.date}, Saat: {attendance1.check_in}")

# 2. Çalışanın giriş kaydını oluştur
attendance2 = Attendance.objects.create(
    employee=employee2,
    date=datetime(2025, 1, 1),
    check_in=datetime.strptime("08:45", "%H:%M").time(),  # Giriş zamanı
    check_out=datetime.strptime("18:00", "%H:%M").time()  # Çıkış zamanı
)

print(f"2. Çalışanın Giriş Kaydı: {attendance2.employee.username}, Tarih: {attendance2.date}, Saat: {attendance2.check_in}")
