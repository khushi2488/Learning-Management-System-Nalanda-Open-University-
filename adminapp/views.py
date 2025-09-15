from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import User
from django.contrib import messages
from nouapp.models import Student, Enquiry, Login
from studentapp.models import StuResponse
from .models import Program, Branch, Year, Material, News, Course, MaterialCategory,NewsAnnouncement, NewsCategory
from datetime import date
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime


# Create your views here.
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def adminhome(request):
    try:
        if request.session['adminid']!=None:
            adminid=request.session['adminid']
            return render(request,"adminhome.html",{'adminid':adminid})
    except KeyError:
        return redirect('nouapp:login')

def adminlogout(request):
    try:
        del request.session['adminid']
        return redirect('nouapp:login')
    except KeyError:
        return redirect('nouapp:login')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def viewstudent(request):
    try:
        if request.session['adminid']!=None:
            adminid=request.session['adminid']
            student=Student.objects.all()
            return render(request,"viewstudent.html",locals())
    except KeyError:
        return redirect('nouapp:login')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def viewenquiry(request):
    try:
        if request.session['adminid']!=None:
            adminid=request.session['adminid']
            enq=Enquiry.objects.all()
            return render(request,"viewenquiry.html",locals())
    except KeyError:
        return redirect('nouapp:login')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def viewfeedback(request):
    try:
        if request.session['adminid']!=None:
            adminid=request.session['adminid']
            feed=StuResponse.objects.filter(responsetype='feedback')
            return render(request,"viewfeedback.html",locals())
    except KeyError:
        return redirect('nouapp:login')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def viewcomplain(request):
    try:
        if request.session['adminid']!=None:
            adminid=request.session['adminid']
            comp=StuResponse.objects.filter(responsetype='complain')
            return render(request,"viewcomplain.html",locals())
    except KeyError:
        return redirect('nouapp:login')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def studymaterial(request):
    try:
        if request.session['adminid']!=None:
            adminid=request.session['adminid']
            courses = Course.objects.all()
            categories = MaterialCategory.objects.all()
            return render(request, "studymaterial.html", {'adminid': adminid, 'courses': courses, 'categories': categories})
    except KeyError:
        return redirect('nouapp:login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def move(request):
    try:
        if request.session['adminid'] is not None:
            adminid = request.session['adminid']

            if request.method == 'POST':
                # Get POST data
                course_id = request.POST.get('course')
                title = request.POST.get('title')
                description = request.POST.get('description', '')
                category_id = request.POST.get('category')
                my_file = request.FILES.get('my_file')

                # Validation
                if not course_id or not title or not my_file:
                    messages.error(request, "Course, title, and file are required!")
                    courses = Course.objects.all()
                    categories = MaterialCategory.objects.all()
                    return render(request, "studymaterial.html", {
                        'adminid': adminid, 
                        'courses': courses, 
                        'categories': categories
                    })

                # Get related objects
                course = get_object_or_404(Course, id=course_id)
                category = MaterialCategory.objects.filter(id=category_id).first() if category_id else None
                
                # Get admin user - you'll need to adjust this based on how you store admin info
                try:
                    # Option 1: If adminid is the user ID
                    user = User.objects.get(id=adminid)
                except (User.DoesNotExist, ValueError):
                    # Option 2: If adminid is username or you need to create a default admin user
                    user, created = User.objects.get_or_create(
                        username='admin',
                        defaults={
                            'is_staff': True,
                            'is_superuser': True
                        }
                    )

                # Create Material object
                material = Material.objects.create(
                    title=title,
                    description=description,
                    course=course,
                    category=category,
                    file=my_file,
                    created_by=user,
                    is_public=True  # You can adjust this based on your needs
                )

                messages.success(request, "Material uploaded successfully!")
                return redirect('adminapp:viewmaterial')  # Redirect to view materials
                
            # If GET request, show the form
            courses = Course.objects.all()
            categories = MaterialCategory.objects.all()
            return render(request, "studymaterial.html", {
                'adminid': adminid, 
                'courses': courses, 
                'categories': categories
            })

    except KeyError:
        return redirect('nouapp:login')

    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def viewmaterial(request):
    try:
        if request.session['adminid']!=None:
            adminid=request.session['adminid']
            # Use select_related to avoid N+1 queries
            mat = Material.objects.select_related('course', 'course__program', 'course__branch', 'course__year', 'category', 'created_by').all()
            print(f"Found {len(mat)} materials")  # Debug print
            for m in mat:
                print(f"Material: {m.title}, Course: {m.course}, File: {m.file}")  # Debug print
            return render(request,"viewmaterial.html", {'mat': mat, 'adminid': adminid})
    except KeyError:
        return redirect('nouapp:login')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def news(request):
    try:
        if request.session['adminid']!=None:
            adminid=request.session['adminid']
            if request.method=="POST":
                newstext=request.POST['newstext']
                newsdate=date.today()
                News(newstext=newstext,newsdate=newsdate).save()
            ns=News.objects.all()
            return render(request,"news.html",locals())
    except KeyError:
        return redirect('nouapp:login')
    
#____________For file management system______________________

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404, FileResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import ListView
import os
import mimetypes
from PIL import Image
import pdf2image
from .models import Material, MaterialCategory, MaterialAccess, Course
from .forms import MaterialForm, MaterialCategoryForm
from datetime import datetime, timedelta

from django.db.models import F


@login_required
def material_list(request, course_id=None):
    """List materials with filtering and search"""
    materials = Material.objects.select_related('category', 'course', 'created_by')
    
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        materials = materials.filter(course=course)
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        materials = materials.filter(category_id=category_id)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        materials = materials.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by file type
    file_type = request.GET.get('file_type')
    if file_type:
        materials = materials.filter(file_type=file_type)
    
    # Only show latest versions by default
    show_all_versions = request.GET.get('show_all_versions', False)
    if not show_all_versions:
        materials = materials.filter(is_latest_version=True)
    
    # Pagination
    paginator = Paginator(materials, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter dropdown
    categories = MaterialCategory.objects.all()
    
    # Get available file types for filter
    file_types = materials.values_list('file_type', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'file_types': file_types,
        'current_category': category_id,
        'current_file_type': file_type,
        'search_query': search_query,
        'show_all_versions': show_all_versions,
    }
    
    if course_id:
        context['course'] = course
    
    return render(request, 'adminapp/material_list.html', context)

@login_required
def material_detail(request, material_id):
    """Detailed view of a material with version history"""
    material = get_object_or_404(Material, id=material_id)
    
    # Check if user has access to this material
    if material.requires_enrollment:
        # Add enrollment check logic here
        pass
    
    # Get all versions of this material
    all_versions = material.get_all_versions()
    
    # Log the view
    MaterialAccess.objects.create(
        material=material,
        user=request.user,
        access_type='view',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Increment view count
    Material.objects.filter(id=material_id).update(view_count=F('view_count') + 1)
    
    context = {
        'material': material,
        'all_versions': all_versions,
        'can_edit': request.user == material.created_by or request.user.is_staff,
    }
    
    return render(request, 'adminapp/material_detail.html', context)

@login_required
def material_preview(request, material_id):
    """Generate and serve material preview"""
    material = get_object_or_404(Material, id=material_id)
    
    if not material.is_previewable:
        return JsonResponse({'error': 'Preview not available for this file type'}, status=400)
    
    # Log the preview access
    MaterialAccess.objects.create(
        material=material,
        user=request.user,
        access_type='preview',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    try:
        if material.file_type in ['jpg', 'jpeg', 'png', 'gif']:
            # Image preview - return the image directly
            return FileResponse(material.file.open(), content_type=f'image/{material.file_type}')
        
        elif material.file_type == 'pdf':
            # PDF preview - return first page as image if preview_image exists
            if material.preview_image:
                return FileResponse(material.preview_image.open(), content_type='image/png')
            else:
                # Generate preview image for PDF
                preview_path = generate_pdf_preview(material)
                if preview_path:
                    return FileResponse(open(preview_path, 'rb'), content_type='image/png')
        
        elif material.file_type == 'txt':
            # Text preview - return first 500 characters
            with material.file.open('r') as f:
                content = f.read(500)
                return JsonResponse({'preview_text': content, 'type': 'text'})
        
        elif material.file_type == 'mp4':
            # Video preview - return video with controls
            return JsonResponse({
                'video_url': material.file.url,
                'type': 'video'
            })
    
    except Exception as e:
        return JsonResponse({'error': f'Error generating preview: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Preview generation failed'}, status=500)

def generate_pdf_preview(material):
    """Generate preview image for PDF files"""
    try:
        # Convert first page of PDF to image
        images = pdf2image.convert_from_path(material.file.path, first_page=1, last_page=1)
        if images:
            preview_path = f"media/previews/{material.id}_preview.png"
            os.makedirs(os.path.dirname(preview_path), exist_ok=True)
            images[0].save(preview_path, 'PNG')
            
            # Update material with preview image
            material.preview_image = preview_path
            material.save()
            
            return preview_path
    except Exception as e:
        print(f"Error generating PDF preview: {e}")
    return None

@login_required
def material_download(request, material_id):
    """Handle material download with access logging"""
    material = get_object_or_404(Material, id=material_id)
    
    # Check permissions
    if material.requires_enrollment:
        # Add enrollment check logic here
        pass
    
    # Log the download
    MaterialAccess.objects.create(
        material=material,
        user=request.user,
        access_type='download',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Increment download count
    Material.objects.filter(id=material_id).update(download_count=F('download_count') + 1)
    
    # Serve the file
    response = FileResponse(
        material.file.open(),
        content_type=mimetypes.guess_type(material.file.path)[0],
        as_attachment=True,
        filename=material.file.name.split('/')[-1]
    )
    
    return response

@login_required
def create_material(request, course_id):
    """Create new material"""
    course = get_object_or_404(Course, id=course_id)
    
    # Check permissions
    if not (request.user.is_staff or course.instructor == request.user):
        messages.error(request, "You don't have permission to add materials to this course.")
        return redirect('course_detail', course_id=course_id)
    
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.created_by = request.user
            material.save()
            
            messages.success(request, 'Material uploaded successfully!')
            return redirect('material_detail', material_id=material.id)
    else:
        form = MaterialForm()
    
    return render(request, 'adminapp/create_material.html', {
        'form': form,
        'course': course
    })

@login_required
def create_material_version(request, material_id):
    """Create new version of existing material"""
    original_material = get_object_or_404(Material, id=material_id)
    
    # Check permissions
    if not (request.user.is_staff or original_material.created_by == request.user):
        messages.error(request, "You don't have permission to create versions of this material.")
        return redirect('material_detail', material_id=material_id)
    
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            new_version = form.save(commit=False)
            new_version.course = original_material.course
            new_version.created_by = request.user
            new_version.parent_material = original_material if not original_material.parent_material else original_material.parent_material
            new_version.save()
            
            messages.success(request, f'New version ({new_version.version}) created successfully!')
            return redirect('material_detail', material_id=new_version.id)
    else:
        # Pre-populate form with original material data
        form = MaterialForm(initial={
            'title': original_material.title,
            'description': original_material.description,
            'category': original_material.category,
            'is_public': original_material.is_public,
            'requires_enrollment': original_material.requires_enrollment,
        })
    
    return render(request, 'adminapp/create_material_version.html', {
        'form': form,
        'original_material': original_material
    })

@login_required
def material_categories(request):
    """Manage material categories"""
    categories = MaterialCategory.objects.all()
    
    if request.method == 'POST':
        form = MaterialCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('material_categories')
    else:
        form = MaterialCategoryForm()
    
    return render(request, 'adminapp/material_categories.html', {
        'categories': categories,
        'form': form
    })

@require_http_methods(["POST"])
@login_required
def delete_material(request, material_id):
    """Delete a material (soft delete - mark as inactive)"""
    material = get_object_or_404(Material, id=material_id)
    
    # Check permissions
    if not (request.user.is_staff or material.created_by == request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Instead of actual deletion, mark as inactive or move to trash
    # material.is_active = False
    # material.save()
    
    # For now, we'll do actual deletion
    course_id = material.course.id
    material.delete()
    
    messages.success(request, 'Material deleted successfully!')
    return redirect('material_list', course_id=course_id)

#for news extend
# Enhanced news management view
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_news(request):
    """Enhanced news management with categories and filtering"""
    try:
        if request.session['adminid'] is not None:
            adminid = request.session['adminid']
            
            # Get filter parameters
            category_filter = request.GET.get('category', '')
            status_filter = request.GET.get('status', 'all')  # all, active, expired
            
            # Base queryset
            news_list = NewsAnnouncement.objects.all().select_related('category')
            
            # Apply filters
            if category_filter:
                news_list = news_list.filter(category_id=category_filter)
                
            if status_filter == 'active':
                now = timezone.now()
                news_list = news_list.filter(
                    is_active=True,
                    publish_date__lte=now
                ).exclude(
                    expiry_date__lt=now
                )
            elif status_filter == 'expired':
                news_list = news_list.filter(
                    expiry_date__lt=timezone.now()
                )
            
            # Get categories for filter dropdown
            categories = NewsCategory.objects.filter(is_active=True)
            
            return render(request, "manage_news.html", {
                'adminid': adminid,
                'news_list': news_list,
                'categories': categories,
                'current_category': category_filter,
                'current_status': status_filter
            })
    except KeyError:
        return redirect('nouapp:login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_news(request):
    """Create new news/announcement with proper date handling"""
    try:
        if request.session['adminid'] is not None:
            adminid = request.session['adminid']
            
            if request.method == 'POST':
                # Get form data
                title = request.POST.get('title')
                newstext = request.POST.get('newstext')
                category_id = request.POST.get('category')
                priority = request.POST.get('priority', 'normal')
                target_audience = request.POST.get('target_audience', 'all')
                
                # Date fields - FIXED: Handle timezone-aware datetime
                publish_date_str = request.POST.get('publish_date')
                expiry_date_str = request.POST.get('expiry_date')
                
                # Target specific groups
                target_programs = request.POST.get('target_programs', '')
                target_branches = request.POST.get('target_branches', '')
                target_years = request.POST.get('target_years', '')
                
                # Validation
                if not title or not newstext:
                    messages.error(request, "Title and content are required!")
                    return render(request, "create_news.html", {
                        'adminid': adminid,
                        'categories': NewsCategory.objects.filter(is_active=True)
                    })
                
                # Parse dates properly with timezone
                publish_date = timezone.now()  # Default to now
                if publish_date_str:
                    try:
                        # Parse the datetime string and make it timezone aware
                        naive_dt = datetime.strptime(publish_date_str, '%Y-%m-%dT%H:%M')
                        publish_date = timezone.make_aware(naive_dt)
                    except ValueError:
                        messages.error(request, "Invalid publish date format!")
                        return render(request, "create_news.html", {
                            'adminid': adminid,
                            'categories': NewsCategory.objects.filter(is_active=True)
                        })
                
                expiry_date = None
                if expiry_date_str:
                    try:
                        naive_dt = datetime.strptime(expiry_date_str, '%Y-%m-%dT%H:%M')
                        expiry_date = timezone.make_aware(naive_dt)
                    except ValueError:
                        messages.error(request, "Invalid expiry date format!")
                        return render(request, "create_news.html", {
                            'adminid': adminid,
                            'categories': NewsCategory.objects.filter(is_active=True)
                        })
                
                # Create news item
                news = NewsAnnouncement.objects.create(
                    title=title,
                    newstext=newstext,
                    category_id=category_id if category_id else None,
                    priority=priority,
                    target_audience=target_audience,
                    target_programs=target_programs,
                    target_branches=target_branches, 
                    target_years=target_years,
                    publish_date=publish_date,
                    expiry_date=expiry_date,
                    created_by=f"Admin_{adminid}",
                    is_pinned=bool(request.POST.get('is_pinned')),
                    attachment=request.FILES.get('attachment'),
                    is_active=True  # Make sure it's active by default
                )
                
                messages.success(request, "News/Announcement created successfully!")
                return redirect('adminapp:manage_news')
            
            # GET request - show form
            categories = NewsCategory.objects.filter(is_active=True)
            programs = Program.objects.all()  # Add programs for dropdown
            branches = Branch.objects.all()   # Add branches for dropdown
            years = Year.objects.all()        # Add years for dropdown
            
            return render(request, "create_news.html", {
                'adminid': adminid,
                'categories': categories,
                'programs': programs,
                'branches': branches,
                'years': years
            })
    except KeyError:
        return redirect('nouapp:login')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_news(request, news_id):
    """Edit existing news/announcement"""
    try:
        if request.session['adminid'] is not None:
            adminid = request.session['adminid']
            news = get_object_or_404(NewsAnnouncement, nid=news_id)
            
            if request.method == 'POST':
                # Update news item
                news.title = request.POST.get('title')
                news.newstext = request.POST.get('newstext')
                news.category_id = request.POST.get('category') or None
                news.priority = request.POST.get('priority', 'normal')
                news.target_audience = request.POST.get('target_audience', 'all')
                news.target_programs = request.POST.get('target_programs', '')
                news.target_branches = request.POST.get('target_branches', '')
                news.target_years = request.POST.get('target_years', '')
                news.is_pinned = bool(request.POST.get('is_pinned'))
                
                # Handle dates
                publish_date = request.POST.get('publish_date')
                if publish_date:
                    news.publish_date = datetime.strptime(publish_date, '%Y-%m-%dT%H:%M')
                
                expiry_date = request.POST.get('expiry_date')
                news.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%dT%H:%M') if expiry_date else None
                
                # Handle file upload
                if request.FILES.get('attachment'):
                    news.attachment = request.FILES.get('attachment')
                
                news.save()
                messages.success(request, "News/Announcement updated successfully!")
                return redirect('adminapp:manage_news')
            
            # GET request - show edit form
            categories = NewsCategory.objects.filter(is_active=True)
            return render(request, "edit_news.html", {
                'adminid': adminid,
                'news': news,
                'categories': categories
            })
    except KeyError:
        return redirect('nouapp:login')

# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_categories(request):
    """Manage news categories"""
    try:
        if request.session['adminid'] is not None:
            adminid = request.session['adminid']
            
            if request.method == 'POST':
                # Check if it's editing an existing category
                if 'edit_category' in request.POST:
                    category_id = request.POST.get('edit_category')
                    category = get_object_or_404(NewsCategory, id=category_id)
                    
                    category.name = request.POST.get('edit_name')
                    category.description = request.POST.get('edit_description', '')
                    category.icon = request.POST.get('edit_icon', '')
                    category.color_code = request.POST.get('edit_color_code', '#007bff')
                    category.is_active = bool(request.POST.get('edit_is_active'))
                    category.save()
                    
                    messages.success(request, "Category updated successfully!")
                else:
                    # Create new category
                    name = request.POST.get('name')
                    description = request.POST.get('description', '')
                    icon = request.POST.get('icon', '')
                    color_code = request.POST.get('color_code', '#007bff')
                    
                    if name:
                        NewsCategory.objects.create(
                            name=name,
                            description=description,
                            icon=icon,
                            color_code=color_code
                        )
                        messages.success(request, "Category created successfully!")
                    else:
                        messages.error(request, "Category name is required!")
                
            categories = NewsCategory.objects.all().order_by('name')
            return render(request, "manage_categories.html", {
                'adminid': adminid,
                'categories': categories
            })
    except KeyError:
        return redirect('nouapp:login')


# Utility views
def toggle_news_status(request, news_id):
    """Toggle active/inactive status of news"""
    try:
        if request.session['adminid'] is not None:
            news = get_object_or_404(NewsAnnouncement, nid=news_id)
            news.is_active = not news.is_active
            news.save()
            
            status = "activated" if news.is_active else "deactivated"
            messages.success(request, f"News {status} successfully!")
    except KeyError:
        pass
    
    return redirect('adminapp:manage_news')

def delete_news(request, news_id):
    """Delete news item"""
    try:
        if request.session['adminid'] is not None:
            news = get_object_or_404(NewsAnnouncement, nid=news_id)
            news.delete()
            messages.success(request, "News deleted successfully!")
    except KeyError:
        pass
    
    return redirect('adminapp:manage_news')

def pin_news(request, news_id):
    """Toggle pin status of news"""
    try:
        if request.session['adminid'] is not None:
            news = get_object_or_404(NewsAnnouncement, nid=news_id)
            news.is_pinned = not news.is_pinned
            news.save()
            
            status = "pinned" if news.is_pinned else "unpinned"
            messages.success(request, f"News {status} successfully!")
    except KeyError:
        pass
    
    return redirect('adminapp:manage_news')

def get_news_stats():
    """Get news statistics for dashboard"""
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    total_news = NewsAnnouncement.objects.count()
    active_news = NewsAnnouncement.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now()
    ).exclude(expiry_date__lt=timezone.now()).count()
    
    news_this_week = NewsAnnouncement.objects.filter(
        newsdate__date__gte=week_ago
    ).count()
    
    expired_news = NewsAnnouncement.objects.filter(
        expiry_date__lt=timezone.now()
    ).count()
    
    return {
        'total_news': total_news,
        'active_news': active_news,
        'news_this_week': news_this_week,
        'expired_news': expired_news
    }

def cleanup_expired_news():
    """Cleanup function to handle expired news"""
    from django.utils import timezone
    
    # Option 1: Mark as inactive
    expired_count = NewsAnnouncement.objects.filter(
        expiry_date__lt=timezone.now(),
        is_active=True
    ).update(is_active=False)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def enhanced_admin_dashboard(request):
    """Enhanced admin dashboard with news stats"""
    try:
        if request.session['adminid'] is not None:
            adminid = request.session['adminid']
            
            # Get news statistics
            news_stats = get_news_stats()
            
            # Get recent news
            recent_news = NewsAnnouncement.objects.filter(
                is_active=True
            ).order_by('-newsdate')[:5]
            
            
            
            # Get urgent announcements
            urgent_news = NewsAnnouncement.objects.filter(
                is_active=True,
                priority='urgent',
                publish_date__lte=timezone.now()
            ).exclude(expiry_date__lt=timezone.now())
            
            return render(request, "enhanced_admin_dashboard.html", {
                'adminid': adminid,
                'news_stats': news_stats,
                'recent_news': recent_news,
                'urgent_news': urgent_news
            })
    except KeyError:
        return redirect('nouapp:login')


#new 
# Add these views to your adminapp/views.py

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def bulk_news_action(request):
    """Handle bulk actions on multiple news items"""
    try:
        if request.session['adminid'] is not None:
            if request.method == 'POST':
                action = request.POST.get('bulk_action')
                selected_news = request.POST.getlist('selected_news')
                
                if not selected_news:
                    messages.error(request, "No news items selected!")
                    return redirect('adminapp:manage_news')
                
                if not action:
                    messages.error(request, "No action selected!")
                    return redirect('adminapp:manage_news')
                
                # Get selected news items
                news_items = NewsAnnouncement.objects.filter(nid__in=selected_news)
                count = news_items.count()
                
                if action == 'activate':
                    news_items.update(is_active=True)
                    messages.success(request, f"Activated {count} news items successfully!")
                    
                elif action == 'deactivate':
                    news_items.update(is_active=False)
                    messages.success(request, f"Deactivated {count} news items successfully!")
                    
                elif action == 'delete':
                    news_items.delete()
                    messages.success(request, f"Deleted {count} news items successfully!")
                    
                elif action == 'pin':
                    news_items.update(is_pinned=True)
                    messages.success(request, f"Pinned {count} news items successfully!")
                    
                elif action == 'unpin':
                    news_items.update(is_pinned=False)
                    messages.success(request, f"Unpinned {count} news items successfully!")
                    
                else:
                    messages.error(request, "Invalid action selected!")
                    
            return redirect('adminapp:manage_news')
    except KeyError:
        return redirect('nouapp:login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def duplicate_news(request, news_id):
    """Duplicate a news item"""
    try:
        if request.session['adminid'] is not None:
            adminid = request.session['adminid']
            original_news = get_object_or_404(NewsAnnouncement, nid=news_id)
            
            # Create a duplicate
            duplicate = NewsAnnouncement.objects.create(
                title=f"Copy of {original_news.title}",
                newstext=original_news.newstext,
                category=original_news.category,
                priority=original_news.priority,
                target_audience=original_news.target_audience,
                target_programs=original_news.target_programs,
                target_branches=original_news.target_branches,
                target_years=original_news.target_years,
                publish_date=timezone.now(),  # Set to current time
                expiry_date=original_news.expiry_date,
                created_by=f"Admin_{adminid}",
                is_active=False,  # Start as inactive for review
                is_pinned=False,  # Don't duplicate pinned status
                # Note: attachment is not duplicated for security reasons
            )
            
            messages.success(request, f"News item duplicated successfully! Please review and activate.")
            return redirect('adminapp:edit_news', news_id=duplicate.nid)
            
    except KeyError:
        return redirect('nouapp:login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def preview_news(request, news_id):
    """Preview news item (AJAX endpoint)"""
    try:
        if request.session['adminid'] is not None:
            news = get_object_or_404(NewsAnnouncement, nid=news_id)
            
            # Return HTML preview
            preview_html = f"""
            <div class="news-preview">
                <div class="mb-3">
                    <h4>{news.title}</h4>
                    <div class="mb-2">
                        <span class="badge badge-{news.get_priority_class().replace('alert-', '')}">{news.get_priority_display()}</span>
                        {f'<span class="badge ml-1" style="background-color: {news.category.color_code};">{news.category.name}</span>' if news.category else ''}
                        {'<span class="badge badge-warning ml-1">Pinned</span>' if news.is_pinned else ''}
                    </div>
                </div>
                
                <div class="mb-3">
                    <strong>Target Audience:</strong> {news.get_target_audience_display()}
                    {f'<br><strong>Programs:</strong> {news.target_programs}' if news.target_programs else ''}
                    {f'<br><strong>Branches:</strong> {news.target_branches}' if news.target_branches else ''}
                    {f'<br><strong>Years:</strong> {news.target_years}' if news.target_years else ''}
                </div>
                
                <div class="mb-3">
                    <strong>Content:</strong>
                    <div class="mt-2 p-3 bg-light border-left border-primary">
                        {news.newstext.replace(chr(10), '<br>')}
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <strong>Publish Date:</strong><br>
                        {news.publish_date.strftime('%B %d, %Y at %I:%M %p')}
                    </div>
                    <div class="col-md-6">
                        <strong>Expiry Date:</strong><br>
                        {news.expiry_date.strftime('%B %d, %Y at %I:%M %p') if news.expiry_date else 'Never expires'}
                    </div>
                </div>
                
                {f'<div class="mt-3"><strong>Attachment:</strong> <a href="{news.attachment.url}" target="_blank">{news.attachment.name}</a></div>' if news.attachment else ''}
                
                <div class="mt-3 text-muted">
                    <small>Created by: {news.created_by} | Views: {news.view_count}</small>
                </div>
            </div>
            """
            
            from django.http import HttpResponse
            return HttpResponse(preview_html)
            
    except KeyError:
        return redirect('nouapp:login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def news_analytics(request):
    """News analytics dashboard"""
    try:
        if request.session['adminid'] is not None:
            adminid = request.session['adminid']
            
            from django.db.models import Count, Q, Sum
            from datetime import timedelta
            
            # Analytics data
            total_news = NewsAnnouncement.objects.count()
            active_news = NewsAnnouncement.objects.filter(is_active=True).count()
            
            # News by category
            category_stats = NewsCategory.objects.annotate(
                news_count=Count('newsannouncement')
            ).order_by('-news_count')
            
            # News by priority
            priority_stats = NewsAnnouncement.objects.values('priority').annotate(
                count=Count('priority')
            ).order_by('priority')
            
            # Recent activity (last 30 days)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_news = NewsAnnouncement.objects.filter(
                newsdate__gte=thirty_days_ago
            ).count()
            
            # Most viewed news
            popular_news = NewsAnnouncement.objects.filter(
                is_active=True
            ).order_by('-view_count')[:10]
            
            # Expiring soon (next 7 days)
            seven_days_later = timezone.now() + timedelta(days=7)
            expiring_soon = NewsAnnouncement.objects.filter(
                expiry_date__lte=seven_days_later,
                expiry_date__gt=timezone.now(),
                is_active=True
            ).count()
            
            context = {
                'adminid': adminid,
                'total_news': total_news,
                'active_news': active_news,
                'recent_news': recent_news,
                'expiring_soon': expiring_soon,
                'category_stats': category_stats,
                'priority_stats': priority_stats,
                'popular_news': popular_news,
            }
            
            return render(request, "news_analytics.html", context)
            
    except KeyError:
        return redirect('nouapp:login')

# Enhanced manage_news view with pagination
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_news_enhanced(request):
    """Enhanced news management with pagination and proper statistics"""
    try:
        if request.session['adminid'] is not None:
            adminid = request.session['adminid']
            
            from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
            from django.utils import timezone
            
            # Get filter parameters
            category_filter = request.GET.get('category', '')
            status_filter = request.GET.get('status', 'all')
            priority_filter = request.GET.get('priority', '')
            search_query = request.GET.get('search', '')
            
            # Base queryset for display
            news_list = NewsAnnouncement.objects.all().select_related('category')
            
            # Get all news for statistics (before filtering)
            all_news = NewsAnnouncement.objects.all().select_related('category')
            
            # Calculate statistics from all news
            now = timezone.now()
            
            # Count active news
            active_count = all_news.filter(
                is_active=True,
                publish_date__lte=now
            ).exclude(expiry_date__lt=now).count()
            
            # Count scheduled news (publish_date is in the future)
            scheduled_count = all_news.filter(
                is_active=True,
                publish_date__gt=now
            ).count()
            
            # Count expired news
            expired_count = all_news.filter(
                expiry_date__lt=now
            ).count()
            
            # Count inactive news (manually set to inactive)
            inactive_count = all_news.filter(is_active=False).count()
            
            # Total count
            total_count = all_news.count()
            
            # Apply search to display queryset
            if search_query:
                news_list = news_list.filter(
                    Q(title__icontains=search_query) |
                    Q(newstext__icontains=search_query)
                )
            
            # Apply filters to display queryset
            if category_filter:
                news_list = news_list.filter(category_id=category_filter)
                
            if priority_filter:
                news_list = news_list.filter(priority=priority_filter)
                
            if status_filter == 'active':
                news_list = news_list.filter(
                    is_active=True,
                    publish_date__lte=now
                ).exclude(expiry_date__lt=now)
            elif status_filter == 'expired':
                news_list = news_list.filter(expiry_date__lt=now)
            elif status_filter == 'scheduled':
                news_list = news_list.filter(
                    is_active=True,
                    publish_date__gt=now
                )
            elif status_filter == 'inactive':
                news_list = news_list.filter(is_active=False)
            
            # Order by most recent first
            news_list = news_list.order_by('-newsdate')
            
            # Pagination
            paginator = Paginator(news_list, 20)  # Show 20 news per page
            page = request.GET.get('page')
            
            try:
                news_list = paginator.page(page)
            except PageNotAnInteger:
                news_list = paginator.page(1)
            except EmptyPage:
                news_list = paginator.page(paginator.num_pages)
            
            # Get categories for filter dropdown
            categories = NewsCategory.objects.filter(is_active=True)
            
            # Statistics dictionary
            news_stats = {
                'total_count': total_count,
                'active_count': active_count,
                'scheduled_count': scheduled_count,
                'expired_count': expired_count,
                'inactive_count': inactive_count
            }
            
            return render(request, "manage_news.html", {
                'adminid': adminid,
                'news_list': news_list,
                'categories': categories,
                'current_category': category_filter,
                'current_status': status_filter,
                'current_priority': priority_filter,
                'search_query': search_query,
                'is_paginated': news_list.has_other_pages(),
                'page_obj': news_list,
                'news_stats': news_stats,  # Pass statistics to template
            })
    except KeyError:
        return redirect('nouapp:login')

# View to increment news view count
def increment_news_view(request, news_id):
    """Increment view count for news item (AJAX)"""
    if request.method == 'POST':
        try:
            news = NewsAnnouncement.objects.get(nid=news_id)
            news.view_count += 1
            news.save()
            
            from django.http import JsonResponse
            return JsonResponse({'status': 'success', 'view_count': news.view_count})
        except NewsAnnouncement.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'News not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})