from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse,Http404
from .forms import TeacherSignupForm, TeacherLoginForm,ClassroomForm,StudentForm
from django.contrib.auth.decorators import login_required
from .models import Classroom, Student,TestResult
import random
import string
import json

# Définir les groupes et leurs caractéristiques
groups = {
    'empathetic': ['Warm', 'Compassionate', 'Sensitive'], #5
    'work lover': ['Logic', 'Responsible', 'Organised'], #1
    'persevering': ['Conscientious', 'Observant', 'Dedicated'], #3 
    'promoter': ['Calm', 'Introspective', 'Imaginative'], #2
    'dreamer': ['Adaptable', 'Resourceful', 'Charming'], #4
    'rebel': ['Creative', 'Spontaneous', 'Playful'] #6
}


def home(request):
    """Render the home page with modals."""
    signup_form = TeacherSignupForm()
    login_form = TeacherLoginForm()
    student_form = StudentForm()
    return render(request, "home.html", {"signup_form": signup_form, "login_form": login_form,"student_form" : student_form})

def teacher_signup(request):
    """Handle signup inside the modal."""
    if request.method == "POST":
        form = TeacherSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            return JsonResponse({"success": True, "redirect_url": "/dashboard/"})  # Redirect to dashboard
        return JsonResponse({"success": False, "errors": form.errors})  # Return errors
    
    return JsonResponse({"success": False, "message": "Invalid request."})

def teacher_login(request):
    """Handle login inside the modal."""
    if request.method == "POST":
        form = TeacherLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return JsonResponse({"success": True, "redirect_url": "/dashboard/"})  # Redirect to dashboard
        
        return JsonResponse({"success": False, "errors": form.errors})  # Return errors
    
    return JsonResponse({"success": False, "message": "Invalid request."})

def teacher_logout(request):
    """Logout the user."""
    logout(request)
    return redirect("home")


@login_required
def dashboard(request):
    if request.method == "POST":
        form = ClassroomForm(request.POST)
        if form.is_valid():
            # Create and save the classroom instance
            classroom = form.save(commit=False)
            # You can manually set the number of students if it's passed in the form
            classroom.students_count = form.cleaned_data.get('students_count', 0)
            classroom.teacher = request.user  # Make sure the teacher is set correctly
            classroom.save()
            return redirect('dashboard')  # Redirect back to the dashboard page

    else:
        form = ClassroomForm()

    # Fetch all the classrooms for the teacher to display
    classrooms = Classroom.objects.filter(teacher=request.user)
    
    return render(request, "dashboard.html", {"form": form, "classrooms": classrooms})




# For teacher to generate the code for each class

def generate_class_code(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))  # Generate 10-character code
    classroom.code = code
    classroom.save()
    return JsonResponse({"code": code})  # Return the generated code as JSON

def enter_class_code(request):
    if request.method == "POST":
        code = request.POST.get("code")
        classroom = Classroom.objects.filter(code=code).first()
        
        if classroom:
            # Class code is valid, handle student form
            student_form = StudentForm(request.POST)  # Pass all POST data to the form
            
            if student_form.is_valid():
                student = student_form.save(commit=False)
                student.classroom = classroom
                student.save()
                return redirect('take_test')  # Redirect to the test page
            else:
                # If the student form is not valid, re-render the page with error messages
                return render(request, 'home.html', {'student_form': student_form, 'error': 'Invalid student information.'})
        else:
            # Invalid class code
            return render(request, 'home.html', {'error': 'Invalid class code.'})
    
    else:
        # For GET request, just show the empty form
        student_form = StudentForm()  # Empty student form
        return render(request, 'home.html', {'student_form': student_form})





# Teacher viewing list of students and their results
def view_students_results(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    students = Student.objects.filter(classroom=classroom)
    return render(request, 'students_results_modal.html', {'students': students})




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
                request.session['student_id'] = student.id  # Set student ID in session
                return redirect('personality_test')  # Utiliser le nom correct
            else:
                return render(request, 'home.html', {'student_form': student_form, 'error': 'Invalid student information.'})
        else:
            return render(request, 'home.html', {'error': 'Invalid class code.'})
    
    else:
        student_form = StudentForm()
        return render(request, 'home.html', {'student_form': student_form})

    
def randomize_characteristics():
    """Mélange les caractéristiques des groupes."""
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
    # Exemple de contexte à passer au template
    context = {
        'message': 'Voici votre résultat personnalisé.',
    }
    return render(request, 'result.html', context)

# def take_test(request):
#     questions = [
#             "Vous vous faites fréquemment de nouveaux amis.",
#             "Les idées complexes et novatrices vous enthousiasment plus que les idées simples et directes.",
#             "Vous vous laissez en général plus facilement convaincre par des émotions qui vous touchent que par des arguments factuels.",
#             "Vos espaces de vie et de travail sont propres et organisés.",
#             "Vous restez généralement calme, même sous une forte pression.",
#             "Vous trouvez l’idée de réseauter ou de vous promouvoir auprès d’étrangers très intimidante.",
#             "Vous priorisez et planifiez les tâches de manière efficace, les accomplissant souvent bien avant la date limite.",
#             "Les histoires et les émotions des gens vous parlent plus fort que les chiffres ou les données.",
#             "Vous aimez recourir à des outils de gestion tels que les calendriers et les listes.",
#             "Même une petite erreur peut vous faire douter de vos capacités et de vos connaissances.",
#             "Vous n’avez aucun mal à aller vers quelqu’un que vous trouvez intéressant et à entamer une conversation.",
#             "Vous n’aimez pas particulièrement les discussions portant sur les différentes interprétations des œuvres créatives.",
#             "Vous accordez la priorité aux faits plutôt qu’aux sentiments des gens lorsque vous déterminez une ligne de conduite.",
#             "Vous laissez souvent la journée se dérouler sans aucun planning.",
#             "Vous vous souciez rarement de faire bonne impression auprès des gens que vous rencontrez.",
#             "Vous appréciez participer à des activités en équipe.",
#             "Vous aimez expérimenter des approches nouvelles et non testées.",
#             "Vous attachez plus d’importance à la sensibilité qu’à l’honnêteté.",
#             "Vous êtes en quête permanente de nouvelles expériences et de nouveaux domaines de connaissances à approfondir.",
#             "Vous avez tendance à vous inquiéter que les choses aillent de mal en pis.",
#             "Vous appréciez davantage les passe-temps ou les activités solitaires que ceux et celles en groupe.",
#             "Vous ne vous voyez pas exercer un métier d’écrivain(e) de fiction.",
#             "Vous préconisez des décisions efficaces, même si cela implique de faire abstraction de certains aspects émotionnels.",
#             "Vous préférez vous acquitter de vos tâches avant de vous détendre.",
#             "En cas de désaccord, vous privilégiez la défense de votre point de vue au détriment des sentiments d’autrui.",
#             "Vous attendez généralement que les autres se présentent en premier lors des réunions sociales.",
#             "Votre humeur peut changer très rapidement.",
#             "Vous ne vous laissez pas facilement influencer par des arguments émotionnels.",
#             "Vous vous retrouvez souvent à faire les choses à la dernière minute.",
#             "Vous aimez débattre de dilemmes éthiques.",
#             "Vous préférez généralement être entouré que seul.",
#             "Vous vous lassez ou perdez tout intérêt lorsque la discussion devient très théorique.",
#             "En cas de conflit entre les faits et les sentiments, vous suivez généralement votre cœur.",
#             "Vous avez du mal à maintenir un planning de travail ou d’études cohérent.",
#             "Vous remettez rarement en question les choix que vous avez faits.",
#             "Vos amis vous décriraient comme étant enjoué(e) et extraverti(e)."
#         ]
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             answers = data.get("answers")
#             student_id = request.session.get("student_id")

#             if not student_id:
#                 return JsonResponse({"success": False, "error": "Student not found in session."})

#             student = Student.objects.get(id=student_id)
#             TestResult.objects.create(student=student, answers=answers)

#             return JsonResponse({"success": True, "message": "Test submitted successfully!"})
#         except Exception as e:
#             return JsonResponse({"success": False, "error": str(e)})

#     return render(request, "test.html", {"questions": questions})
