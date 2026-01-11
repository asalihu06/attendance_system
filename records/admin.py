from django.contrib import admin
from django.utils.html import format_html
from .models import Staff, Attendance

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'staff_id', 'department', 'position', 'show_qr_code')

    def show_qr_code(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="80" height="80" />', obj.qr_code.url)
        return "No QR code"

    show_qr_code.short_description = 'QR Code'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('staff', 'date', 'time_in', 'time_out', 'status')
