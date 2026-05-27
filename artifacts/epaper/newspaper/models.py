from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Edition(models.Model):
    """Supabase Postgres-backed newspaper edition."""
    title = models.CharField(max_length=200)
    edition_date = models.DateField()
    pdf_file = models.URLField(max_length=1000)
    cover_image = models.URLField(max_length=1000, blank=True, null=True)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.edition_date}"

    def get_absolute_url(self):
        return reverse('edition_detail', args=[self.pk])

    class Meta:
        ordering = ['-edition_date', '-created_at']
        indexes = [
            models.Index(fields=['edition_date'], name='newspaper_e_edition_958ca5_idx'),
            models.Index(fields=['is_published'], name='newspaper_e_is_publ_0d10e4_idx'),
        ]
