from core.models import Attendance, CustomUser
from datetime import datetime

def record_attendance(employee_id, check_in=None, check_out=None):
    employee = CustomUser.objects.get(id=employee_id)
    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=datetime.now().date()
    )
    if check_in:
        attendance.check_in = check_in
    if check_out:
        attendance.check_out = check_out
    attendance.save()
