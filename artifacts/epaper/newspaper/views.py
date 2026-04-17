from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q, F, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Edition
from .forms import EditionForm, AdminLoginForm, SignUpForm


def is_admin(user):
    return user.is_staff or user.is_superuser


def home(request):
    editions = Edition.objects.filter(is_published=True)
    query = request.GET.get('q', '').strip()
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()
    sort = request.GET.get('sort', 'newest')

    if query:
        editions = editions.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if from_date:
        editions = editions.filter(edition_date__gte=from_date)

    if to_date:
        editions = editions.filter(edition_date__lte=to_date)

    if sort == 'oldest':
        editions = editions.order_by('edition_date', '-created_at')
    else:
        editions = editions.order_by('-edition_date', '-created_at')

    latest = editions.first()
    return render(request, 'newspaper/home.html', {
        'editions': editions,
        'latest': latest,
        'query': query,
        'from_date': from_date,
        'to_date': to_date,
        'sort': sort,
    })


def edition_detail(request, pk):
    edition = get_object_or_404(Edition, pk=pk, is_published=True)
    Edition.objects.filter(pk=edition.pk).update(view_count=F('view_count') + 1)
    edition.refresh_from_db(fields=['view_count'])
    share_url = request.build_absolute_uri(edition.get_absolute_url())
    return render(request, 'newspaper/edition_detail.html', {
        'edition': edition,
        'share_url': share_url,
    })


@require_GET
def api_editions(request):
    editions = Edition.objects.filter(is_published=True)
    query = request.GET.get('q', '').strip()
    if query:
        editions = editions.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    editions = editions.order_by('-edition_date', '-created_at')[:50]
    data = [
        {
            'id': edition.pk,
            'title': edition.title,
            'edition_date': edition.edition_date.isoformat(),
            'description': edition.description,
            'pdf_url': request.build_absolute_uri(edition.pdf_file.url),
            'cover_image_url': request.build_absolute_uri(edition.cover_image.url) if edition.cover_image else None,
            'detail_url': request.build_absolute_uri(edition.get_absolute_url()),
            'view_count': edition.view_count,
        }
        for edition in editions
    ]
    return JsonResponse({'count': len(data), 'editions': data})


@require_GET
def api_edition_detail(request, pk):
    edition = get_object_or_404(Edition, pk=pk, is_published=True)
    return JsonResponse({
        'id': edition.pk,
        'title': edition.title,
        'edition_date': edition.edition_date.isoformat(),
        'description': edition.description,
        'pdf_url': request.build_absolute_uri(edition.pdf_file.url),
        'cover_image_url': request.build_absolute_uri(edition.cover_image.url) if edition.cover_image else None,
        'view_count': edition.view_count,
        'detail_url': request.build_absolute_uri(edition.get_absolute_url()),
    })


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
    published_count = editions.filter(is_published=True).count()
    total_views = editions.aggregate(total=Sum('view_count'))['total'] or 0
    draft_count = editions.filter(is_published=False).count()
    return render(request, 'newspaper/admin_dashboard.html', {
        'editions': editions,
        'published_count': published_count,
        'draft_count': draft_count,
        'total_views': total_views,
    })


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'newspaper/profile.html', {'user': request.user})


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
