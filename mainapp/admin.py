from django.contrib import admin
from .models import *  # Import your Teacher model

# Register your models here
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'is_active', 'is_staff')  # Fields to display in the admin list view
    list_filter = ('is_active', 'is_staff')  # Filters for the admin list view
    search_fields = ('email', 'full_name')  # Fields to search in the admin panel
    ordering = ('email',)  # Default ordering for the list view

admin.site.register(Classroom)
admin.site.register(Student)
admin.site.register(TestResult)
admin.site.register(Group_student)