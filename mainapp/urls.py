from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path("login/", views.teacher_login, name="login"),
    path("logout/", views.teacher_logout, name="logout"),
    path("signup/", views.teacher_signup, name="signup"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('classroom/<int:classroom_id>/generate_code/', views.generate_class_code, name='generate_class_code'),
    path('enter_code/', views.enter_class_code, name='enter_code'),
    path('classroom/<int:classroom_id>/view_students/', views.view_students_results, name='view_students_results'),
    # path('take-test/', views.take_test, name='take_test'),  # Ensure this is correctly mapped
    path('personality-test/', views.personality_test, name='personality_test'),
    path('personality-test/result/', views.result, name='result'),
    path('submit-result/', views.submit_result, name='submit_result'),
    
]