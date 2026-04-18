from django.contrib import admin

# MongoEngine models cannot be registered with Django admin
# Edition is now a MongoEngine Document and is managed through custom views
# See newspaper/views.py for admin_dashboard() and edition_upload/edit/delete views
