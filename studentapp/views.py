
from django.shortcuts import render, redirect
from nouapp.models import Student, Login
from django.views.decorators.cache import cache_control
from .models import StuResponse, Question, Answer
from datetime import date
from django.contrib import messages
from adminapp.models import Material, Course, Program, Branch, Year
from django.db.models import Q
from adminapp.analytics_utils import log_student_activity


# Create your views here.
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def studenthome(request):
    try:
        if request.session['rollno']!=None:
            rollno=request.session['rollno']
            stu=Student.objects.get(rollno=rollno)
            
            # Log login activity
            log_student_activity(rollno, 'login', request)
            
            return render(request,"studenthome.html",{'stu':stu})
    except KeyError:
        return redirect('nouapp:login')

    
def studentlogout(request):
    try:
        rollno = request.session['rollno']
        
        # Log logout activity before deleting session
        log_student_activity(rollno, 'logout', request)
        
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
                
                # Log activity
                activity_type = 'feedback_submit' if responsetype == 'feedback' else 'complaint_submit'
                log_student_activity(rollno, activity_type, request, f"Subject: {subject}")
                
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
                
                # Log question post activity
                log_student_activity(rollno, 'question_post', request, f"Question ID: {ques.qid}")
                
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
            
            # Log answer post activity
            log_student_activity(rollno, 'answer_post', request, f"Question ID: {qid}")
            
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

# Update your viewmat view
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def viewmat(request):
    try:
        rollno = request.session.get('rollno')
        if not rollno:
            return redirect('nouapp:login')
        
        stu = Student.objects.get(rollno=rollno)
        
        # Log material view activity
        log_student_activity(rollno, 'material_view', request)
        
        # ... your existing material filtering logic ...
        from adminapp.models import Program, Branch, Year, Course
        
        program_obj = Program.objects.filter(program__iexact=stu.program).first()
        branch_obj = Branch.objects.filter(branch__iexact=stu.branch).first()  
        year_obj = Year.objects.filter(year__iexact=stu.year).first()
        
        if not all([program_obj, branch_obj, year_obj]):
            # Your flexible matching logic
            program_obj = Program.objects.filter(
                Q(program__icontains=stu.program) |
                Q(program__icontains='computer') if 'computer' in stu.program.lower() else Q() |
                Q(program__icontains='tech') if 'tech' in stu.program.lower() else Q()
            ).first()
            
            branch_obj = Branch.objects.filter(
                Q(branch__icontains=stu.branch) |
                Q(branch__icontains='computer') if 'computer' in stu.branch.lower() else Q() |
                Q(branch__icontains='science') if 'science' in stu.branch.lower() else Q()
            ).first()
            
            year_obj = Year.objects.filter(
                Q(year__icontains=stu.year) |
                Q(year__icontains='first') if 'first' in stu.year.lower() else Q() |
                Q(year__icontains='1') if any(char in stu.year.lower() for char in ['1', 'first']) else Q()
            ).first()
        
        if not all([program_obj, branch_obj, year_obj]):
            mat = Material.objects.filter(is_latest_version=True).select_related(
                'course', 'course__program', 'course__branch', 'course__year', 'category', 'created_by'
            )
            context = {'mat': mat, 'stu': stu, 'debug_mode': True}
            return render(request, 'viewmat.html', context)
        
        matching_courses = Course.objects.filter(
            program=program_obj,
            branch=branch_obj,
            year=year_obj
        )
        
        if matching_courses.exists():
            mat = Material.objects.filter(
                course__in=matching_courses,
                is_latest_version=True
            ).select_related('course', 'course__program', 'course__branch', 'course__year', 'category', 'created_by')
        else:
            mat = Material.objects.none()
        
        return render(request, 'viewmat.html', {'mat': mat, 'stu': stu})
        
    except Student.DoesNotExist:
        return redirect('nouapp:login')
    except Exception as e:
        print(f"Error in viewmat: {e}")
        return redirect('nouapp:login')

# Optional: Add a function to download materials with logging
# Add a new view for tracking material downloads
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def download_material(request, material_id):
    """Track material downloads"""
    try:
        rollno = request.session.get('rollno')
        if not rollno:
            return redirect('nouapp:login')
        
        material = Material.objects.get(id=material_id)
        
        # Log download activity
        log_student_activity(rollno, 'material_download', request, f"Material: {material.title}")
        
        # Serve the file
        from django.http import FileResponse
        import mimetypes
        
        response = FileResponse(
            material.file.open(),
            content_type=mimetypes.guess_type(material.file.path)[0],
            as_attachment=True,
            filename=material.file.name.split('/')[-1]
        )
        
        return response
        
    except Material.DoesNotExist:
        messages.error(request, "Material not found")
        return redirect('studentapp:viewmat')
    except Exception as e:
        print(f"Error in download_material: {e}")
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