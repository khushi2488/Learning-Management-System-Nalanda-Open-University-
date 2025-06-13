from django.contrib import admin
from . models import StuResponse,Question,Answer

# Register your models here.
admin.site.register(StuResponse)
admin.site.register(Question)
admin.site.register(Answer)