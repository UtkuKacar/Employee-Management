from core.models import Leave, CustomUser

def add_leave(employee_id, start_date, end_date, leave_type):
    employee = CustomUser.objects.get(id=employee_id)
    leave = Leave.objects.create(
        employee=employee,
        start_date=start_date,
        end_date=end_date,
        leave_type=leave_type
    )
    leave.save()
