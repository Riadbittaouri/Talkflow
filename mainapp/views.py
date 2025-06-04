# mainapp/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, Http404, HttpResponse
from django.conf import settings
# from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required

from .forms import TeacherSignupForm, TeacherLoginForm, ClassroomForm, StudentForm
from .models import Classroom, Student, TestResult, Group_student
from .gmail_auth import get_gmail_credentials, send_email_via_gmail

from math import ceil
import random
import string
import json

groups = {
    'harmonizer': ['Warm', 'Compassionate', 'Sensitive'],
    'thinker':    ['Logical', 'Responsible', 'Organized'],
    'persister':  ['Conscientious', 'Observant', 'Committed'],
    'promoter':   ['Adaptable', 'Charismatic', 'Action-oriented'],
    'imaginer':   ['Calm', 'Reflective', 'Imaginative'],
    'rebel':      ['Creative', 'Spontaneous', 'Playful']
}

# Email templates for each personality (all three languages)
EMAIL_TEMPLATES = {
    'thinker': {
        'subject': 'Selon le test, votre personnalité est : Thinker',
        'body': (
            "Thinker / Travaillomane / المفكر\n\n"
            "Main Characteristics:\n"
            "• Logical, organized, and responsible.\n"
            "• Makes decisions based on facts and analysis.\n"
            "• Likes structure and precision.\n\n"
            "Main psychological need: Recognition of your work and ideas.\n"
            "Communication Channel: Factual → Prefers clear, logical, and structured communication with precise facts and data.\n"
            "Example in a stressful situation:\n"
            "\"I really appreciate the quality of your work on this file. To move forward efficiently, could you explain your logic behind this approach?\"\n"
            "➝ This values your expertise and brings the discussion back to a rational ground.\n\n"
            "المفكر\n"
            "السمات الرئيسية:\n"
            "• منطقي، منظم، ومسؤول.\n"
            "• يتخذ قرارات بناءً على الحقائق والتحليل.\n"
            "• يحب الهيكلة والدقة.\n\n"
            "الاحتياج النفسي الرئيسي: الاعتراف بعمله وأفكاره.\n"
            "قناة التواصل: واقعي: يفضل التواصل الواضح، المنطقي، والمنظم مع حقائق وبيانات دقيقة.\n"
            "مثال في موقف ضغط:\n"
            "\"أنا أقدّر حقًا جودة عملك في هذا الملف. للمضي قدمًا بكفاءة، هل يمكنك شرح منطقك وراء هذا النهج؟\"\n"
            "هذا يقدّر خبرتك ويعيد النقاش إلى أرضية عقلانية.\n\n"
            "Travaillomane\n"
            "Caractéristiques principales:\n"
            "• Logique, organisé et responsable.\n"
            "• Prend des décisions basées sur les faits et l'analyse.\n"
            "• Aime la structure et la précision.\n\n"
            "Besoin psychologique principal : la reconnaissance de son travail et de ses idées.\n"
            "Canal de communication: Factuel → Il préfère une communication claire, logique et structurée avec des faits et des données précises.\n"
            "Exemple en situation de stress:\n"
            "\"J'apprécie vraiment la qualité de ton travail sur ce dossier. Pour avancer efficacement, pourrais-tu m'expliquer ta logique derrière cette approche ?\"\n"
            "➝ Cela valorise ton expertise et ramène la discussion sur un terrain rationnel."
        )
    },
    'persister': {
        'subject': 'Selon le test, votre personnalité est : Persister',
        'body': (
            "Persister / Persévérant / المثابر\n\n"
            "Main Characteristics:\n"
            "• Conscientious, committed, and observant.\n"
            "• Has strong opinions based on values and beliefs.\n"
            "• Seeks loyalty and recognition of their opinions.\n\n"
            "Main psychological need: Recognition of your values and commitment.\n"
            "Communication Channel: Factual → Appreciates discussions based on principles, values, and well-constructed arguments.\n"
            "Example in a stressful situation:\n"
            "\"I know this subject is important to you, and I appreciate your commitment. Could you share your point of view in more detail so we can find a solution together?\"\n"
            "➝ This shows that your values are respected and encourages you to express your opinion.\n\n"
            "المثابر\n"
            "السمات الرئيسية:\n"
            "• دقيق، ملتزم، وملاحظ جيد.\n"
            "• لديه آراء قوية مبنية على القيم والمعتقدات.\n"
            "• يسعى إلى الولاء والاعتراف بآرائه.\n\n"
            "الاحتياج النفسي الرئيسي: الاعتراف بقيمه والتزامه.\n"
            "قناة التواصل: واقعي: يفضل مناقشات قائمة على المبادئ والقيم والحجج المنطقية.\n"
            "مثال في موقف ضغط:\n"
            "\"أعلم أن هذا الموضوع مهم بالنسبة لك، وأقدّر التزامك. هل يمكنك مشاركة وجهة نظرك بمزيد من التفاصيل حتى نجد حلًا معًا؟\"\n"
            "هذا يظهر أن قيمك محترمة ويشجعك على التعبير عن رأيك.\n\n"
            "Persévérant\n"
            "Caractéristiques principales:\n"
            "• Consciencieux, engagé et observateur.\n"
            "• A des opinions fortes basées sur ses valeurs et ses croyances.\n"
            "• Recherche la loyauté et la reconnaissance de ses opinions.\n\n"
            "Besoin psychologique principal : la reconnaissance de ses valeurs, de son engagement.\n"
            "Canal de communication: Factuel → Apprécie une discussion basée sur des principes, des valeurs et une argumentation bien construite.\n"
            "Exemple en situation de stress:\n"
            "\"Je sais que ce sujet est important pour toi et j’apprécie ton engagement. Peux-tu partager ton point de vue plus en détail pour qu'on trouve une solution ensemble ?\"\n"
            "➝ Cela montre que tes valeurs sont respectées et t'encourage à exprimer ton opinion."
        )
    },
    'rebel': {
        'subject': 'Selon le test, votre personnalité est : Rebel',
        'body': (
            "Rebel / Rebelle / المتمرد\n\n"
            "Main Characteristics:\n"
            "• Creative, playful, and spontaneous.\n"
            "• Reacts to situations with enthusiasm or opposition.\n"
            "• Enjoys having fun and seeks a dynamic environment.\n\n"
            "Main psychological need: Stimulation and positive interactions.\n"
            "Communication Channel: Playful → Prefers light, fun, and energetic communication.\n"
            "Example in a stressful situation:\n"
            "\"Wow, this situation is really tricky! What if we tried a completely original solution, just to see?\"\n"
            "➝ This stimulates your creative spirit and motivates you to regain a positive attitude.\n\n"
            "المتمرد\n"
            "السمات الرئيسية:\n"
            "• مبدع، مرح، وعفوي.\n"
            "• يتفاعل مع المواقف بحماس أو معارضة.\n"
            "• يحب المرح ويبحث عن بيئة ديناميكية.\n\n"
            "الاحتياج النفسي الرئيسي: التحفيز والتفاعلات الإيجابية.\n"
            "قناة التواصل: مرح: يفضل التواصل الخفيف والممتع والمليء بالطاقة.\n"
            "مثال في موقف ضغط:\n"
            "\"يا له من موقف معقد! ماذا لو جربنا حلاً جديدًا تمامًا، لمجرد التجربة؟\"\n"
            "➝ هذا يحفز روحك الإبداعية ويعيد لك الطاقة الإيجابية.\n\n"
            "Rebelle\n"
            "Caractéristiques principales:\n"
            "• Créatif, ludique et spontané.\n"
            "• Réagit aux situations avec enthousiasme ou opposition.\n"
            "• Aime s’amuser et recherche un environnement dynamique.\n\n"
            "Besoin psychologique principal : la stimulation et les interactions positives.\n"
            "Canal de communication: Ludique → Il privilégie une communication légère, amusante et pleine d’énergie.\n"
            "Exemple en situation de stress:\n"
            "\"Ouf, cette situation est un vrai casse-tête ! Si on essayait une solution complètement originale, juste pour voir ?\"\n"
            "➝ Cela stimule ton esprit créatif et te motive à retrouver une attitude positive."
        )
    },
    'promoter': {
        'subject': 'Selon le test, votre personnalité est : Promoter',
        'body': (
            "Promoter / Promoteur / المروج\n\n"
            "Main Characteristics:\n"
            "• Adaptable, charismatic, and action-oriented.\n"
            "• Makes decisions quickly based on opportunities.\n"
            "• Loves challenges and taking risks.\n\n"
            "Main psychological need: Excitement and challenge.\n"
            "Communication Channel: Directive → Prefers direct communication focused on action and results.\n"
            "Example in a stressful situation:\n"
            "\"I know you are excellent at finding quick solutions. If we focus on immediate action, what would be your first step?\"\n"
            "➝ This gives you a concrete challenge and helps you regain control.\n\n"
            "المروج\n"
            "السمات الرئيسية:\n"
            "• متكيف، جذاب، وموجه نحو العمل.\n"
            "• يتخذ قرارات سريعة بناءً على الفرص.\n"
            "• يحب التحديات والمخاطرة.\n\n"
            "الاحتياج النفسي الرئيسي: الإثارة والتحدي.\n"
            "قناة التواصل: مباشر: يفضل التواصل المباشر الموجه نحو العمل والنتائج.\n"
            "مثال في موقف ضغط:\n"
            "\"أعلم أنك بارع في إيجاد الحلول السريعة. إذا ركزنا على الفعل الفوري، ما هي خطوتك الأولى؟\"\n"
            "➝ هذا يعطيك تحديًا ملموسًا ويساعدك على استعادة السيطرة.\n\n"
            "Promoteur\n"
            "Caractéristiques principales:\n"
            "• Adaptable, charmeur et orienté vers l’action.\n"
            "• Prend des décisions rapidement en fonction des opportunités.\n"
            "• Aime le challenge et la prise de risque.\n\n"
            "Besoin psychologique principal : l’excitation et le challenge.\n"
            "Canal de communication: Directif → Il privilégie une communication directe, orientée vers l’action et les résultats.\n"
            "Exemple en situation de stress:\n"
            "\"Je sais que tu es excellent pour trouver des solutions rapides. Si on se concentrait sur l’action immédiate, quelle serait ta première étape ?\"\n"
            "➝ Cela te donne un défi concret et te permet de reprendre le contrôle."
        )
    },
    'harmonizer': {
        'subject': 'Selon le test, votre personnalité est : Harmonizer',
        'body': (
            "Harmonizer / Empathique / المتناغم\n\n"
            "Main Characteristics:\n"
            "• Warm, compassionate, and sensitive.\n"
            "• Acts based on human relationships and emotions.\n"
            "• Seeks harmony and the well-being of others.\n\n"
            "Main psychological need: Recognition of your person and emotions.\n"
            "Communication Channel: Nurturing → Prefers gentle, caring, and affectionate communication.\n"
            "Example in a stressful situation:\n"
            "\"I see that this situation is difficult for you. Know that your well-being is important, and I am here to listen.\"\n"
            "➝ This provides you with comfort and helps you regain calm.\n\n"
            "المتناغم\n"
            "السمات الرئيسية:\n"
            "• دافئ، متعاطف، وحساس.\n"
            "• يتصرف بناءً على العلاقات الإنسانية والعواطف.\n"
            "• يسعى إلى الانسجام ورفاهية الآخرين.\n\n"
            "الاحتياج النفسي الرئيسي: الاعتراف بشخصيتك ومشاعرك.\n"
            "قناة التواصل: راعي: يفضل التواصل اللطيف، الحنون، والعاطفي.\n"
            "مثال في موقف ضغط:\n"
            "\"أرى أن هذا الوضع صعب عليك. اعلم أن رفاهيتك مهمة وأنا هنا للاستماع إليك.\"\n"
            "➝ هذا يوفر لك الراحة ويساعدك على استعادة الهدوء.\n\n"
            "Empathique\n"
            "Caractéristiques principales:\n"
            "• Chaleureux, compatissant et sensible.\n"
            "• Oriente ses actions en fonction des relations humaines et des émotions.\n"
            "• Recherche l’harmonie et le bien-être des autres.\n\n"
            "Besoin psychologique principal: la reconnaissance de ta personne et de tes émotions.\n"
            "Canal de communication: Nourricier → Apprécie une communication douce, bienveillante et affectueuse.\n"
            "Exemple en situation de stress:\n"
            "\"Je vois que cette situation est difficile pour toi. Sache que ton bien-être est important et que je suis là pour t’écouter.\"\n"
            "➝ Cela te procure du réconfort et t'aide à retrouver ton calme."
        )
    },
    'imaginer': {
        'subject': 'Selon le test, votre personnalité est : Imaginer',
        'body': (
            "Imaginer / Rêveur / الحالم\n\n"
            "Main Characteristics:\n"
            "• Calm, reflective, and imaginative.\n"
            "• Likes working alone and projecting into their inner world.\n"
            "• Functions well with clear instructions and time to think.\n\n"
            "Main psychological need: Time and space to think.\n"
            "Communication Channel: Reflective → Prefers calm communication, with pauses and space for introspection.\n"
            "Example in a stressful situation:\n"
            "\"Take the time you need to think about it. When you're ready, let me know how you see things.\"\n"
            "➝ This gives you the necessary space to regain calm.\n\n"
            "الحالم\n"
            "السمات الرئيسية:\n"
            "• هادئ، متأمل، وخيالي.\n"
            "• يحب العمل بمفرده والانغماس في عالمه الداخلي.\n"
            "• يعمل بشكل جيد مع تعليمات واضحة ووقت للتفكير.\n\n"
            "الاحتياج النفسي الرئيسي: الوقت والمساحة للتفكير.\n"
            "قناة التواصل: تفكري: يفضل التواصل الهادئ، مع فترات توقف ومساحة للتأمل.\n"
            "مثال في موقف ضغط:\n"
            "\"خذ وقتك في التفكير في الأمر. عندما تكون جاهزًا، أخبرني كيف ترى الأمور.\"\n"
            "➝ هذا يمنحك المساحة اللازمة لاستعادة الهدوء.\n\n"
            "Rêveur\n"
            "Caractéristiques principales:\n"
            "• Calme, réfléchi et imaginatif.\n"
            "• Aime travailler seul et se projeter dans son monde intérieur.\n"
            "• Fonctionne bien avec des instructions claires et du temps pour réfléchir.\n\n"
            "Besoin psychologique principal: le temps et l’espace pour penser.\n"
            "Canal de communication: Réfléchi → Il apprécie une communication posée, avec des pauses et un espace pour l’introspection.\n"
            "Exemple en situation de stress:\n"
            "\"Prends le temps dont tu as besoin pour y réfléchir. Quand tu seras prêt, dis-moi comment tu vois les choses.\"\n"
            "➝ Cela te donne l’espace nécessaire pour retrouver ton calme."
        )
    }
}


def home(request):
    signup_form  = TeacherSignupForm()
    login_form   = TeacherLoginForm()
    student_form = StudentForm()
    return render(request, "home.html", {
        "signup_form": signup_form,
        "login_form":  login_form,
        "student_form": student_form
    })


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
            email    = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user     = authenticate(request, username=email, password=password)
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
                email = student.email

                if Student.objects.filter(classroom=classroom, email=email).exists():
                    return render(request, 'home.html', {
                        'student_form': student_form,
                        'error': 'This email has already been used for this class.'
                    })

                student.save()
                request.session['student_id'] = student.id
                return redirect('personality_test')
            else:
                return render(request, 'home.html', {
                    'student_form': student_form,
                    'error': 'Invalid student information.'
                })
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

        for group_name, characteristics in groups.items():
            for char in characteristics:
                if char in selected_characteristics:
                    scores[group_name] += 1

        max_score = max(scores.values())
        matching_groups = [grp for grp, score in scores.items() if score == max_score]
        result_group = random.choice(matching_groups) if matching_groups else None

        return render(request, 'result.html', {'result_group': scores})
    
    characteristics = randomize_characteristics()
    return render(request, 'personality_test.html', {'characteristics': characteristics})


def result(request):
    result = request.GET.get('result', '')
    context = {'result': result}
    return render(request, 'result.html', context)


def rebalance_groups(classroom):
    """
    Evenly assign students to groups in a round-robin fashion.
    Assumes that groups have already been created for the classroom.
    """
    # Get all students who have taken the test (score is not None)
    students = list(Student.objects.filter(classroom=classroom, score__isnull=False).order_by('id'))
    # Get all groups for the classroom in a defined order (e.g., by id)
    groups_list = list(classroom.groups.all().order_by('id'))
    num_groups = len(groups_list)

    # Clear existing group memberships
    for grp in groups_list:
        grp.students.clear()

    # Reassign students evenly
    for index, student in enumerate(students):
        group_index = index % num_groups  # round-robin assignment
        groups_list[group_index].students.add(student)

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

        # 1) Parse and save the student's dominant trait
        selected_characteristics = result.split(', ')
        dominant_trait = selected_characteristics[0] if selected_characteristics else None
        student.score = dominant_trait
        student.save()

        # 2) Create a TestResult record (answers + dominant_trait)
        TestResult.objects.create(
            student=student,
            answers={"selected_characteristics": selected_characteristics},
            dominant_trait=dominant_trait
        )

        # --- EMAIL BLOCK REMOVED HERE ---
        # (Everything from “# --- First email via SMTP ---” through the end of that block
        #  has been deleted.)
        #
        # if template and student.email:
        #     … (all SMTP / Gmail‐API calls) …

        # --- Group assignment logic (unchanged) ---
        available_groups = classroom.groups.all().order_by('id')
        assigned_group = None
        for grp in available_groups:
            if grp.students.count() < classroom.group_size:
                grp.students.add(student)
                assigned_group = grp
                break

        if not assigned_group:
            smallest_group = min(available_groups, key=lambda g: g.students.count(), default=None)
            if smallest_group:
                smallest_group.students.add(student)

        # --- Rebalance groups (email sending removed) ---
        all_students = Student.objects.filter(classroom=classroom)
        if all_students.filter(score__isnull=False).count() == classroom.students_count:
            rebalance_groups(classroom)

            # We no longer send the “Your group membership” e-mail to everyone:
            # for s in all_students:
            #     … (email block removed) …

        # Instead of redirecting to “/personality-test/result/”, we simply re-render the test page:
        return render(request, 'personality_test.html')

    # If not a POST, it’s an invalid request for this endpoint:
    return HttpResponse("Invalid request method.", status=400)




# def submit_result(request):
#     if request.method == 'POST':
#         student_id = request.session.get('student_id')
#         if not student_id:
#             return HttpResponse("Student not found. Please start the test again.", status=400)

#         try:
#             student = Student.objects.get(id=student_id)
#         except Student.DoesNotExist:
#             return HttpResponse("Student not found. Please start the test again.", status=400)

#         classroom = student.classroom
#         result = request.POST.get('result', '')
#         if not result:
#             return HttpResponse("No result provided.", status=400)

#         selected_characteristics = result.split(', ')
#         dominant_trait = selected_characteristics[0] if selected_characteristics else None
#         student.score = dominant_trait
#         student.save()

#         TestResult.objects.create(
#             student=student,
#             answers={"selected_characteristics": selected_characteristics},
#             dominant_trait=dominant_trait
#         )

#         # --- First email via SMTP ---
#         template = EMAIL_TEMPLATES.get(dominant_trait.lower()) if dominant_trait else None
#         if template and student.email:
#             subject = template['subject']
#             body = template['body']
#             try:
#                 creds = get_gmail_credentials()
#             except Exception as e:
#                 # Nous affichons un message d’erreur précis en dev (retourné en HttpResponse pour diagnostiquer)
#                 return HttpResponse(f"Erreur OAuth Gmail : {e}", status=500)

#             # Envoi via API Gmail
#             send_email_via_gmail(creds, student.email, subject, body)


#         # --- Group assignment logic ---
#         available_groups = classroom.groups.all().order_by('id')
#         assigned_group = None
#         for grp in available_groups:
#             if grp.students.count() < classroom.group_size:
#                 grp.students.add(student)
#                 assigned_group = grp
#                 break

#         if not assigned_group:
#             smallest_group = min(available_groups, key=lambda g: g.students.count(), default=None)
#             if smallest_group:
#                 smallest_group.students.add(student)

#         # --- Rebalance groups and second email via SMTP ---
#         all_students = Student.objects.filter(classroom=classroom)
#         if all_students.filter(score__isnull=False).count() == classroom.students_count:
#             rebalance_groups(classroom)

#             for s in all_students:
#                 student_groups = s.groups.all()
#                 if student_groups.exists():
#                     grp = student_groups.first()
#                     group_members = grp.students.exclude(id=s.id)
#                     if group_members.exists():
#                         members_info = [f"{m.first_name} - {m.score}" for m in group_members]
#                         group_message = "\n".join(members_info)
#                     else:
#                         group_message = "Vous êtes seul dans votre groupe."

#                     subject = "Votre groupe d'appartenance"
#                     message = f"Le groupe auquel vous appartenez est :\n{group_message}"
#                     if s.email:
#                         try:
#                             creds = get_gmail_credentials()
#                         except Exception as e:
#                             # Nous affichons un message d’erreur précis en dev (retourné en HttpResponse pour diagnostiquer)
#                             return HttpResponse(f"Erreur OAuth Gmail : {e}", status=500)

#                         # Envoi via API Gmail
#                         send_email_via_gmail(creds, student.email, subject, body)


#         return redirect(f'/personality-test/result/?result={result}')

#     return HttpResponse("Invalid request method.", status=400)
