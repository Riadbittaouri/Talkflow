from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class TeacherManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class Teacher(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = TeacherManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.email
    


class Classroom(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)  # Link the custom Teacher model
    name = models.CharField(max_length=255)  # Class name
    students_count = models.PositiveIntegerField(default=0)  # Number of students
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return self.name

    
class Student(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    score = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class TestResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    test_date = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField(default=dict)  # Store answers as a JSON object

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.test_date}"

