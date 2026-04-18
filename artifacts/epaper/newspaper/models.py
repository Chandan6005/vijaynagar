from mongoengine import Document, StringField, DateField, URLField, IntField, BooleanField, DateTimeField
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime


class Edition(Document):
    """MongoDB-backed Edition model"""
    title = StringField(required=True, max_length=200)
    edition_date = DateField(required=True)
    pdf_file_url = URLField(required=True)  # Cloudinary URL
    cover_image_url = URLField()  # Cloudinary URL (optional)
    description = StringField()
    is_published = BooleanField(default=True)
    view_count = IntField(default=0)
    uploaded_by_id = IntField()  # Django User ID
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'editions',
        'ordering': ['-edition_date', '-created_at'],
        'indexes': ['edition_date', 'is_published']
    }

    def __str__(self):
        return f"{self.title} - {self.edition_date}"

    def get_absolute_url(self):
        return reverse('edition_detail', args=[str(self.id)])

    @property
    def uploaded_by(self):
        """Get Django User object for this upload"""
        try:
            return User.objects.get(id=self.uploaded_by_id)
        except User.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
