from django.contrib import admin
from .models import Edition


@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):
    list_display = ['title', 'edition_date', 'is_published', 'uploaded_by', 'created_at']
    list_filter = ['is_published', 'edition_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'edition_date'
