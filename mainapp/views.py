from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, Http404, HttpResponse
from .forms import TeacherSignupForm, TeacherLoginForm, ClassroomForm, StudentForm
from django.contrib.auth.decorators import login_required
from .models import Classroom, Student, TestResult, Group_student
from math import ceil
import random
import string
import json

# Groups characteristics
groups = {
    'harmonizer': ['Warm', 'Compassionate', 'Sensitive'],
    'thinker': ['Logical', 'Responsible', 'Organized'],
    'persister': ['Conscientious', 'Observant', 'Committed'],
    'promoter': ['Adaptable', 'Charismatic', 'Action-oriented'],
    'imaginer': ['Calm', 'Reflective', 'Imaginative'],
    'rebel': ['Creative', 'Spontaneous', 'Playful']
}

def home(request):
    signup_form = TeacherSignupForm()
    login_form = TeacherLoginForm()
    student_form = StudentForm()
    return render(request, "home.html", {"signup_form": signup_form, "login_form": login_form, "student_form": student_form})

def teacher_signup(request):
    if request.method == "POST":
        form = TeacherSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            return JsonResponse({"success": True, "redirect_url": "/dashboard/"})
        return JsonResponse({"success": False, "errors": form.errors})
    return JsonResponse({"success": False, "message": "Invalid request."})

def teacher_login(request):
    if request.method == "POST":
        form = TeacherLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return JsonResponse({"success": True, "redirect_url": "/dashboard/"})
        return JsonResponse({"success": False, "errors": form.errors})
    return JsonResponse({"success": False, "message": "Invalid request."})

def teacher_logout(request):
    logout(request)
    return redirect("home")

@login_required
def dashboard(request):
    if request.method == "POST":
        print("POST data:", request.POST)
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.teacher = request.user
            classroom.save()
            print("Classroom saved with ID:", classroom.id)
            grp_size = classroom.group_size
            total_students = classroom.students_count
            num_groups = ceil(total_students / grp_size)
            print("Group size:", grp_size, "Number of groups:", num_groups)
            for i in range(1, num_groups + 1):
                grp = Group_student(
                    classroom=classroom,
                    name=f"Group {i}"
                )
                grp.save()
                print("Group created:", grp.name)
            return redirect("dashboard")
        else:
            print("Form errors:", form.errors)
    else:
        form = ClassroomForm()
    classrooms = Classroom.objects.filter(teacher=request.user)
    return render(request, "dashboard.html", {"form": form, "classrooms": classrooms})

@login_required
def generate_class_code(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    classroom.code = code
    classroom.save()
    return HttpResponse(code, content_type="text/plain")

def enter_class_code(request):
    if request.method == "POST":
        code = request.POST.get("code")
        classroom = Classroom.objects.filter(code=code).first()
        if classroom:
            student_form = StudentForm(request.POST)
            if student_form.is_valid():
                student = student_form.save(commit=False)
                student.classroom = classroom
                student.save()
                request.session['student_id'] = student.id
                return redirect('personality_test')
            else:
                return render(request, 'home.html', {'student_form': student_form, 'error': 'Invalid student information.'})
        else:
            return render(request, 'home.html', {'error': 'Invalid class code.'})
    else:
        student_form = StudentForm()
        return render(request, 'home.html', {'student_form': student_form})

@login_required
def view_students_results(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    students = Student.objects.filter(classroom=classroom)
    return render(request, 'students_results_modal.html', {'students': students})

def randomize_characteristics():
    all_characteristics = [char for chars in groups.values() for char in chars]
    random.shuffle(all_characteristics)
    return all_characteristics

def personality_test(request):
    if request.method == "POST":
        selected_characteristics = request.POST.getlist('characteristics', [])
        scores = {group: 0 for group in groups}
        for group, characteristics in groups.items():
            for characteristic in characteristics:
                if characteristic in selected_characteristics:
                    scores[group] += 1
        max_score = max(scores.values())
        matching_groups = [group for group, score in scores.items() if score == max_score]
        result_group = random.choice(matching_groups) if matching_groups else None
        return render(request, 'result.html', {'result_group': scores})
    characteristics = randomize_characteristics()
    return render(request, 'personality_test.html', {'characteristics': characteristics})

def result(request):
    result = request.GET.get('result', '')
    context = {
        'result': result,
    }
    return render(request, 'result.html', context)

def submit_result(request):
    if request.method == 'POST':
        student_id = request.session.get('student_id')
        if not student_id:
            return HttpResponse("Student not found. Please start the test again.", status=400)
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return HttpResponse("Student not found. Please start the test again.", status=400)
        classroom = student.classroom
        result = request.POST.get('result', '')
        if not result:
            return HttpResponse("No result provided.", status=400)
        selected_characteristics = result.split(', ')
        answers = {"selected_characteristics": selected_characteristics}
        dominant_trait = selected_characteristics[0] if selected_characteristics else None
        if dominant_trait:
            student.score = dominant_trait
            student.save()
        TestResult.objects.create(
            student=student,
            answers=answers,
            dominant_trait=dominant_trait
        )
        assigned_group = None
        available_groups = classroom.groups.all()
        for group in available_groups:
            group_traits = set(group.students.values_list("score", flat=True))
            if dominant_trait not in group_traits:
                group.students.add(student)
                assigned_group = group
                break
        if not assigned_group:
            smallest_group = min(available_groups, key=lambda g: g.students.count(), default=None)
            if smallest_group:
                smallest_group.students.add(student)
        return redirect(f'/personality-test/result/?result={result}')
    return HttpResponse("Invalid request method.", status=400)
