from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.core import signing
from .models import Staff, Attendance
from datetime import time


def mark_attendance(request):
    token = request.GET.get('token')
    if not token:
        return JsonResponse({'status': 'error', 'message': 'No token provided'})

    try:
        data = signing.loads(token)
        staff_id = data.get('staff_id')
        staff = Staff.objects.get(staff_id=staff_id)
    except (signing.BadSignature, Staff.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Invalid or unknown staff'})

    today = timezone.localdate()
    attendance, created = Attendance.objects.get_or_create(staff=staff, date=today)

    if created or not attendance.time_in:
        now = timezone.localtime().time()
        attendance.time_in = now

       
        on_time_limit = time(9, 0)
        attendance.status = 'On Time' if now <= on_time_limit else 'Late'
        attendance.save()

        return render(request, 'records/mark_success.html', {
            'staff': staff,
            'attendance': attendance,
            'message': f"{staff.name} signed in successfully"
        })

    elif not attendance.time_out:
        attendance.time_out = timezone.localtime().time()
        attendance.status = 'Signed Out'
        attendance.save()

        return render(request, 'records/mark_success.html', {
            'staff': staff,
            'attendance': attendance,
            'message': f"{staff.name} signed out successfully"
        })

    else:
        return render(request, 'records/mark_success.html', {
            'staff': staff,
            'attendance': attendance,
            'message': "Attendance already completed for today"
        })  