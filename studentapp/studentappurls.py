 
from django.urls import path
from . import views

app_name = 'studentapp'

urlpatterns = [
    # Student Dashboard and Home
    path('', views.studenthome, name='studenthome'),
    path('studenthome/', views.studenthome, name='studenthome'),
    path('studentlogout/', views.studentlogout, name='studentlogout'),
    
    # Student Response and Feedback
    path('response/', views.response, name='response'),
    
    # Q&A System
    path('postquestion/', views.postquestion, name='postquestion'),
    path('postanswer/<int:qid>/', views.postanswer, name='postanswer'),
    path('postans/', views.postans, name='postans'),
    path('viewanswer/<int:qid>/', views.viewanswer, name='viewanswer'),
    
    # Profile and Password Management
    path('changepassword/', views.changepassword, name='changepassword'),
    path('viewprofile/', views.viewprofile, name='viewprofile'),
    
    # Study Materials - Updated
    path('viewmat/', views.viewmat, name='viewmat'),
    path('download/<int:material_id>/', views.download_material, name='download_material'),
    
    # path('download-material/<int:material_id>/', views.download_material, name='download_material'),
    path('news/', views.student_news, name='student_news'),
     path('enquiries/', views.student_enquiry_dashboard, name='student_enquiry_dashboard'),
    path('enquiries/create/', views.create_enquiry, name='create_enquiry'),
    path('enquiries/<int:enquiry_id>/', views.enquiry_detail, name='enquiry_detail'),
]
