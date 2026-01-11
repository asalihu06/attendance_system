from datetime import date, timedelta, datetime
from io import BytesIO
import openpyxl
import pandas as pd
from datetime import time
import pytz 

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.db.models import Count
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from records.models import Staff, Attendance
from records.utils import mark_absent
from .forms import StaffForm


# ---------- AUTH ----------

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard_home")
        messages.error(request, "Invalid username or password")
    return render(request, "dashboard/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# ---------- DASHBOARD----------

@login_required
def dashboard_home(request):
    today = date.today()
    attendance_records = Attendance.objects.filter(date=today).select_related("staff")

    # Staff attendance summary
    total_staff = Staff.objects.count()
    present_staff_ids = attendance_records.values_list("staff__id", flat=True)
    absentees = Staff.objects.exclude(id__in=present_staff_ids)

    todays_attendance = attendance_records.count()
    signed_in_count = attendance_records.filter(status__in=["On Time", "Late"]).count()
    signed_out_count = attendance_records.filter(status="Signed Out").count()
    absent_count = absentees.count()

   
    all_today_records = list(attendance_records)
    for staff in absentees:
        all_today_records.append(
            Attendance(
                staff=staff,
                date=today,
                time_in=None,
                time_out=None,
                status="Absent",
            )
        )
 
    labels, attendance_counts = [], []
    day_count, i = 0, 0
    while day_count < 5:
        day = today - timedelta(days=i)
        if day.weekday() < 5:  
            labels.append(day.strftime("%b %d"))
            attendance_counts.append(Attendance.objects.filter(date=day).count())
            day_count += 1
        i += 1

    labels.reverse()
    attendance_counts.reverse()

    context = {
        "attendance_records": all_today_records,
        "labels": labels,
        "attendance_counts": attendance_counts,
        "today": today,
        "total_staff": total_staff,
        "todays_attendance": todays_attendance,
        "signed_in_count": signed_in_count,
        "signed_out_count": signed_out_count,
        "absent_count": absent_count,
    }

    return render(request, "dashboard/home.html", context)

 

@login_required
def download_report_pdf(request):
    """Generate monthly attendance report as PDF."""
    month = request.GET.get("month")
    if not month:
        return HttpResponse("Month not provided", status=400)

    selected_month = datetime.strptime(month, "%Y-%m")
    records = Attendance.objects.filter(
        date__year=selected_month.year,
        date__month=selected_month.month
    ).select_related("staff")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()

    title = Paragraph(
        f"<b>Attendance Report - {selected_month.strftime('%B %Y')}</b>",
        styles["Title"]
    )
    elements.append(title)
    elements.append(Spacer(1, 0.3 * inch))

    data = [["Staff Name", "Staff ID", "Date", "Time In", "Time Out", "Status"]]
    for r in records:
        data.append([
            r.staff.name,
            r.staff.staff_id,
            r.date.strftime("%b %d, %Y"),
            r.time_in.strftime("%H:%M") if r.time_in else "-",
            r.time_out.strftime("%H:%M") if r.time_out else "-",
            r.status or "-"
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"Attendance_Report_{month}.pdf")


@login_required
def download_report_excel(request):
    """Generate monthly attendance report as Excel."""
    month = request.GET.get("month")
    if not month:
        return HttpResponse("Month not provided", status=400)

    selected_month = datetime.strptime(month, "%Y-%m")
    records = Attendance.objects.filter(
        date__year=selected_month.year,
        date__month=selected_month.month
    ).select_related("staff")

    if not records.exists():
        return HttpResponse("No attendance records found for this month.", status=404)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = f"{selected_month.strftime('%B %Y')} Report"

    headers = ["Staff Name", "Staff ID", "Date", "Time In", "Time Out", "Status"]
    sheet.append(headers)

    for r in records:
        sheet.append([
            r.staff.name,
            r.staff.staff_id,
            r.date.strftime("%Y-%m-%d"),
            r.time_in.strftime("%H:%M") if r.time_in else "",
            r.time_out.strftime("%H:%M") if r.time_out else "",
            r.status or "",
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = f"Attendance_Report_{selected_month.strftime('%Y_%m')}.xlsx"
    response["Content-Disposition"] = f'attachment; filename={filename}'
    workbook.save(response)
    return response


 

@login_required
def staff_list(request):
    staffs = Staff.objects.all().order_by("name")
    return render(request, "dashboard/staff_list.html", {"staffs": staffs})


@login_required
def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Staff added successfully.")
        return redirect("staff_list")
    return render(request, "dashboard/add_staff.html", {"form": form})


@login_required
def edit_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    form = StaffForm(request.POST or None, request.FILES or None, instance=staff)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Staff updated successfully.")
        return redirect("staff_list")
    return render(request, "dashboard/edit_staff.html", {"form": form})


@login_required
def delete_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    staff.delete()
    messages.warning(request, "Staff deleted successfully.")
    return redirect("staff_list")


@login_required
def dashboard_reports(request):
    month = request.GET.get("month")
    summary_data = None
    chart_data = {}

    if month:
        selected_month = datetime.strptime(month, "%Y-%m")
        records = Attendance.objects.filter(
            date__year=selected_month.year,
            date__month=selected_month.month
        )

        total_records = records.count()
        total_on_time = records.filter(status="On Time").count()
        total_late = records.filter(status="Late").count()
        total_absent = records.filter(status="Absent").count()

        daily_counts = records.values("date").annotate(count=Count("id")).order_by("date")
        avg_attendance = sum(d["count"] for d in daily_counts) / len(daily_counts) if daily_counts else 0
        highest_day = max(daily_counts, key=lambda d: d["count"])["date"].strftime("%b %d") if daily_counts else "N/A"

        summary_data = {
            "month": month,
            "month_display": selected_month.strftime("%B %Y"),
            "total_records": total_records,
            "average_daily": round(avg_attendance, 2),
            "highest_day": highest_day,
        }

        chart_data = {
            "on_time": total_on_time,
            "late": total_late,
            "absent": total_absent,
        }

    context = {
        "summary_data": summary_data,
        "chart_data": chart_data,
    }
    return render(request, "dashboard/reports.html", context)



def mark_attendance(request, staff_id):
    staff = get_object_or_404(Staff, staff_id=staff_id)
    today = timezone.localdate()
    attendance, created = Attendance.objects.get_or_create(staff=staff, date=today)

    
    lagos = pytz.timezone('Africa/Lagos')
    now_dt = datetime.now(lagos)
    now_time = now_dt.time()

    if created or not attendance.time_in:
        attendance.time_in = now_time

        cutoff = time(9, 0)  
        attendance.status = 'On Time' if now_time < cutoff else 'Late'

        attendance.save()
        message = f"{staff.name} signed in successfully"

    elif not attendance.time_out:
        attendance.time_out = now_time
        attendance.status = 'Signed Out'
        attendance.save()
        message = f"{staff.name} signed out successfully"

    else:
        message = "Attendance already completed for today"

    return render(request, 'dashboard/attendance_confirmation.html', {
        'staff': staff,
        'attendance': attendance,
        'message': message
    })



@login_required
def dashboard_stats(request):
    today = date.today()
    attendance_records = Attendance.objects.filter(date=today)

    signed_in = attendance_records.filter(status__in=["On Time", "Late"]).count()
    signed_out = attendance_records.filter(status__iexact="Signed Out").count()

    data = {
        "total_staff": Staff.objects.count(),
        "todays_attendance": attendance_records.count(),
        "signed_in": signed_in,
        "signed_out": signed_out,
    }
    return JsonResponse(data)


