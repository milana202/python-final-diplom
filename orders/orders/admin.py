from django.contrib import admin
from .models import User


# указать, какие модели должны быть в админке
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['role', 'username', 'second_name', 'last_name', 'email', 'company', 'job_title']