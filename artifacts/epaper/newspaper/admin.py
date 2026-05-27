from django.contrib import admin
from .models import Edition


@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):
    list_display = ('title', 'edition_date', 'is_published', 'view_count', 'uploaded_by')
    list_filter = ('is_published', 'edition_date')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
