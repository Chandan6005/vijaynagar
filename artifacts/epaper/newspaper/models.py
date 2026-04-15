from django.db import models
from django.contrib.auth.models import User


class Edition(models.Model):
    title = models.CharField(max_length=200)
    edition_date = models.DateField()
    pdf_file = models.FileField(upload_to='newspapers/')
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edition_date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.edition_date}"
