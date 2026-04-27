from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

# Позволяет редактировать профиль прямо на странице пользователя
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fk_name = 'user'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Добавляем профиль в форму редактирования пользователя
    inlines = (ProfileInline, )
    
    # Колонки, которые будут видны в списке пользователей
    list_display = ('email', 'username', 'role', 'is_staff', 'is_admin')
    # Фильтры справа
    list_filter = ('role', 'is_staff', 'is_superuser')
    
    # Группировка полей в форме редактирования
    fieldsets = UserAdmin.fieldsets + (
        ('Роль и статус', {'fields': ('role',)}),
    )
    
    # Поля при создании пользователя (через админку)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Роль', {'fields': ('role',)}),
    )

    ordering = ('email',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'gender', 'birth_date')
    search_fields = ('user__email', 'phone')
