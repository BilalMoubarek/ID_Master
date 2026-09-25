from django.urls import path
from .views import (
    login_view, logout_view, dashboard_view, student_dashboard_view, 
    register_view, stagiaires_list, formateurs_list, settings_view, 
    messages_view, toggle_maintenance, save_grades, export_stagiaires_csv
)

urlpatterns = [
    path('', login_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    path('dashboard/', dashboard_view, name='dashboard'), 
    path('mon-espace/', student_dashboard_view, name='student_dashboard'), 
    path('save-grades/', save_grades, name='save_grades'),
    path('toggle-maintenance/', toggle_maintenance, name='toggle_maintenance'),
    
    path('stagiaires/', stagiaires_list, name='stagiaires'),
    path('formateurs/', formateurs_list, name='formateurs'),
    path('settings/', settings_view, name='settings'),

    path('toggle-maintenance/', toggle_maintenance, name='toggle_maintenance'),
    
    path('messages/', messages_view, name='messages'),
    path('messages/<int:user_id>/', messages_view, name='chat'),
    
    path('export/stagiaires/', export_stagiaires_csv, name='export_stagiaires'),
]