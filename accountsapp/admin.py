from django.contrib import admin
from .models import StudentCard

@admin.register(StudentCard)
class StudentCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'created_at')
    search_fields = ('user__username', 'phone')
    list_per_page = 30