from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # زدنا is_active باش يبان ليك واش الكونط مقبول ولا لا
    list_display = ['username', 'email', 'role', 'is_active']
    # هادي غتخليك تبدل الدور وتقبل الكونط نيشان من الجدول
    list_editable = ['role', 'is_active'] 
    
    fieldsets = UserAdmin.fieldsets + (
        ('Rôle Utilisateur - OFPPT', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rôle Utilisateur - OFPPT', {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)