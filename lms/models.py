from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db import models
from accounts.models import CustomUser

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='tps/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=100, default="ID 101")
    created_at = models.DateTimeField(auto_now_add=True)

class Announcement(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

class StudentRecord(models.Model):
    student = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='record')
    absences = models.IntegerField(default=0)
    note_python = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    note_linux = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    note_reseau = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

class DocumentScolarite(models.Model):
    DOC_TYPES = (
        ('emploi', 'Emploi du Temps'),
        ('resultats', 'Résultats & Examens'),
        ('stages', 'Document de Stage'),
    )
    title = models.CharField(max_length=200)
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES)
    file = models.FileField(upload_to='scolarite/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class CahierTexte(models.Model):
    title = models.CharField(max_length=200)
    module = models.CharField(max_length=100)
    content = models.TextField()
    professor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'professeur'}, related_name='lms_cahiers')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.date}"
    
# 2. تذاكر صيانة العتاد (IT Support Tickets)
class SupportTicket(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.CharField(max_length=150)
    description = models.TextField()
    status = models.CharField(max_length=20, default='En attente') # En attente, Résolu
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"

# زيد هادو لتحت فملف lms/models.py

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True) # الرابط فين غيمشي ملي يكليكي
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif pour {self.user.username}: {self.message}"

class Absence(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='absences')
    date_absence = models.DateField(default=timezone.now)
    heures = models.IntegerField(default=2) # شحال من ساعة غاب
    module = models.CharField(max_length=100, default="Général")
    justifiee = models.BooleanField(default=False)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='absences_enregistrees')

    def __str__(self):
        return f"{self.student.username} - {self.heures}H le {self.date_absence}"

class ProjetStagiaire(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    students = models.CharField(max_length=255)
    github_link = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='projets/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# ==========================================
# 2. FORUM Q&A (أسئلة وأجوبة)
# ==========================================
class ForumQuestion(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class ForumAnswer(models.Model):
    question = models.ForeignKey(ForumQuestion, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False) # باش الأستاذ يماركي الجواب الصحيح

# ==========================================
# 3. RÉSERVATION DE MATÉRIEL IT (حجز المعدات)
# ==========================================
class Equipment(models.Model):
    name = models.CharField(max_length=100) # مثال: Câble Console, Switch Cisco 2960
    description = models.TextField(blank=True)
    total_quantity = models.IntegerField(default=1)
    available_quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.name} ({self.available_quantity} dispo)"

class EquipmentReservation(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    expected_return = models.DateField()
    status = models.CharField(max_length=20, default='En attente') # En attente, Approuvé, Retourné

    def __str__(self):
        return f"{self.student.username} - {self.equipment.name}"

# ==========================================
# 4. LEADERBOARD & POINTS (ترتيب الطلبة)
# ==========================================
class StudentScore(models.Model):
    student = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='score')
    points = models.IntegerField(default=0)
    badges = models.CharField(max_length=255, blank=True, help_text="Ex: Cisco Master, Linux Pro")

    def __str__(self):
        return f"{self.student.username} - {self.points} pts"