from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Classroom, Student

User = get_user_model()

class TeacherSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["full_name", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match")
        return cleaned_data

class TeacherLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ["name", "students_count", "group_size"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter class name"}),
            "students_count": forms.NumberInput(attrs={"class": "form-control", "min": "0", "value": "0"}),
            "group_size": forms.NumberInput(attrs={"class": "form-control", "min": "1", "value": "4"}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}),
            'last_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"}),
            'email': forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
        }

