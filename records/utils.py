from datetime import datetime, time
import pytz
from django.conf import settings
from django.utils import timezone
from .models import Staff, Attendance


def mark_staff_attendance(staff):
    """
    Marks attendance for a staff member.
    Returns a tuple: (attendance object, message string)
    """
    today = timezone.localdate()
    attendance, created = Attendance.objects.get_or_create(staff=staff, date=today)

    # Lagos timezone
    lagos = pytz.timezone('Africa/Lagos')
    now_dt = datetime.now(lagos)
    now_time = now_dt.replace(second=0, microsecond=0).time()

    
    cutoff_setting = getattr(settings, 'ATTENDANCE_CUTOFF', "9:00")
    if isinstance(cutoff_setting, str):
        cutoff_hour, cutoff_minute = map(int, cutoff_setting.split(":"))
    else:
        cutoff_hour, cutoff_minute = cutoff_setting
    cutoff = time(cutoff_hour, cutoff_minute)

    # Mark attendance
    if created or not attendance.time_in:
        attendance.time_in = now_time
        attendance.status = 'On Time' if now_time <= cutoff else 'Late'
        attendance.save()
        message = f"{staff.name} signed in successfully"

    elif not attendance.time_out:
        attendance.time_out = now_time
        attendance.status = 'Signed Out'
        attendance.save()
        message = f"{staff.name} signed out successfully"

    else:
        message = "Attendance already completed for today"

    return attendance, message


def mark_absent():
    """
    Marks all staff who haven't checked in today as Absent.
    Should be run at the end of the day.
    """
    today = timezone.localdate()
    all_staff = Staff.objects.all()

    for staff in all_staff:
        if not Attendance.objects.filter(staff=staff, date=today).exists():
            Attendance.objects.create(
                staff=staff,
                date=today,
                status='Absent'
            )
    print("Absentees marked successfully.")
