from django.contrib import admin
from .models import CustomUser, Attendance, Leave


# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Attendance)
admin.site.register(Leave)
