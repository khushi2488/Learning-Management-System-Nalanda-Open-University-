from django.urls import path
from . import views

urlpatterns=[
    path('adminhome/',views.adminhome,name='adminhome'),
    path('adminlogout/',views.adminlogout,name='adminlogout'),
    path('viewstudent/',views.viewstudent,name='viewstudent'),
    path('viewfeedback/',views.viewfeedback,name='viewfeedback'),
    path('viewenquiry/',views.viewenquiry,name='viewenquiry'),
    path('viewcomplain/',views.viewcomplain,name='viewcomplain'),
    path('studymaterial/',views.studymaterial,name='studymaterial'),
    path('move/',views.move,name='move'),
    path('viewmaterial/',views.viewmaterial,name='viewmaterial'),
    path('news/',views.news,name='news'),
    # for the file management system
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
]