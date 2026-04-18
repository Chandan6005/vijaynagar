from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from datetime import datetime
import cloudinary.uploader
from mongoengine import Q as MongoQ
from .models import Edition
from .forms import EditionForm, AdminLoginForm, SignUpForm


def is_admin(user):
    return user.is_staff or user.is_superuser


def home(request):
    """List published editions with search and filter"""
    try:
        editions = Edition.objects(is_published=True)
    except Exception as e:
        messages.warning(request, 'Database connection issue. Showing cached data.')
        editions = []

    query = request.GET.get('q', '').strip()
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()
    sort = request.GET.get('sort', 'newest')

    # Apply search filter
    if query:
        editions = editions.filter(MongoQ(title__icontains=query) | MongoQ(description__icontains=query))

    # Apply date range filters
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            editions = editions.filter(edition_date__gte=from_date_obj)
        except:
            pass

    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            editions = editions.filter(edition_date__lte=to_date_obj)
        except:
            pass

    # Sort editions
    # if sort == 'oldest':
    #     editions = editions.order_by('edition_date', '-created_at')
    # else:
    #     editions = editions.order_by('-edition_date', '-created_at')

    # editions = list(editions)
    # latest = editions[0] if editions else None

    return render(request, 'newspaper/home.html', {
        'editions': editions,
        'latest': latest,
        'query': query,
        'from_date': from_date,
        'to_date': to_date,
        'sort': sort,
    })


def edition_detail(request, pk):
    """Display a single edition and increment view count"""
    try:
        edition = Edition.objects.get(id=pk, is_published=True)
        # Increment view count
        edition.view_count += 1
        edition.save()
    except Edition.DoesNotExist:
        return render(request, 'not-found.html', status=404)

    share_url = request.build_absolute_uri(edition.get_absolute_url())
    return render(request, 'newspaper/edition_detail.html', {
        'edition': edition,
        'share_url': share_url,
    })


@require_GET
def api_editions(request):
    """API endpoint for fetching published editions"""
    try:
        editions = Edition.objects(is_published=True).order_by('-edition_date', '-created_at')[:50]
    except Exception:
        editions = []

    query = request.GET.get('q', '').strip()
    if query:
        editions = Edition.objects(
            is_published=True,
            title__icontains=query
        ).order_by('-edition_date', '-created_at')[:50]

    data = [
        {
            'id': str(edition.id),
            'title': edition.title,
            'edition_date': edition.edition_date.isoformat(),
            'description': edition.description or '',
            'pdf_url': edition.pdf_file_url,
            'cover_image_url': edition.cover_image_url,
            'detail_url': edition.get_absolute_url(),
            'view_count': edition.view_count,
        }
        for edition in editions
    ]
    return JsonResponse({'count': len(data), 'editions': data})


@require_GET
def api_edition_detail(request, pk):
    """API endpoint for a single edition"""
    try:
        edition = Edition.objects.get(id=pk, is_published=True)
        return JsonResponse({
            'id': str(edition.id),
            'title': edition.title,
            'edition_date': edition.edition_date.isoformat(),
            'description': edition.description or '',
            'pdf_url': edition.pdf_file_url,
            'cover_image_url': edition.cover_image_url,
            'view_count': edition.view_count,
            'detail_url': edition.get_absolute_url(),
        })
    except Edition.DoesNotExist:
        return JsonResponse({'error': 'Edition not found'}, status=404)


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
    """Admin dashboard with stats"""
    try:
        editions = Edition.objects()
        published_count = Edition.objects(is_published=True).count()
        draft_count = Edition.objects(is_published=False).count()
        total_views = sum(e.view_count for e in editions)
    except Exception:
        editions = []
        published_count = 0
        draft_count = 0
        total_views = 0

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
    """Upload a new edition"""
    if request.method == 'POST':
        form = EditionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Upload PDF to Cloudinary
                pdf_file = request.FILES.get('pdf_file')
                pdf_response = cloudinary.uploader.upload(
                    pdf_file,
                    resource_type='raw',
                    folder='epaper/pdfs',
                    public_id=f"{form.cleaned_data['title'].replace(' ', '_')}"
                )
                pdf_url = pdf_response['secure_url']

                # Upload cover image if provided
                cover_url = None
                if 'cover_image' in request.FILES:
                    cover_file = request.FILES.get('cover_image')
                    cover_response = cloudinary.uploader.upload(
                        cover_file,
                        folder='epaper/covers'
                    )
                    cover_url = cover_response['secure_url']

                # Create Edition in MongoDB
                edition = Edition(
                    title=form.cleaned_data['title'],
                    edition_date=form.cleaned_data['edition_date'],
                    pdf_file_url=pdf_url,
                    cover_image_url=cover_url,
                    description=form.cleaned_data['description'],
                    is_published=form.cleaned_data['is_published'],
                    uploaded_by_id=request.user.id,
                )
                edition.save()
                messages.success(request, f'Edition "{edition.title}" uploaded successfully!')
                return redirect('admin_dashboard')
            except Exception as e:
                messages.error(request, f'Upload failed: {str(e)}')
    else:
        form = EditionForm()

    return render(request, 'newspaper/edition_form.html', {'form': form, 'action': 'Upload'})


@login_required
@user_passes_test(is_admin, login_url='/admin-login/')
def edition_edit(request, pk):
    """Edit an existing edition"""
    try:
        edition = Edition.objects.get(id=pk)
    except Edition.DoesNotExist:
        messages.error(request, 'Edition not found.')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = EditionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                edition.title = form.cleaned_data['title']
                edition.edition_date = form.cleaned_data['edition_date']
                edition.description = form.cleaned_data['description']
                edition.is_published = form.cleaned_data['is_published']

                # Update PDF if new file uploaded
                if 'pdf_file' in request.FILES:
                    pdf_file = request.FILES.get('pdf_file')
                    pdf_response = cloudinary.uploader.upload(
                        pdf_file,
                        resource_type='raw',
                        folder='epaper/pdfs',
                        public_id=f"{form.cleaned_data['title'].replace(' ', '_')}_v{int(datetime.now().timestamp())}"
                    )
                    edition.pdf_file_url = pdf_response['secure_url']

                # Update cover image if new file uploaded
                if 'cover_image' in request.FILES:
                    cover_file = request.FILES.get('cover_image')
                    cover_response = cloudinary.uploader.upload(
                        cover_file,
                        folder='epaper/covers'
                    )
                    edition.cover_image_url = cover_response['secure_url']

                edition.updated_at = datetime.utcnow()
                edition.save()
                messages.success(request, f'Edition "{edition.title}" updated successfully!')
                return redirect('admin_dashboard')
            except Exception as e:
                messages.error(request, f'Update failed: {str(e)}')
    else:
        form = EditionForm(initial={
            'title': edition.title,
            'edition_date': edition.edition_date,
            'description': edition.description,
            'is_published': edition.is_published,
        })

    return render(request, 'newspaper/edition_form.html', {'form': form, 'action': 'Edit'})


@login_required
@user_passes_test(is_admin, login_url='/admin-login/')
def edition_delete(request, pk):
    """Delete an edition"""
    try:
        edition = Edition.objects.get(id=pk)
    except Edition.DoesNotExist:
        messages.error(request, 'Edition not found.')
        return redirect('admin_dashboard')

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


@login_required
def site_logout(request):
    logout(request)
    return redirect('home')
