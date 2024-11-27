from rest_framework import viewsets
from .models import CustomUser, Attendance, Leave
from .serializers import UserSerializer, AttendanceSerializer, LeaveSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from datetime import datetime, time
from django.views import View
from .forms import LeaveForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone


# REST API ViewSets
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer


class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer


class CustomLogoutView(View):
    """GET ve POST destekleyen logout view."""
    def get(self, request):
        logout(request)
        return redirect('login')  # Çıkıştan sonra login sayfasına yönlendir

    def post(self, request):
        logout(request)
        return redirect('login')  # Çıkıştan sonra login sayfasına yönlendir


# Kullanıcı Giriş Fonksiyonu
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_manager:
                return redirect('manager_dashboard')
            return redirect('employee_dashboard')
        else:
            return render(request, 'core/manager_employee_login.html', {'error': 'Hatalı kullanıcı adı veya şifre.'})

    return render(request, 'core/manager_employee_login.html')


# Yönetici Paneli
@login_required
def manager_dashboard(request):
    """Yönetici kontrol paneli."""
    if not request.user.is_manager:
        return HttpResponse("Bu alana erişiminiz yok.", status=401)

    # Personel giriş kayıtlarını al
    attendances = Attendance.objects.all()

    attendance_data = []
    for attendance in attendances:
        lateness = attendance.calculate_lateness()
        attendance_data.append({
            'employee': attendance.employee.username,
            'date': attendance.date,
            'check_in': attendance.check_in.strftime('%H:%M:%S') if attendance.check_in else "Giriş Yok",
            'lateness': str(lateness) if lateness else "Zamanında",
        })

    # Aylık çalışma saatlerini hesapla
    month = int(request.GET.get('month', 1))
    year = int(request.GET.get('year', 2025))

    employees = CustomUser.objects.all()
    reports = []
    for employee in employees:
        total_hours = Attendance.get_monthly_working_hours(employee, month, year)
        reports.append({
            'employee': employee,
            'total_hours': total_hours
        })

    # Tüm izinleri çek (onay bekleyen, onaylanan ve reddedilenler)
    leaves = Leave.objects.all()

    return render(request, 'core/manager_dashboard.html', {
        'attendance_data': attendance_data,
        'leaves': leaves,  # Tüm izinleri (onay bekleyen, onaylanan ve reddedilen) şablona gönder
        'reports': reports,  # Aylık çalışma saati raporlarını şablona gönder
        'month': month,
        'year': year,
    })


# Aylık Çalışma Saatleri
def monthly_report(request):
    """
    Çalışanlar için aylık çalışma saatlerini gösteren rapor sayfası.
    """
    month = int(request.GET.get('month', 1))
    year = int(request.GET.get('year', 2025))
    
    employees = CustomUser.objects.all()

    reports = []
    for employee in employees:
        total_hours = Attendance.get_monthly_working_hours(employee, month, year)
        reports.append({
            'employee': employee,
            'total_hours': total_hours
        })

    return render(request, 'monthly_report.html', {'reports': reports, 'month': month, 'year': year})



# Personel Paneli
@login_required
def employee_dashboard(request):
    """Personel kontrol paneli."""
    if request.user.is_manager:
        return HttpResponse("Bu alana erişiminiz yok.", status=401)

    # Personelin izin talep formunu işleme
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            # Formu kaydet ve formu temizle
            leave = form.save(commit=False)
            leave.employee = request.user
            leave.save()
            return redirect('employee_dashboard')  # Formu kaydettikten sonra tekrar aynı sayfaya yönlendir
    else:
        form = LeaveForm()

    # Personelin izin ve giriş kayıtlarını al
    attendances = Attendance.objects.filter(employee=request.user)
    leaves = Leave.objects.filter(employee=request.user)

    return render(request, 'core/employee_dashboard.html', {
        'attendances': attendances,
        'leaves': leaves,
        'form': form,  # Formu şablona gönder
    })

@login_required
def approve_leave(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    if not leave.is_approved:  # Zaten onaylı değilse işlemi yap
        leave.is_approved = True
        leave.save()

        # Çalışanın yıllık izninden izin gün sayısını düşür
        employee = leave.employee
        employee.annual_leave_days -= leave.days_off  # Gün sayısını yıllık izninden düş
        employee.save()

    return redirect('manager_dashboard')  # Yönetici paneline yönlendir


@login_required
def reject_leave(request, leave_id):
    """İzin talebini reddet."""
    leave = get_object_or_404(Leave, id=leave_id)

    # Zaten onaylanmış veya reddedilmişse işlem yapma
    if leave.is_approved is not None:
        return redirect('manager_dashboard')

    # İzin reddedildiğinde, onay durumu False yapılır
    leave.is_approved = False  # Reddet
    leave.save()

    return redirect('manager_dashboard')

# Yeni İzin Tanımlama
@login_required
def create_leave(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user  # İzin talebini oluşturan kullanıcıyı ata
            leave.is_approved = None  # Varsayılan olarak beklemede olmalı
            leave.save()
            return redirect('employee_dashboard')  # Kayıttan sonra yönlendir
    else:
        form = LeaveForm()

    return render(request, 'core/create_leave.html', {'form': form})



# Genel Dashboard
@login_required
def dashboard(request):
    if request.user.is_manager:
        return redirect('manager_dashboard')
    else:
        return redirect('employee_dashboard')

@login_required
def add_leave(request):
    """Yeni bir izin kaydı eklemek için kullanılan fonksiyon."""
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manager_dashboard')  # Başarılı eklemeden sonra yönlendir
    else:
        form = LeaveForm()

    return render(request, 'core/add_leave.html', {'form': form})

@login_required
def manage_leave_requests(request):
    """Yöneticinin izin taleplerini onaylayıp reddetmesi için view"""
    if not request.user.is_manager:
        return HttpResponse("Bu alana erişiminiz yok.", status=401)

    # Sadece bekleyen izin taleplerini al
    leave_requests = Leave.objects.filter(is_approved=None)

    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')  # 'approve' veya 'reject' olabilir

        leave = get_object_or_404(Leave, id=leave_id)

        if leave.is_approved is not None:  # Daha önce işlem yapılmış talepler
            return HttpResponse("Bu izin talebi zaten işlenmiş.", status=400)

        if action == 'approve':
            leave.is_approved = True
            leave.approved_at = timezone.now()  # Onay tarihi
        elif action == 'reject':
            leave.is_approved = False
            leave.approved_at = timezone.now()  # Reddetme tarihi

        leave.save()

        # Personel kullanıcısına bildirim gönderme
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{leave.employee.id}",  # Personel kullanıcıya özel grup
            {
                "type": "send_notification",
                "message": f"İzin talebiniz {'onaylandı' if leave.is_approved else 'reddedildi'}: {leave.start_date} - {leave.end_date}",
            }
        )

    return render(request, 'core/manage_leave_requests.html', {'leave_requests': leave_requests})
