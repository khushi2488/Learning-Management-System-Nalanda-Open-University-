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
        # Check if student is logged in
        rollno = request.session.get('rollno')
        if not rollno:
            return redirect('nouapp:login')
        
        # Get student object
        stu = Student.objects.get(rollno=rollno)
        print(f"Student: {stu.program}, {stu.branch}, {stu.year}")
        
        # Debug: Check what data exists in the database
        print("Available programs:", [p.program for p in Program.objects.all()])
        print("Available branches:", [b.branch for b in Branch.objects.all()]) 
        print("Available years:", [y.year for y in Year.objects.all()])
        
        # Try to find exact matches first
        program_obj = Program.objects.filter(program__iexact=stu.program).first()
        branch_obj = Branch.objects.filter(branch__iexact=stu.branch).first()  
        year_obj = Year.objects.filter(year__iexact=stu.year).first()
        
        print(f"Exact matches - Program: {program_obj}, Branch: {branch_obj}, Year: {year_obj}")
        
        # If no exact matches, try flexible matching
        if not program_obj:
            # Try case-insensitive partial matching for program
            program_obj = Program.objects.filter(
                Q(program__icontains=stu.program) |
                Q(program__icontains='computer') if 'computer' in stu.program.lower() else Q() |
                Q(program__icontains='tech') if 'tech' in stu.program.lower() else Q()
            ).first()
            print(f"Flexible program match: {program_obj}")
            
        if not branch_obj:
            # Try case-insensitive partial matching for branch
            branch_obj = Branch.objects.filter(
                Q(branch__icontains=stu.branch) |
                Q(branch__icontains='computer') if 'computer' in stu.branch.lower() else Q() |
                Q(branch__icontains='science') if 'science' in stu.branch.lower() else Q()
            ).first()
            print(f"Flexible branch match: {branch_obj}")
            
        if not year_obj:
            # Try case-insensitive partial matching for year
            year_obj = Year.objects.filter(
                Q(year__icontains=stu.year) |
                Q(year__icontains='first') if 'first' in stu.year.lower() else Q() |
                Q(year__icontains='1') if any(char in stu.year.lower() for char in ['1', 'first']) else Q()
            ).first()
            print(f"Flexible year match: {year_obj}")
        
        # If still no matches found, create debug info and show all materials
        if not all([program_obj, branch_obj, year_obj]):
            print("No matches found for student's program/branch/year")
            print(f"Student details - Program: '{stu.program}', Branch: '{stu.branch}', Year: '{stu.year}'")
            
            # Show all materials for debugging
            mat = Material.objects.filter(is_latest_version=True).select_related(
                'course', 'course__program', 'course__branch', 'course__year', 'category', 'created_by'
            )
            
            context = {
                'mat': mat, 
                'stu': stu, 
                'debug_mode': True,
                'debug_info': {
                    'student_program': stu.program,
                    'student_branch': stu.branch,
                    'student_year': stu.year,
                    'available_programs': [p.program for p in Program.objects.all()],
                    'available_branches': [b.branch for b in Branch.objects.all()],
                    'available_years': [y.year for y in Year.objects.all()],
                    'found_program': program_obj,
                    'found_branch': branch_obj,
                    'found_year': year_obj,
                }
            }
            return render(request, 'viewmaterial.html', context)
        
        # Find courses that match the student's profile
        matching_courses = Course.objects.filter(
            program=program_obj,
            branch=branch_obj,
            year=year_obj
        )
        print(f"Found {matching_courses.count()} matching courses")
        
        if matching_courses.exists():
            # Get materials for these courses
            mat = Material.objects.filter(
                course__in=matching_courses,
                is_latest_version=True
            ).select_related('course', 'course__program', 'course__branch', 'course__year', 'category', 'created_by')
            print(f"Found {mat.count()} materials for student")
        else:
            mat = Material.objects.none()
            print("No matching courses found")
        
        return render(request, 'viewmaterial.html', {'mat': mat, 'stu': stu})
        
    except Student.DoesNotExist:
        print("Student not found")
        return redirect('nouapp:login')
    except Exception as e:
        print(f"Error in viewmat: {e}")
        import traceback
        traceback.print_exc()
        return redirect('nouapp:login')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def viewprofile(request):
    try:
        if request.session['rollno']!=None:
            rollno=request.session['rollno']
            stu=Student.objects.get(rollno=rollno)
            return render(request,"viewprofile.html" , {'stu':stu})
    except KeyError:
        return redirect('nouapp:login')