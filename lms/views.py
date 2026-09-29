from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Course, Announcement, DocumentScolarite
# Zidna Notification w Absence hna
from .models import Course, Announcement, DocumentScolarite, Notification, Absence 
# Zidna CustomUser hna bach yqdr yjib l'etudiant fih l'absence
from accounts.models import CustomUser
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import CahierTexte, SupportTicket
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import datetime
from .models import ProjetStagiaire
from .models import ForumQuestion, ForumAnswer
from .models import Equipment, EquipmentReservation
from .models import StudentScore
from accounts.models import CustomUser
from django.db.models import Q
from .models import Course, ForumQuestion, ProjetStagiaire
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_overview(request):
    data = {
        "status": "success",
        "message": "Welcome to ID_Master High-Performance API!",
        "architecture": "3-Tier API-First / Serverless Ready"
    }
    return Response(data)

def global_search_view(request):
    if not request.user.is_authenticated: return redirect('login')
    
    query = request.GET.get('q', '')
    courses = []
    questions = []
    projets = []
    
    if query:
        # كنقلبو فالعناوين أو الوصف
        courses = Course.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
        questions = ForumQuestion.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
        projets = ProjetStagiaire.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
        
    return render(request, 'lms/search_results.html', {
        'query': query,
        'courses': courses,
        'questions': questions,
        'projets': projets
    })

def leaderboard_view(request):
    if not request.user.is_authenticated: return redirect('login')
    
    # كنتأكدو بلي كاع الطلبة عندهم سجل ديال النقاط باش ما يعطيناش إيرور
    students = CustomUser.objects.filter(role='etudiant')
    for student in students:
        StudentScore.objects.get_or_create(student=student)
        
    # كنجيبو الترتيب من النقطة الكبيرة للصغيرة
    leaderboard = StudentScore.objects.all().order_by('-points')
    
    return render(request, 'lms/leaderboard.html', {'leaderboard': leaderboard})

def equipments_view(request):
    if not request.user.is_authenticated: return redirect('login')
    
    # ملي الطالب كيسيفط طلب الحجز
    if request.method == 'POST':
        equipment_id = request.POST.get('equipment_id')
        expected_return = request.POST.get('expected_return')
        
        if equipment_id and expected_return:
            equip = get_object_or_404(Equipment, id=equipment_id)
            EquipmentReservation.objects.create(
                student=request.user,
                equipment=equip,
                expected_return=expected_return
                # status par défaut هو 'En attente'
            )
            return redirect('equipments')
            
    equipments = Equipment.objects.all()
    my_reservations = EquipmentReservation.objects.filter(student=request.user).order_by('-request_date')
    
    return render(request, 'lms/equipments.html', {
        'equipments': equipments,
        'my_reservations': my_reservations
    })

# الدالة الأولى: عرض الأسئلة وطرح سؤال جديد
def forum_view(request):
    if not request.user.is_authenticated: return redirect('login')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            ForumQuestion.objects.create(title=title, content=content, author=request.user)
            return redirect('forum')
            
    questions = ForumQuestion.objects.all().order_by('-created_at')
    return render(request, 'lms/forum.html', {'questions': questions})

# الدالة الثانية: الدخول لسؤال محدد لإضافة جواب
def forum_detail_view(request, question_id):
    if not request.user.is_authenticated: return redirect('login')
    
    question = get_object_or_404(ForumQuestion, id=question_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            ForumAnswer.objects.create(question=question, author=request.user, content=content)
            return redirect('forum_detail', question_id=question.id)
            
    return render(request, 'lms/forum_detail.html', {'question': question})

# ==========================================
# 1. COURS & TPs
# ==========================================
def courses_list(request):
    if not request.user.is_authenticated: return redirect('login')
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'lms/courses_list.html', {'courses': courses})

def upload_course(request):
    if not request.user.is_authenticated: return redirect('login')
    if getattr(request.user, 'role', '') == 'etudiant': return redirect('courses_list')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        file = request.FILES.get('file')
        group_name = request.POST.get('group_name', 'ID 101')
        if title and file:
            Course.objects.create(title=title, description=description, file=file, uploaded_by=request.user, group_name=group_name)
            return redirect('courses_list')
    return render(request, 'lms/upload_course.html')

def delete_course(request, course_id):
    if not request.user.is_authenticated: return redirect('login')
    course = get_object_or_404(Course, id=course_id)
    if request.user == course.uploaded_by or request.user.is_superuser or getattr(request.user, 'role', '') == 'admin':
        course.delete()
    return redirect('courses_list')

def cahier_texte_view(request):
    cahiers = CahierTexte.objects.all().order_by('-date')
    if request.method == 'POST' and (request.user.role == 'professeur' or request.user.is_superuser):
        title = request.POST.get('title')
        module = request.POST.get('module')
        content = request.POST.get('content')
        if title and content:
            CahierTexte.objects.create(title=title, module=module, content=content, professor=request.user)
            return redirect('cahier_texte')
    return render(request, 'lms/cahier_texte.html', {'cahiers': cahiers})

@login_required
def attestation_view(request):
    # كنجيبو معلومات الطالب اللي مكونيكتي دابا
    context = {
        'date_edition': datetime.date.today(),
        'annee_scolaire': '2026/2027', # تقدر تردها ديناميكية
        'filiere': 'Infrastructure Digitale', # التخصص ديالكم فـ ISFP
        'etablissement': 'ISFP - OFPPT'
    }
    return render(request, 'lms/attestation.html', context)

# صفحة مكتبة الكتب
def bibliotheque_view(request):
    return render(request, 'lms/bibliotheque.html')

# تذاكر الصيانة (IT Support)
def support_tickets_view(request):
    tickets = SupportTicket.objects.all().order_by('-created_at')
    if request.method == 'POST' and request.user.is_authenticated:
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        if subject and description:
            SupportTicket.objects.create(student=request.user, subject=subject, description=description)
            return redirect('support_tickets')
    return render(request, 'lms/support_tickets.html', {'tickets': tickets})


# ==========================================
# 2. RÉSEAU ISFP (FEED & ANNONCES)
# ==========================================
def feed_view(request):
    if not request.user.is_authenticated: return redirect('login')
    
    # مسح المنشورات اللي سالا الوقت ديالها
    Announcement.objects.filter(expires_at__lt=timezone.now()).delete()

    # إضافة منشور جديد (خاص بالأساتذة والإدارة)
    if request.method == 'POST' and getattr(request.user, 'role', '') != 'etudiant':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        expire_in = request.POST.get('expire_in')
        
        if content:
            announcement = Announcement(author=request.user, content=content, image=image)
            if expire_in == '2days':
                announcement.expires_at = timezone.now() + timedelta(days=2)
            announcement.save()
            return redirect('feed')
            
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'lms/feed.html', {'announcements': announcements})

def delete_announcement(request, post_id):
    if not request.user.is_authenticated: return redirect('login')
    post = get_object_or_404(Announcement, id=post_id)
    if request.user == post.author or request.user.is_superuser or getattr(request.user, 'role', '') == 'admin':
        post.delete()
    return redirect('feed')


# ==========================================
# 3. SCOLARITÉ ISFP (AFFICHAGE)
# ==========================================
def emploi_view(request):
    if not request.user.is_authenticated: return redirect('login')
    docs = DocumentScolarite.objects.filter(doc_type='emploi').order_by('-uploaded_at')
    return render(request, 'lms/emploi.html', {'docs': docs})

def resultats_view(request):
    if not request.user.is_authenticated: return redirect('login')
    docs = DocumentScolarite.objects.filter(doc_type='resultats').order_by('-uploaded_at')
    return render(request, 'lms/resultats.html', {'docs': docs})

def stages_view(request):
    if not request.user.is_authenticated: return redirect('login')
    docs = DocumentScolarite.objects.filter(doc_type='stages').order_by('-uploaded_at')
    return render(request, 'lms/stages.html', {'docs': docs})


# ==========================================
# 4. SCOLARITÉ ISFP (GESTION ADMIN/PROF)
# ==========================================
def upload_scolarite(request):
    if not request.user.is_authenticated or getattr(request.user, 'role', '') == 'etudiant': 
        return redirect('student_dashboard')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        doc_type = request.POST.get('doc_type')
        file = request.FILES.get('file')
        if title and doc_type and file:
            DocumentScolarite.objects.create(title=title, doc_type=doc_type, file=file, uploaded_by=request.user)
            
    return redirect('dashboard')

def delete_scolarite(request, doc_id):
    if not request.user.is_authenticated or getattr(request.user, 'role', '') == 'etudiant': 
        return redirect('student_dashboard')
        
    doc = get_object_or_404(DocumentScolarite, id=doc_id)
    if request.user == doc.uploaded_by or request.user.is_superuser or getattr(request.user, 'role', '') == 'admin':
        doc.delete()
        
    # الرجوع لنفس الصفحة اللي مسح منها (Dashboard)
    return redirect('dashboard')

def projets_view(request):
    projets = ProjetStagiaire.objects.all().order_by('-created_at')
    if request.method == 'POST' and request.user.is_authenticated:
        title = request.POST.get('title')
        description = request.POST.get('description')
        students = request.POST.get('students')
        github_link = request.POST.get('github_link')
        image = request.FILES.get('image')
        
        if title and description:
            ProjetStagiaire.objects.create(
                title=title, description=description, students=students, 
                github_link=github_link, image=image
            )
            return redirect('projets_stagiaires')
            
    return render(request, 'lms/projets.html', {'projets': projets})


# ==========================================
# 5. NOTIFICATIONS & ABSENCES
# ==========================================
def mark_notifications_read(request):
    if request.user.is_authenticated:
        # كاع الإشعارات ديال هاد اليوزر نردوهام مقروءة
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    # كيرجعو لنفس الصفحة اللي كان فيها
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

def projets_view(request):
    projets = ProjetStagiaire.objects.all().order_by('-created_at')
    if request.method == 'POST' and request.user.is_authenticated:
        title = request.POST.get('title')
        description = request.POST.get('description')
        students = request.POST.get('students')
        github_link = request.POST.get('github_link')
        image = request.FILES.get('image')
        
        if title and description:
            ProjetStagiaire.objects.create(
                title=title, description=description, students=students, 
                github_link=github_link, image=image
            )
            return redirect('projets_stagiaires')
            
    return render(request, 'lms/projets.html', {'projets': projets})

def add_absence(request):
    if not request.user.is_authenticated or getattr(request.user, 'role', '') == 'etudiant': 
        return redirect('student_dashboard')
        
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        heures = request.POST.get('heures')
        module = request.POST.get('module')
        date_abs = request.POST.get('date_abs')
        
        if student_id and heures:
            student = get_object_or_404(CustomUser, id=student_id)
            Absence.objects.create(
                student=student, heures=heures, module=module, 
                date_absence=date_abs, recorded_by=request.user
            )
            # صيفط إشعار للطالب
            Notification.objects.create(
                user=student, 
                message=f"⚠️ Nouvelle absence enregistrée : {heures}H en {module}.",
                link="/mon-espace/"
            )
            
    return redirect('stagiaires') # غنرجعوه لصفحة المتدربين منين دخل الغياب