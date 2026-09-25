from django.urls import path
from .views import (
    courses_list, upload_course, delete_course, feed_view, delete_announcement, 
    emploi_view, resultats_view, stages_view, upload_scolarite, delete_scolarite,
    mark_notifications_read, add_absence, cahier_texte_view, qr_presence_view, 
    bibliotheque_view, support_tickets_view, attestation_view, projets_view,
    
    # هاهما اللي زدنا دابا ديال المنتدى
    forum_view, forum_detail_view, equipments_view, leaderboard_view, global_search_view,
)

urlpatterns = [
    path('courses/', courses_list, name='courses_list'),
    path('upload/', upload_course, name='upload_course'),
    path('delete/<int:course_id>/', delete_course, name='delete_course'),
    path('feed/', feed_view, name='feed'),
    path('feed/delete/<int:post_id>/', delete_announcement, name='delete_announcement'),
    
    path('scolarite/upload/', upload_scolarite, name='upload_scolarite'),
    path('scolarite/delete/<int:doc_id>/', delete_scolarite, name='delete_scolarite'),
    path('emploi-du-temps/', emploi_view, name='emploi'),
    path('resultats-examens/', resultats_view, name='resultats'),
    path('espace-stages/', stages_view, name='stages'),

    path('cahier-texte/', cahier_texte_view, name='cahier_texte'),
    path('qr-presence/', qr_presence_view, name='qr_presence'),
    path('bibliotheque/', bibliotheque_view, name='bibliotheque'),
    path('support/', support_tickets_view, name='support_tickets'),
    path('projets/', projets_view, name='projets_stagiaires'),

    path('recherche/', global_search_view, name='global_search'),

    path('materiel/', equipments_view, name='equipments'),

    path('classement/', leaderboard_view, name='leaderboard'),

    path('forum/', forum_view, name='forum'),
    path('forum/<int:question_id>/', forum_detail_view, name='forum_detail'),

    # هاهما الروابط اللي كانو ناقصين ودارو لينا هاد المشكل
    path('notifications/read/', mark_notifications_read, name='mark_notifications_read'),
    path('absences/add/', add_absence, name='add_absence'),
    path('attestation/', attestation_view, name='attestation'),
]