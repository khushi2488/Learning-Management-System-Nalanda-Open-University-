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
]