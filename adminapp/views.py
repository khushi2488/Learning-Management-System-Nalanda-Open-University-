from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_control
from nouapp.models import Student, Enquiry, Login
from studentapp.models import StuResponse
from . models import Program, Branch, Year, Material, News
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
            program=Program.objects.all()
            branch=Branch.objects.all()
            year=Year.objects.all()
            return render(request,"studymaterial.html",locals())
    except KeyError:
        return redirect('nouapp:login')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def move(request):
    try:
        if request.session['adminid']!=None:
            adminid=request.session['adminid']
            program=request.POST['program']
            branch=request.POST['branch']
            year=request.POST['year']
            subject=request.POST['subject']
            file_name=request.POST['file_name']
            my_file=request.FILES['my_file']
            mt=Material(program=program,branch=branch,year=year,subject=subject,file_name=file_name,my_file=my_file)
            mt.save()
            return render(request,"studymaterial.html",locals())
    except KeyError:
        return redirect('nouapp:login')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def viewmaterial(request):
    try:
        if request.session['adminid']!=None:
            adminid=request.session['adminid']
            mat=Material.objects.all()
            return render(request,"viewmaterial.html",locals())
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