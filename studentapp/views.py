
from django.shortcuts import render, redirect
from nouapp.models import Student, Login
from django.views.decorators.cache import cache_control
from .models import StuResponse, Question, Answer
from datetime import date
from django.contrib import messages
from adminapp.models import Material, Course, Program, Branch, Year
from django.db.models import Q

# Create your views here.
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def studenthome(request):
    try:
        if request.session['rollno']!=None:
            rollno=request.session['rollno']
            stu=Student.objects.get(rollno=rollno)
            return render(request,"studenthome.html",{'stu':stu})
    except KeyError:
        return redirect('nouapp:login')
    
def studentlogout(request):
        try:
            del request.session['rollno']
        except KeyError:
            return redirect('nouapp:login')
        return redirect('nouapp:login')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def response(request):
    try:
        if request.session['rollno']!=None:
            rollno=request.session['rollno']
            stu=Student.objects.get(rollno=rollno)
            if request.method=="POST":
                responsetype=request.POST['responsetype']
                subject=request.POST['subject']
                responsetext=request.POST['responsetext']
                responsedate=date.today()
                sr=StuResponse(rollno=stu.rollno,name=stu.name,program=stu.program,branch=stu.branch,year=stu.year,contactno=stu.contactno,emailaddress=stu.emailaddress,responsetype=responsetype,subject=subject,responsetext=responsetext,responsedate=responsedate)
                sr.save()
                messages.success(request,'Your Response is Submitted')
            return render(request,"response.html",{'stu':stu})
    except KeyError:
        return redirect('nouapp:login')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def postquestion(request):
    try:
        if request.session['rollno']!=None:
            rollno=request.session['rollno']
            stu=Student.objects.get(rollno=rollno)
            if request.method=="POST":
                question=request.POST['question']
                postedby=stu.name
                posteddate=date.today()
                ques=Question(question=question,postedby=postedby,posteddate=posteddate)
                ques.save()
            ques=Question.objects.all()
            return render(request,"postquestion.html",{'stu':stu,'ques':ques})
    except KeyError:
        return redirect('nouapp:login')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def postanswer(request,qid):
    try:
        if request.session['rollno']!=None:
            rollno=request.session['rollno']
            stu=Student.objects.get(rollno=rollno)
            return render(request,'postanswer.html',{'stu':stu,'qid':qid})
    except KeyError:
        return redirect('nouapp:login')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def postans(request):
    try:
        if request.session['rollno']!=None:
            rollno=request.session['rollno']
            stu=Student.objects.get(rollno=rollno)
            qid=request.POST['qid']
            answer=request.POST['answer']
            answered=stu.name
            posteddate=date.today()
            ans=Answer(answer=answer,answered=answered,posteddate=posteddate,qid=qid)
            ans.save()
            return redirect('studentapp:postquestion')
    except KeyError:
        return redirect('nouapp:login')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def viewanswer(request,qid):
    try:
        if request.session['rollno']!=None:
            rollno=request.session['rollno']
            stu=Student.objects.get(rollno=rollno)
            ans=Answer.objects.filter(qid=qid)
            return render(request,"viewanswer.html",{'stu':stu,'ans':ans})
    except KeyError:
        return redirect('nouapp:login')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def changepassword(request):
    try:
        if request.session['rollno']!=None:
            rollno=request.session['rollno']
            stu=Student.objects.get(rollno=rollno)
            if request.method=='POST':
                oldpassword=request.POST['oldpassword']
                newpassword=request.POST['newpassword']
                confirmpassword=request.POST['confirmpassword']
                presentpassword=Login.objects.get(userid=rollno)
                if oldpassword==presentpassword.password:
                    if oldpassword!=newpassword:
                        if newpassword==confirmpassword:
                            Login.objects.filter(userid=rollno).update(password=newpassword)
                            return redirect('studentapp:studentlogout')
                        else:
                            messages.warning(request,'New Password an Confirm Password must be same..')
                    else:
                        messages.warning(request,'New Password an Old Password must not be same..')
                else:
                    messages.warning(request,'Old Password is incorrect..')
            return render(request,"changepassword.html",{'stu':stu})
    except KeyError:
        return redirect('nouapp:login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def viewmat(request):
    try:
        rollno = request.session.get('rollno')
        if not rollno:
            return redirect('nouapp:login')

        stu = Student.objects.get(rollno=rollno)
        print(f"Student: {stu.name}, Program: {stu.program}, Branch: {stu.branch}, Year: {stu.year}")

        # Map Student text to FK objects (case-insensitive)
        program_obj = Program.objects.filter(program__iexact=stu.program).first()
        branch_obj = Branch.objects.filter(branch__iexact=stu.branch).first()
        year_obj = Year.objects.filter(year__iexact=stu.year).first()

        if not (program_obj and branch_obj and year_obj):
            messages.warning(request, "No matching Program/Branch/Year found.")
            mat = Material.objects.none()
        else:
            # Filter using IDs, ensures correct FK matching
            mat = Material.objects.filter(
                course__program=program_obj,
                course__branch=branch_obj,
                course__year=year_obj,
                is_latest_version=True
            ).select_related(
                'course', 'course__program', 'course__branch', 'course__year', 'category', 'created_by'
            ).order_by('-created_at')

        print(f"Found {mat.count()} materials for this student")

        return render(request, 'viewmat.html', {
            'mat': mat,
            'stu': stu,
            'total_materials': mat.count()
        })

    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Please login again.")
        return redirect('nouapp:login')
    except Exception as e:
        print(f"Error in viewmat: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, "An error occurred while loading materials.")
        return redirect('studentapp:studenthome')


# Optional: Add a function to download materials with logging
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def download_material(request, material_id):
    try:
        # Check if student is logged in
        rollno = request.session.get('rollno')
        if not rollno:
            return redirect('nouapp:login')
        
        # Get student object
        stu = Student.objects.get(rollno=rollno)
        
        # Get material object
        material = Material.objects.get(id=material_id)
        
        # Log the download (optional)
        print(f"Student {stu.name} downloaded material: {material.title}")
        
        # Redirect to the file URL for download
        if material.file:
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(material.file.url)
        else:
            messages.error(request, "File not found.")
            return redirect('studentapp:viewmat')
            
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('nouapp:login')
    except Material.DoesNotExist:
        messages.error(request, "Material not found.")
        return redirect('studentapp:viewmat')
    except Exception as e:
        print(f"Error in download_material: {e}")
        messages.error(request, "Error downloading file.")
        return redirect('studentapp:viewmat')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def viewprofile(request):
    try:
        if request.session['rollno']!=None:
            rollno=request.session['rollno']
            stu=Student.objects.get(rollno=rollno)
            return render(request,"viewprofile.html" , {'stu':stu})
    except KeyError:
        return redirect('nouapp:login')