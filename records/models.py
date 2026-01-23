import os
from io import BytesIO
from datetime import time

from django.db import models
from django.core.files import File
from django.core.files.base import ContentFile

import qrcode
from PIL import Image


class Staff(models.Model):
    name = models.CharField(max_length=100)
    staff_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        base_url = os.environ.get('BASE_URL', 'http://127.0.0.1:8000')
        
        if not self.qr_code or 'res.cloudinary.com' not in str(self.qr_code):
            qr_data = f"{base_url}/dashboard/mark/{self.staff_id}/"
            qr_img = qrcode.make(qr_data).convert("RGB")
            
            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            
            file_name = f"qr_{self.staff_id}.png"
            # Save the file to Cloudinary via ContentFile
            self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)
            buffer.close()
        
        super().save(*args, **kwargs)

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Signed In', 'Signed In'),
        ('Signed Out', 'Signed Out'),
        ('On Time', 'On Time'),
        ('Late', 'Late'),
        ('Absent', 'Absent'),
    ]

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='Signed In')

    def save(self, *args, **kwargs):
        start_time = time(9, 0)
        if self.time_in:
            self.status = 'On Time' if self.time_in <= start_time else 'Late'
        else:
            self.status = 'Absent'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.staff.name} - {self.date}"
