from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    UserViewSet,
    AttendanceViewSet,
    LeaveViewSet,
    custom_login,
    manager_dashboard,
    employee_dashboard,
    dashboard,
    CustomLogoutView,  # Özel logout view'i import edin
    add_leave,
)

# REST Framework için Router
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'leaves', LeaveViewSet)

urlpatterns = [
    # Anasayfa olarak giriş ekranını ayarla
    path('', custom_login, name='home'),

    # API endpoint'leri
    path('api/', include(router.urls)),

    # Kullanıcı giriş ve çıkış işlemleri
    path('login/', custom_login, name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),  # Özel logout view kullanılıyor

    # Yönetici ve Personel Panelleri
    path('manager/dashboard/', manager_dashboard, name='manager_dashboard'),
    path('employee/dashboard/', employee_dashboard, name='employee_dashboard'),

    # Genel dashboard (Kullanıcı türüne göre yönlendirme)
    path('dashboard/', dashboard, name='dashboard'),

    path('manager/add-leave/', add_leave, name='add_leave'),
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),

    path('manage_leave_requests/', views.manage_leave_requests, name='manage_leave_requests'),

    path('leave/approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('leave/reject/<int:leave_id>/', views.reject_leave, name='reject_leave'),
]
