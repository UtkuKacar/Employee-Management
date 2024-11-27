from django.db import models
from django.contrib.auth.models import AbstractUser
from core.scripts.date_utils import is_holiday
from datetime import datetime, time
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User

class CustomUser(AbstractUser):
    is_manager = models.BooleanField(default=False)  # Yetkili mi?
    annual_leave_days = models.IntegerField(default=15)  # Yıllık izin günleri
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField()

    def reduce_leave(self, lateness_minutes):
        """
        Geç kalma süresini yıllık izinden düşer.
        480 dakika (8 saat) = 1 iş günü olarak hesaplanır.
        """
        lateness_days = lateness_minutes / 480  # Dakikayı gün birimine çevir
        self.annual_leave_days -= lateness_days
        self.save()

    def check_annual_leave(self):
        """
        Eğer yıllık izin günleri 3 günden azsa, yöneticilere bildirim gönder.
        """
        if self.annual_leave_days < 3:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "managers",  # Tüm yöneticilere bildirim gönder
                {
                    "type": "send_notification",
                    "message": f"{self.username} adlı personelin yıllık izin günleri 3 günden az kaldı: {self.annual_leave_days} gün.",
                }
            )

class Attendance(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.username} - {self.date}"

    def calculate_lateness(self):
        """
        Geç kalma süresini hesaplar ve yıllık izinden düşer.
        """
        work_start = time(hour=8, minute=0)  # İş başlangıç saati

        # Eğer check_in string formatında ise, onu time nesnesine dönüştür
        if isinstance(self.check_in, str):
            self.check_in = datetime.strptime(self.check_in, "%H:%M").time()

        # check_in zamanı iş başlangıç saatinden büyükse, geç kalma hesaplanır
        if self.check_in and self.check_in > work_start:
            lateness = datetime.combine(self.date, self.check_in) - datetime.combine(self.date, work_start)
            lateness_minutes = lateness.total_seconds() / 60  # Dakika olarak hesapla
            self.employee.reduce_leave(lateness_minutes)  # Yıllık izinden kesinti yap
            return lateness_minutes  # Geç kalma süresi dakikalar olarak döndürülür
        return None

    def working_hours(self):
        """
        Günlük çalışma saatini hesaplar.
        """
        if self.check_in and self.check_out:
            # Çalışma saatini hesapla
            work_start = datetime.combine(self.date, self.check_in)
            work_end = datetime.combine(self.date, self.check_out)
            work_duration = work_end - work_start
            return work_duration.total_seconds() / 3600  # Saat olarak döndür
        return 0
    
    def get_monthly_working_hours(employee, month, year):
        """
        Verilen ay ve yıl için çalışanın toplam çalışma saatlerini hesaplar.
        """
        # Çalışanın o ayki tüm 'Attendance' kayıtlarını al
        attendances = Attendance.objects.filter(
            employee=employee,
            date__year=year,
            date__month=month
        )

        # Toplam çalışma saatini hesapla
        total_hours = sum([attendance.working_hours() for attendance in attendances])
        return total_hours

    def save(self, *args, **kwargs):
        """
        Kayıt sırasında geç kalma kontrolü yapılır ve yıllık izinden kesinti uygulanır.
        Ayrıca, geç kalma varsa yöneticilere bildirim gönderilir.
        """
        # Tatil kontrolü
        if is_holiday(self.date):
            raise ValueError("Tatil günlerinde giriş yapılamaz.")

        # Eğer check-in varsa geç kalma süresini hesapla ve yıllık izinden düş
        lateness = self.calculate_lateness()

        # Eğer geç kalma varsa yöneticilere bildirim gönder
        if lateness:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(  # Asenkron olarak yöneticilere bildirim gönder
                "managers",  # Tüm yetkililere bildirim gönder
                {
                    "type": "send_notification",
                    "message": f"{self.employee.username} adlı personel, {self.date} tarihinde saat {self.check_in.strftime('%H:%M')}'de geç kalmıştır.",
                }
            )

        super().save(*args, **kwargs)  # Ana kaydetme işlemi
        
        # Yıllık izni kontrol et ve 3 günden azsa bildirim gönder
        self.employee.check_annual_leave()


class Leave(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=50)
    is_approved = models.BooleanField(default=None)
    reason = models.TextField(default="N/A")

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} ({'Onaylı' if self.is_approved else 'Bekliyor'})"

    @property
    def days_off(self):
        """
        Bu fonksiyon, izin başlangıç ve bitiş tarihine göre izin gün sayısını döndürür.
        """
        delta = self.end_date - self.start_date
        return delta.days + 1  # +1, başlangıç gününü de dahil eder.