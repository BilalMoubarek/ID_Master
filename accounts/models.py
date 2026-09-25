from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = (('admin', 'Administrateur'), ('professor', 'Professeur'), ('etudiant', 'Étudiant'))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    numero_cef = models.CharField(max_length=50, blank=True, null=True, verbose_name="N° Inscription (CEF)")
    last_activity = models.DateTimeField(default=timezone.now)

    def is_online(self):
        return timezone.now() - self.last_activity < timezone.timedelta(minutes=5)

    def __str__(self): return self.username

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class SiteSetting(models.Model):
    is_maintenance = models.BooleanField(default=False)

    def __str__(self):
        return f"Mode Maintenance : {self.is_maintenance}"

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"De {self.sender.username} à {self.receiver.username}"

