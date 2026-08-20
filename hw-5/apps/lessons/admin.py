from django.contrib import admin
from apps.lessons.models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'view_count', 'created_at')
    list_display_links = ('id', 'title')
    search_fields = ('title',)
    readonly_fields = ('view_count', 'created_at')
