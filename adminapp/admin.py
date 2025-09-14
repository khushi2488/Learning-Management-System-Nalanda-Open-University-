from django.contrib import admin
from django.utils.html import format_html
from .models import Program, Branch, Year, Material, News, Admin_table, MaterialCategory, MaterialAccess , Course , NewsCategory ,NewsAnnouncement

# Register simple models directly
admin.site.register(Program)
admin.site.register(Branch)
admin.site.register(Year)
admin.site.register(News)
admin.site.register(NewsCategory)
admin.site.register(NewsAnnouncement)
admin.site.register(Admin_table)
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'program', 'branch', 'year', 'course_code', 'instructor', 'is_active')
    search_fields = ('title', 'course_code')
@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'color_preview', 'icon', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 50%; display: inline-block;"></div>',
            obj.color_code
        )
    color_preview.short_description = 'Color'

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'course', 'category', 'file_type', 'version', 
        'is_latest_version', 'view_count', 'download_count', 
        'created_by', 'created_at'
    ]
    list_filter = [
        'file_type', 'category', 'is_latest_version', 
        'is_public', 'requires_enrollment', 'created_at'
    ]
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = [
        'file_size', 'file_type', 'version', 'view_count', 
        'download_count', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'course', 'category')
        }),
        ('File Information', {
            'fields': ('file', 'file_size', 'file_type', 'preview_image', 'preview_text', 'is_previewable')
        }),
        ('Versioning', {
            'fields': ('version', 'parent_material', 'is_latest_version', 'version_notes'),
            'classes': ('collapse',)
        }),
        ('Access Control', {
            'fields': ('is_public', 'requires_enrollment')
        }),
        ('Statistics', {
            'fields': ('view_count', 'download_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new material
            obj.created_by = request.user
        else:  # Updating existing material
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(MaterialAccess)
class MaterialAccessAdmin(admin.ModelAdmin):
    list_display = ['material', 'user', 'access_type', 'ip_address', 'accessed_at']
    list_filter = ['access_type', 'accessed_at']
    search_fields = ['material__title', 'user__username', 'ip_address']
    readonly_fields = ['accessed_at']
    date_hierarchy = 'accessed_at'
    
    def has_add_permission(self, request):
        return False  # Don't allow manual creation of access logs
    
    def has_change_permission(self, request, obj=None):
        return False  # Don't allow editing of access logs
