# adminapp/urls.py - Fixed version

from django.urls import path
from . import views, analytics_views
# from analytics_views import debug_analytics
app_name = "adminapp"

urlpatterns = [
    # Existing admin URLs
    path('adminhome/', views.adminhome, name='adminhome'),
    path('adminlogout/', views.adminlogout, name='adminlogout'),
    path('viewstudent/', views.viewstudent, name='viewstudent'),
    path('viewfeedback/', views.viewfeedback, name='viewfeedback'),
    path('viewenquiry/', views.viewenquiry, name='viewenquiry'),
    path('viewcomplain/', views.viewcomplain, name='viewcomplain'),
    path('studymaterial/', views.studymaterial, name='studymaterial'),
    path('move/', views.move, name='move'),
    path('viewmaterial/', views.viewmaterial, name='viewmaterial'),
    # path('news/', views.news, name='news'),
    
    # Analytics URLs - FIXED
    path('dashboard/', analytics_views.admin_dashboard, name='admin_dashboard'),
    path('analytics-data/', analytics_views.analytics_data, name='analytics_data'),  # Fixed function name
    path('enrollment-analytics/', analytics_views.enrollment_analytics_view, name='enrollment_analytics'),
    path('course-analytics/', analytics_views.course_analytics_view, name='course_analytics'),
    path('performance-analytics/', analytics_views.performance_analytics_view, name='performance_analytics'),
    path('real-time-analytics/', analytics_views.real_time_analytics, name='real_time_analytics'),
    
    # File management system URLs - FIXED path syntax
    path('materials/', views.material_list, name='material_list'),
    path('course/<int:course_id>/materials/', views.material_list, name='course_materials'),
    path('materials/<int:material_id>/', views.material_detail, name='material_detail'),
    path('materials/<int:material_id>/preview/', views.material_preview, name='material_preview'),
    path('materials/<int:material_id>/download/', views.material_download, name='material_download'),
    path('materials/<int:material_id>/delete/', views.delete_material, name='delete_material'),
    
    # Material Creation URLs
    path('course/<int:course_id>/materials/create/', views.create_material, name='create_material'),
    path('materials/<int:material_id>/version/', views.create_material_version, name='create_material_version'),
    
    # Category Management URLs
    path('materials/categories/', views.material_categories, name='material_categories'),
    path('debug-analytics/', analytics_views.debug_analytics, name='debug_analytics'),
    
    # Enhanced News URLs
    # path('news/', views.manage_news, name='manage_news'),
    path('manage-news/', views.manage_news_enhanced, name='manage_news'),# Replace old news URL
    path('news/create/', views.create_news, name='create_news'),
    path('news/<int:news_id>/edit/', views.edit_news, name='edit_news'),
    path('news/<int:news_id>/toggle/', views.toggle_news_status, name='toggle_news_status'),
    path('news/<int:news_id>/delete/', views.delete_news, name='delete_news'),
    path('news/<int:news_id>/pin/', views.pin_news, name='pin_news'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('news/bulk-action/', views.bulk_news_action, name='bulk_news_action'),
path('news/<int:news_id>/duplicate/', views.duplicate_news, name='duplicate_news'),
path('news/<int:news_id>/preview/', views.preview_news, name='preview_news'),

# Academic Data Management URLs
    path('manage-academic-data/', views.manage_academic_data, name='manage_academic_data'),
    path('manage-programs/', views.manage_programs, name='manage_programs'),
    path('manage-branches/', views.manage_branches, name='manage_branches'),
    path('manage-years/', views.manage_years, name='manage_years'),
    
    path('manage-courses/', views.manage_courses, name='manage_courses'),
    path('create-course/', views.create_course, name='create_course'),
    path('edit-course/<int:course_id>/', views.edit_course, name='edit_course'),
#    path('delete-course/<int:course_id>/', views.delete_course, name='delete_course'),
   path('delete-course/<int:course_id>/', views.delete_course_simple, name='delete_course'),
    path('enquiries/', views.admin_enquiry_dashboard, name='admin_enquiry_dashboard'),
    path('enquiries/<int:enquiry_id>/', views.admin_enquiry_detail, name='admin_enquiry_detail'),
]