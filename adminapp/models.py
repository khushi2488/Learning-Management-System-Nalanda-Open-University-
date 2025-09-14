from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import os
from nouapp.models import Student
from django.utils import timezone

# Create your models here.
class MaterialCategory(models.Model):
    """Categories for organizing learning materials"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # CSS class for icons
    color_code = models.CharField(max_length=7, default='#007bff')  # Hex color
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Material Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Program(models.Model):
    program = models.CharField(max_length=100)
    
    def __str__(self):
        return self.program

class Branch(models.Model):
    branch = models.CharField(max_length=100)
    
    def __str__(self):
        return self.branch

class Year(models.Model):
    year = models.CharField(max_length=100)
    
    def __str__(self):
        return self.year

class Course(models.Model):
    """Course model that integrates with your existing structure"""
    title = models.CharField(max_length=200)  # Subject name
    description = models.TextField(blank=True)
    
    # Link to your existing models
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    year = models.ForeignKey(Year, on_delete=models.CASCADE, null=True, blank=True)
    
    # Additional course info
    course_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_courses', null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['title']
        
    def __str__(self):
        prog_name = self.program.program if self.program else 'N/A'
        branch_name = self.branch.branch if self.branch else 'N/A'
        year_name = self.year.year if self.year else 'N/A'
        return f"{self.title} - {prog_name} {branch_name} {year_name}"

class Material(models.Model):
    """Enhanced Material model with categories, preview, and versioning"""
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=1)  # assuming course with id=1 exists

    category = models.ForeignKey(MaterialCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # File Information
    file = models.FileField(
        upload_to='materials/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=[
            'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'mp4', 'mp3', 
            'jpg', 'jpeg', 'png', 'gif', 'zip', 'rar'
        ])]
    )
    file_size = models.PositiveIntegerField(default=0)  # in bytes
    file_type = models.CharField(max_length=10, blank=True)
    
    # Preview Information
    preview_image = models.ImageField(upload_to='previews/%Y/%m/%d/', blank=True, null=True)
    preview_text = models.TextField(blank=True)  # For text-based previews
    is_previewable = models.BooleanField(default=False)
    
    # Versioning
    version = models.PositiveIntegerField(default=1)
    parent_material = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='versions')
    is_latest_version = models.BooleanField(default=True)
    version_notes = models.TextField(blank=True)
    
    # Access Control
    is_public = models.BooleanField(default=False)
    requires_enrollment = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_materials')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_materials', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['course', 'title', 'version']
    
    def __str__(self):
        return f"{self.title} (v{self.version})"
    
    def save(self, *args, **kwargs):
        # Auto-detect file type and size
        if self.file:
            self.file_size = self.file.size
            self.file_type = os.path.splitext(self.file.name)[1][1:].lower()
            
            # Auto-set previewable based on file type
            previewable_types = ['pdf', 'txt', 'jpg', 'jpeg', 'png', 'gif', 'mp4']
            self.is_previewable = self.file_type in previewable_types
        
        # Handle versioning
        if self.pk is None:  # New material
            # Check if this is a new version of existing material
            if self.parent_material:
                # Set version number
                latest_version = Material.objects.filter(
                    parent_material=self.parent_material
                ).aggregate(models.Max('version'))['version__max'] or 0
                self.version = latest_version + 1
                
                # Mark previous versions as not latest
                Material.objects.filter(
                    parent_material=self.parent_material,
                    is_latest_version=True
                ).update(is_latest_version=False)
                
                # Mark original as not latest if this is a new version
                if self.parent_material.is_latest_version:
                    self.parent_material.is_latest_version = False
                    self.parent_material.save()
        
        super().save(*args, **kwargs)
    
    def get_file_icon(self):
        """Return appropriate icon class based on file type"""
        icon_mapping = {
            'pdf': 'fas fa-file-pdf text-danger',
            'doc': 'fas fa-file-word text-primary',
            'docx': 'fas fa-file-word text-primary',
            'ppt': 'fas fa-file-powerpoint text-warning',
            'pptx': 'fas fa-file-powerpoint text-warning',
            'txt': 'fas fa-file-alt text-secondary',
            'mp4': 'fas fa-file-video text-info',
            'mp3': 'fas fa-file-audio text-success',
            'jpg': 'fas fa-file-image text-info',
            'jpeg': 'fas fa-file-image text-info',
            'png': 'fas fa-file-image text-info',
            'gif': 'fas fa-file-image text-info',
            'zip': 'fas fa-file-archive text-dark',
            'rar': 'fas fa-file-archive text-dark',
        }
        return icon_mapping.get(self.file_type, 'fas fa-file text-secondary')
    
    def get_formatted_size(self):
        """Return human-readable file size"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024**2:
            return f"{self.file_size/1024:.1f} KB"
        elif self.file_size < 1024**3:
            return f"{self.file_size/(1024**2):.1f} MB"
        else:
            return f"{self.file_size/(1024**3):.1f} GB"
    
    def get_all_versions(self):
        """Get all versions of this material"""
        if self.parent_material:
            # This is a version, get all versions of the parent
            return Material.objects.filter(
                models.Q(id=self.parent_material.id) |
                models.Q(parent_material=self.parent_material)
            ).order_by('-version')
        else:
            # This might be the original, get all its versions
            return Material.objects.filter(
                models.Q(id=self.id) |
                models.Q(parent_material=self)
            ).order_by('-version')
    
    def get_latest_version(self):
        """Get the latest version of this material"""
        return self.get_all_versions().first()

class MaterialAccess(models.Model):
    """Track material access for analytics"""
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=20, choices=[
        ('view', 'View'),
        ('download', 'Download'),
        ('preview', 'Preview'),
    ])
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    accessed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-accessed_at']    

# class News(models.Model):
#     nid = models.AutoField(primary_key=True)
#     newstext = models.TextField()
#     newsdate = models.CharField(max_length=30)

class Admin_table(models.Model):
    Admin_Id = models.BigAutoField(primary_key=True)
    Admin_Name = models.CharField(max_length=100, null=False)
    Admin_Password = models.CharField(max_length=20, null=False)
    
    def __str__(self):
        return self.Admin_Name
    
#___________For the Admin analytic dashboard___________________
class StudentActivity(models.Model):
    """Track student activity using rollno instead of FK"""
    rollno = models.CharField(max_length=50)  # Use rollno like your existing system
    student_name = models.CharField(max_length=100)
    program = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    year = models.CharField(max_length=100)
    
    activity_type = models.CharField(max_length=50, choices=[
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('material_view', 'Material View'),
        ('material_download', 'Material Download'),
        ('question_post', 'Question Post'),
        ('answer_post', 'Answer Post'),
        ('feedback_submit', 'Feedback Submit'),
        ('complaint_submit', 'Complaint Submit'),
    ])
    activity_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    additional_info = models.TextField(blank=True)  # JSON-like string for extra data

    class Meta:
        ordering = ['-activity_date']

class DailyStats(models.Model):
    """Daily aggregated statistics"""
    date = models.DateField(unique=True)
    
    # Student metrics
    total_students = models.PositiveIntegerField(default=0)
    students_logged_in = models.PositiveIntegerField(default=0)
    unique_active_students = models.PositiveIntegerField(default=0)
    
    # Activity metrics
    total_logins = models.PositiveIntegerField(default=0)
    material_views = models.PositiveIntegerField(default=0)
    material_downloads = models.PositiveIntegerField(default=0)
    questions_posted = models.PositiveIntegerField(default=0)
    answers_posted = models.PositiveIntegerField(default=0)
    feedback_submitted = models.PositiveIntegerField(default=0)
    complaints_submitted = models.PositiveIntegerField(default=0)
    
    # Material metrics
    materials_uploaded = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-date']

class ProgramStats(models.Model):
    """Statistics by program"""
    program = models.CharField(max_length=100)
    total_students = models.PositiveIntegerField(default=0)
    active_students_today = models.PositiveIntegerField(default=0)
    materials_count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

class BranchStats(models.Model):
    """Statistics by branch"""
    branch = models.CharField(max_length=100)
    total_students = models.PositiveIntegerField(default=0)
    active_students_today = models.PositiveIntegerField(default=0)
    materials_count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
class NewsCategory(models.Model):
    """Categories for organizing news/announcements"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # CSS icon class
    color_code = models.CharField(max_length=7, default='#007bff')  # Hex color
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "News Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class NewsAnnouncement(models.Model):
    """Enhanced News/Announcements model"""
    
    # Priority levels
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Target audience
    AUDIENCE_CHOICES = [
        ('all', 'All Users'),
        ('students', 'Students Only'),
        ('admins', 'Admins Only'),
        ('specific_program', 'Specific Program'),
        ('specific_branch', 'Specific Branch'),
        ('specific_year', 'Specific Year'),
    ]
    
    # Basic fields (keeping compatibility with your existing News model)
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)  # New: separate title field
    newstext = models.TextField()
    newsdate = models.DateTimeField(default=timezone.now)  # Changed to DateTime
    
    # Enhanced fields
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Visibility and expiry
    is_active = models.BooleanField(default=True)
    publish_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    # Target audience
    target_audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    target_programs = models.TextField(blank=True, help_text="Comma-separated program names")
    target_branches = models.TextField(blank=True, help_text="Comma-separated branch names") 
    target_years = models.TextField(blank=True, help_text="Comma-separated year names")
    
    # Additional metadata
    created_by = models.CharField(max_length=100, blank=True)  # Admin who created it
    attachment = models.FileField(upload_to='news_attachments/', blank=True, null=True)
    is_pinned = models.BooleanField(default=False)  # Pin important announcements
    view_count = models.PositiveIntegerField(default=0)
    # Add these methods to your NewsAnnouncement model in adminapp/models.py
# Add them inside the NewsAnnouncement class, before the Meta class

    def get_current_status(self):
        """Get the current status of this news item"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return 'inactive'
        elif self.publish_date > now:
            return 'scheduled'
        elif self.expiry_date and self.expiry_date < now:
            return 'expired'
        else:
            return 'active'

    def get_status_display(self):
        """Get human-readable status"""
        status = self.get_current_status()
        status_map = {
            'active': 'Active',
            'scheduled': 'Scheduled',
            'expired': 'Expired',
            'inactive': 'Inactive'
        }
        return status_map.get(status, 'Unknown')

    def get_status_class(self):
        """Get CSS class for status badge"""
        status = self.get_current_status()
        class_map = {
            'active': 'badge-success',
            'scheduled': 'badge-info',
            'expired': 'badge-secondary',
            'inactive': 'badge-danger'
        }
        return class_map.get(status, 'badge-secondary')

    def is_visible_to_student(self, student):
        """Check if this news should be visible to a specific student"""
        from django.utils import timezone
        now = timezone.now()
        
        # Check if news is currently active
        if not self.is_active or self.publish_date > now:
            return False
        
        # Check if expired
        if self.expiry_date and self.expiry_date < now:
            return False
        
        # Check audience targeting
        if self.target_audience == 'all':
            return True
        
        elif self.target_audience == 'students':
            # Show to ALL students regardless of program/branch/year
            return True
        
        elif self.target_audience == 'specific':
            # Check specific targeting criteria
            program_match = True
            branch_match = True
            year_match = True
            
            # Check program targeting
            if self.target_programs:
                target_programs = [p.strip() for p in self.target_programs.split(',')]
                program_match = student.program.name in target_programs
            
            # Check branch targeting
            if self.target_branches:
                target_branches = [b.strip() for b in self.target_branches.split(',')]
                branch_match = student.branch.name in target_branches
            
            # Check year targeting
            if self.target_years:
                target_years = [y.strip() for y in self.target_years.split(',')]
                year_match = student.year.name in target_years
            
            return program_match and branch_match and year_match
        
        return False

    def get_target_display(self):
        """Get human-readable target audience"""
        if self.target_audience == 'all':
            return 'Everyone'
        elif self.target_audience == 'students':
            return 'All Students'
        elif self.target_audience == 'specific':
            parts = []
            if self.target_programs:
                parts.append(f"Programs: {self.target_programs}")
            if self.target_branches:
                parts.append(f"Branches: {self.target_branches}")
            if self.target_years:
                parts.append(f"Years: {self.target_years}")
            return " | ".join(parts) if parts else "Specific (no criteria)"
        else:
            return self.get_target_audience_display()

    @property
    def is_currently_active(self):
     """Property to check if news is currently active"""
     return self.get_current_status() == 'active'
    
    class Meta:
        ordering = ['-is_pinned', '-priority', '-publish_date']
        
    def __str__(self):
        return f"{self.title} - {self.newsdate.strftime('%Y-%m-%d')}"
    
    def is_expired(self):
        """Check if the news item has expired"""
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False
    
    def is_published(self):
        """Check if the news item should be published"""
        now = timezone.now()
        return (self.is_active and 
                self.publish_date <= now and 
                not self.is_expired())
    
    def get_priority_class(self):
        """Return CSS class based on priority"""
        priority_classes = {
            'low': 'alert-secondary',
            'normal': 'alert-info', 
            'high': 'alert-warning',
            'urgent': 'alert-danger'
        }
        return priority_classes.get(self.priority, 'alert-info')
    
    
    def can_view(self, user_type, user_program=None, user_branch=None, user_year=None):
        """Check if a user can view this news item"""
        if not self.is_published():
            return False
            
        if self.target_audience == 'all':
            return True
        elif self.target_audience == 'students' and user_type == 'student':
            return True
        elif self.target_audience == 'admins' and user_type == 'admin':
            return True
        elif self.target_audience == 'specific_program':
            if user_program and self.target_programs:
                programs = [p.strip() for p in self.target_programs.split(',')]
                return user_program in programs
        elif self.target_audience == 'specific_branch':
            if user_branch and self.target_branches:
                branches = [b.strip() for b in self.target_branches.split(',')]
                return user_branch in branches
        elif self.target_audience == 'specific_year':
            if user_year and self.target_years:
                years = [y.strip() for y in self.target_years.split(',')]
                return user_year in years
                
        return False
     

# Keep your original News model for backward compatibility, or migrate data
class News(models.Model):
    """Legacy News model - keep for backward compatibility"""
    nid = models.AutoField(primary_key=True)
    newstext = models.TextField()
    newsdate = models.CharField(max_length=30)
    
    class Meta:
        db_table = 'adminapp_news'  # Keep original table name
    