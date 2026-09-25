from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth import logout
from .models import SiteSetting

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setting, created = SiteSetting.objects.get_or_create(id=1)
        
        if setting.is_maintenance:
            path = request.path
            is_admin = request.user.is_authenticated and (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin')
            
            # المسارات اللي مسموح الدخول ليها وقت الصيانة
            is_allowed_path = (
                path.startswith('/login/') or 
                path.startswith('/admin/') or 
                path.startswith('/logout/') or 
                path.startswith('/static/')
            )
            
            if not is_admin and not is_allowed_path:
                # إيلا كان طالب مكونيكطي، كنخرجوه باش ما يطيحش فـ حلقة لا نهائية
                if request.user.is_authenticated:
                    logout(request)
                
                # كنخرجو ليه هاد الصفحة الزوينة ديريكت عوض ما نرجعوه لـ login
                html = """
                <!DOCTYPE html>
                <html lang="fr">
                <head>
                    <meta charset="UTF-8">
                    <title>Maintenance - ID Master</title>
                    <style>
                        body { background-color: #f8f9fc; color: #2d3748; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; text-align: center; }
                        .box { background: white; padding: 50px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 5px solid #e53e3e; }
                        a { display: inline-block; margin-top: 25px; background: #2d3748; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; }
                    </style>
                </head>
                <body>
                    <div class="box">
                        <div style="font-size: 60px; margin-bottom: 15px;">🛠️</div>
                        <h1 style="margin-top: 0;">Plateforme en Maintenance</h1>
                        <p>ID-Master est en cours de mise à jour par l'administration.</p>
                        <p style="color: #718096; font-size: 14px;">Revenez un peu plus tard.</p>
                        <a href="/login/">Accès Administrateur</a>
                    </div>
                </body>
                </html>
                """
                return HttpResponse(html, status=503)
                
        response = self.get_response(request)
        return response