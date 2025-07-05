from django import forms
from .models import Student, Attendance
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 'fathers_name', 'dob', 'phone', 'email',
            'university_roll_no', 'registration_number', 'address',
            'image', 'year', 'roll_no', 'course', 'optional_info'
        ]
        
    def clean_roll_no(self):
        roll_no = self.cleaned_data.get('roll_no')
        if roll_no:
            if not roll_no.isdigit() or int(roll_no) < 1:
                raise forms.ValidationError("Roll number must be a positive integer.")
        return roll_no     

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class PhotoUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['image']

class StudentEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 'fathers_name', 'dob', 'phone', 'email',
            'university_roll_no', 'registration_number', 'address',
            'year', 'roll_no', 'course', 'optional_info'
        ]

class AdminAttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date']
    student = forms.ModelChoiceField(queryset=User.objects.filter(student__isnull=False))

class AbsenceReasonForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['date', 'absence_reason', 'medical_doc']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }