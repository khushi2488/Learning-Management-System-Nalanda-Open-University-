from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import os

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

class News(models.Model):
    nid = models.AutoField(primary_key=True)
    newstext = models.TextField()
    newsdate = models.CharField(max_length=30)

class Admin_table(models.Model):
    Admin_Id = models.BigAutoField(primary_key=True)
    Admin_Name = models.CharField(max_length=100, null=False)
    Admin_Password = models.CharField(max_length=20, null=False)
    
    def __str__(self):
        return self.Admin_Name