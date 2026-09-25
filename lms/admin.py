from django.contrib import admin
from .models import Course
from django.contrib import admin
from .models import Course, Announcement, DocumentScolarite, Notification, Absence, CahierTexte, SupportTicket, ProjetStagiaire
from .models import ForumQuestion, ForumAnswer, Equipment, EquipmentReservation, StudentScore

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'group_name', 'uploaded_by', 'created_at')
    list_filter = ('group_name', 'created_at')
    search_fields = ('title', 'description')

admin.site.register(Notification)
admin.site.register(Absence)
admin.site.register(CahierTexte)
admin.site.register(SupportTicket)
admin.site.register(ProjetStagiaire)
admin.site.register(ForumQuestion)
admin.site.register(ForumAnswer)
admin.site.register(Equipment)
admin.site.register(EquipmentReservation)
admin.site.register(StudentScore)