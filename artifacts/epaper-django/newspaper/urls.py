from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('edition/<int:pk>/', views.edition_detail, name='edition_detail'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/upload/', views.edition_upload, name='edition_upload'),
    path('admin-dashboard/edit/<int:pk>/', views.edition_edit, name='edition_edit'),
    path('admin-dashboard/delete/<int:pk>/', views.edition_delete, name='edition_delete'),
]
