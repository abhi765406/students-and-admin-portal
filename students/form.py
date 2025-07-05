from django import forms
from .models import Student


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

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

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