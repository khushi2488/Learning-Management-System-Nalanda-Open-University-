from django.urls import path
from . import views

urlpatterns=[
    path('',views.index,name='index'),
    path('aboutus/',views.aboutus,name='aboutus'),
    path('registration/',views.registration,name='registration'),
    path('login/',views.login,name='login'),
    path('contactus/',views.contactus,name='contactus'),
    path('courses/',views.courses,name='courses'),
    path('services/',views.services,name='services'),
    path('chat/', views.chat_api, name='chat_api'),
]