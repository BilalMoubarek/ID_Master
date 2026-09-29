from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Sum
from accounts.models import CustomUser, Message, SiteSetting
from lms.models import Course, Announcement, StudentRecord
from django.contrib import messages
from .forms import CustomUserCreationForm
import csv
from django.http import HttpResponse
from rest_framework.decorators import api_view

# الصفحة الرئيسية (مفتوحة للعموم - Public)
def home_view(request):
    # إيلا كان اليوزر مسجل دخول ديجا، نردوه للداشبورد ديالو نيشان
    if request.user.is_authenticated:
        return redirect('student_dashboard') if getattr(request.user, 'role', '') == 'etudiant' else redirect('dashboard')
        
    courses = Course.objects.all()[:4] # عينة من الدروس للعموم
    announcements = Announcement.objects.all()[:5] # آخر الإعلانات
    
    context = {
        'courses': courses,
        'announcements': announcements,
    }
    # هنا عزلنا اسم الملف فـ templates (تأكد واش سميتو home.html ولا index.html فـ folders ديالك)
    return render(request, 'accounts/home.html', context)

def toggle_maintenance(request):
    if request.user.is_authenticated and request.user.is_superuser:
        setting, created = SiteSetting.objects.get_or_create(id=1)
        setting.is_maintenance = not setting.is_maintenance
        setting.save()
    return redirect('dashboard')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('student_dashboard') if getattr(request.user, 'role', '') == 'etudiant' else redirect('dashboard')
    error, success = None, request.session.pop('success', None)
    if request.method == 'POST':
        u, p = request.POST.get('username'), request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return redirect('student_dashboard') if getattr(user, 'role', '') == 'etudiant' else redirect('dashboard')
        error = "Identifiants incorrects ou compte non approuvé."
    return render(request, 'accounts/login.html', {'error': error, 'success': success})

def feed_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.method == 'POST':
        post_content = request.POST.get('post_content')
        if post_content:
            messages.success(request, "🎉 Publication partagée avec succès sur le campus !")
            return redirect('feed')
            
    return render(request, 'accounts/feed.html')

def export_stagiaires_csv(request):
    if not request.user.is_authenticated or getattr(request.user, 'role', '') == 'etudiant':
        return redirect('dashboard')
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stagiaires_isfp.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nom d\'utilisateur', 'Nom', 'Prénom', 'CEF', 'Rôle'])
    
    stagiaires = CustomUser.objects.all()
    for s in stagiaires:
        writer.writerow([s.id, s.username, s.last_name, s.first_name, s.numero_cef, s.role])
        
    return response

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # كيحبس الكونط حتى يوافق عليه الأدمين (بلال)
            user.save()
            messages.success(request, "🎉 Inscription réussie ! Votre compte est en attente d'approbation par Bilal (Admin).")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# الداشبورد ديال الأستاذ والأدمين
def dashboard_view(request):
    if not request.user.is_authenticated or getattr(request.user, 'role', '') == 'etudiant': return redirect('student_dashboard')
    students = CustomUser.objects.filter(role='etudiant', is_active=True).select_related('record')
    setting, _ = SiteSetting.objects.get_or_create(id=1)
    return render(request, 'accounts/admin_dashboard.html', {'students': students, 'setting': setting})

# حفظ النقط والغياب من الأستاذ
def save_grades(request):
    if request.method == 'POST' and getattr(request.user, 'role', '') != 'etudiant':
        for key, value in request.POST.items():
            if key.startswith('abs_'):
                sid = key.split('_')[1]
                rec, _ = StudentRecord.objects.get_or_create(student_id=sid)
                rec.absences = value or 0
                rec.note_python = request.POST.get(f'py_{sid}') or 0.00
                rec.note_linux = request.POST.get(f'lin_{sid}') or 0.00
                rec.note_reseau = request.POST.get(f'res_{sid}') or 0.00
                rec.save()
    return redirect('dashboard')

def student_dashboard_view(request):
    if not request.user.is_authenticated or getattr(request.user, 'role', '') != 'etudiant': return redirect('dashboard')
    record, _ = StudentRecord.objects.get_or_create(student=request.user)
    return render(request, 'accounts/student_dashboard.html', {'record': record})

def stagiaires_list(request):
    if not request.user.is_authenticated: return redirect('login')
    
    stagiaires = CustomUser.objects.filter(role='etudiant').annotate(
        total_absences=Sum('absences__heures')
    )

    return render(request, 'accounts/stagiaires_list.html', {'stagiaires': stagiaires})

def formateurs_list(request):
    if not request.user.is_authenticated: return redirect('login')
    formateurs = CustomUser.objects.filter(role='professor')
    return render(request, 'accounts/formateurs_list.html', {'formateurs': formateurs})

def settings_view(request):
    if not request.user.is_authenticated: return redirect('login')
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.numero_cef = request.POST.get('numero_cef', '')
        if 'profile_picture' in request.FILES: request.user.profile_picture = request.FILES['profile_picture']
        request.user.save()
        return redirect('settings')
    return render(request, 'accounts/settings.html')

def messages_view(request, user_id=None):
    if not request.user.is_authenticated: return redirect('login')
    
    users = CustomUser.objects.exclude(id=request.user.id)
    active_chat_user = None
    chat_messages = []
    
    if user_id:
        active_chat_user = get_object_or_404(CustomUser, id=user_id)
        Message.objects.filter(sender=active_chat_user, receiver=request.user, is_read=False).update(is_read=True)
        chat_messages = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=active_chat_user)) |
            (Q(sender=active_chat_user) & Q(receiver=request.user))
        ).order_by('timestamp')
        
    if request.method == 'POST' and active_chat_user:
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, receiver=active_chat_user, content=content)
            return redirect('chat', user_id=active_chat_user.id)
            
    return render(request, 'accounts/messages.html', {
        'users': users,
        'active_chat_user': active_chat_user,
        'chat_messages': chat_messages
    })