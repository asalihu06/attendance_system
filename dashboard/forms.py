from django import forms
from records.models import Staff

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['name', 'staff_id', 'department', 'position']
