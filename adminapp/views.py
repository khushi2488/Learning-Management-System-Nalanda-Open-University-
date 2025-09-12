from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import User
from django.contrib import messages
from nouapp.models import Student, Enquiry, Login
from studentapp.models import StuResponse
from .models import Program, Branch, Year, Material, News, Course, MaterialCategory
from datetime import date

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