from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q
from .models import Edition
from .forms import EditionForm, AdminLoginForm


def is_admin(user):
    return user.is_staff or user.is_superuser


def home(request):
    editions = Edition.objects.filter(is_published=True)
    query = request.GET.get('q', '')
    if query:
        editions = editions.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    latest = editions.first()
    return render(request, 'newspaper/home.html', {
        'editions': editions,
        'latest': latest,
        'query': query,
    })


def edition_detail(request, pk):
    edition = get_object_or_404(Edition, pk=pk, is_published=True)
    return render(request, 'newspaper/edition_detail.html', {'edition': edition})


def admin_login(request):
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin_dashboard')
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user and is_admin(user):
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Invalid credentials or insufficient permissions.')
    else:
        form = AdminLoginForm()
    return render(request, 'newspaper/admin_login.html', {'form': form})


@login_required
@user_passes_test(is_admin, login_url='/admin-login/')
def admin_dashboard(request):
    editions = Edition.objects.all()
    return render(request, 'newspaper/admin_dashboard.html', {'editions': editions})


@login_required
@user_passes_test(is_admin, login_url='/admin-login/')
def edition_upload(request):
    if request.method == 'POST':
        form = EditionForm(request.POST, request.FILES)
        if form.is_valid():
            edition = form.save(commit=False)
            edition.uploaded_by = request.user
            edition.save()
            messages.success(request, f'Edition "{edition.title}" uploaded successfully!')
            return redirect('admin_dashboard')
    else:
        form = EditionForm()
    return render(request, 'newspaper/edition_form.html', {'form': form, 'action': 'Upload'})


@login_required
@user_passes_test(is_admin, login_url='/admin-login/')
def edition_edit(request, pk):
    edition = get_object_or_404(Edition, pk=pk)
    if request.method == 'POST':
        form = EditionForm(request.POST, request.FILES, instance=edition)
        if form.is_valid():
            form.save()
            messages.success(request, f'Edition "{edition.title}" updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = EditionForm(instance=edition)
    return render(request, 'newspaper/edition_form.html', {'form': form, 'action': 'Edit'})


@login_required
@user_passes_test(is_admin, login_url='/admin-login/')
def edition_delete(request, pk):
    edition = get_object_or_404(Edition, pk=pk)
    if request.method == 'POST':
        title = edition.title
        edition.delete()
        messages.success(request, f'Edition "{title}" deleted.')
        return redirect('admin_dashboard')
    return render(request, 'newspaper/edition_confirm_delete.html', {'edition': edition})


@login_required
@user_passes_test(is_admin, login_url='/admin-login/')
def admin_logout(request):
    logout(request)
    return redirect('home')
