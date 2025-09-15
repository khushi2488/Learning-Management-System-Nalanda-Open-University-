from django.shortcuts import render, redirect
from nouapp.models import Student, Login
from django.views.decorators.cache import cache_control
from .models import StuResponse, Question, Answer
from datetime import date
from django.contrib import messages
from adminapp.models import Material, Course, Program, Branch, Year, NewsAnnouncement, NewsCategory
from django.db.models import Q
from adminapp.analytics_utils import log_student_activity
from django.utils import timezone


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
    

# Enhanced student news view
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def student_news(request):
    """Enhanced view for students to see news with proper program filtering"""
    try:
        if request.session['rollno'] is not None:
            rollno = request.session['rollno']
            stu = Student.objects.get(rollno=rollno)
            
            # Debug: Print student info
            print(f"DEBUG: Student program: '{stu.program}', branch: '{stu.branch}', year: '{stu.year}'")
            
            # Get category filter if provided
            category_filter = request.GET.get('category', '')
            
            # Get all active news that are currently published and not expired
            now = timezone.now()
            news_query = NewsAnnouncement.objects.filter(
                is_active=True,
                publish_date__lte=now
            ).exclude(
                expiry_date__lt=now
            ).select_related('category').order_by('-is_pinned', '-publish_date')
            
            # Apply category filter if specified
            if category_filter:
                news_query = news_query.filter(category_id=category_filter)
            
            # Filter news based on target audience
            visible_news = []
            for news in news_query:
                should_show = False
                
                print(f"DEBUG: Processing news '{news.title}' - target_audience: '{news.target_audience}'")
                
                if news.target_audience == 'all':
                    should_show = True
                    print(f"DEBUG: Showing '{news.title}' - target audience is 'all'")
                    
                elif news.target_audience == 'students':
                    should_show = True
                    print(f"DEBUG: Showing '{news.title}' - target audience is 'students'")
                    
                elif news.target_audience == 'specific_program' and news.target_programs:
                    # Handle program-specific targeting
                    target_programs = [p.strip().lower() for p in news.target_programs.split(',')]
                    student_program = stu.program.strip().lower()
                    
                    print(f"DEBUG: Program check - target_programs: {target_programs}, student_program: '{student_program}'")
                    
                    if student_program in target_programs:
                        should_show = True
                        print(f"DEBUG: Showing '{news.title}' - program match found")
                    else:
                        # Try partial matching for program names
                        for target_prog in target_programs:
                            if target_prog in student_program or student_program in target_prog:
                                should_show = True
                                print(f"DEBUG: Showing '{news.title}' - partial program match: '{target_prog}' ~ '{student_program}'")
                                break
                    
                elif news.target_audience == 'specific_branch' and news.target_branches:
                    # Handle branch-specific targeting
                    target_branches = [b.strip().lower() for b in news.target_branches.split(',')]
                    student_branch = stu.branch.strip().lower()
                    
                    print(f"DEBUG: Branch check - target_branches: {target_branches}, student_branch: '{student_branch}'")
                    
                    if student_branch in target_branches:
                        should_show = True
                        print(f"DEBUG: Showing '{news.title}' - branch match found")
                    else:
                        # Try partial matching for branch names
                        for target_branch in target_branches:
                            if target_branch in student_branch or student_branch in target_branch:
                                should_show = True
                                print(f"DEBUG: Showing '{news.title}' - partial branch match: '{target_branch}' ~ '{student_branch}'")
                                break
                    
                elif news.target_audience == 'specific_year' and news.target_years:
                    # Handle year-specific targeting
                    target_years = [y.strip().lower() for y in news.target_years.split(',')]
                    student_year = stu.year.strip().lower()
                    
                    print(f"DEBUG: Year check - target_years: {target_years}, student_year: '{student_year}'")
                    
                    if student_year in target_years:
                        should_show = True
                        print(f"DEBUG: Showing '{news.title}' - year match found")
                    else:
                        # Try partial matching for year names
                        for target_year in target_years:
                            if target_year in student_year or student_year in target_year:
                                should_show = True
                                print(f"DEBUG: Showing '{news.title}' - partial year match: '{target_year}' ~ '{student_year}'")
                                break
                
                elif news.target_audience == 'specific':
                    # Handle combined specific targeting (program AND branch AND year)
                    program_match = True
                    branch_match = True
                    year_match = True
                    
                    # Check program targeting
                    if news.target_programs:
                        target_programs = [p.strip().lower() for p in news.target_programs.split(',')]
                        student_program = stu.program.strip().lower()
                        program_match = student_program in target_programs
                        
                        if not program_match:
                            # Try partial matching
                            for target_prog in target_programs:
                                if target_prog in student_program or student_program in target_prog:
                                    program_match = True
                                    break
                    
                    # Check branch targeting
                    if news.target_branches:
                        target_branches = [b.strip().lower() for b in news.target_branches.split(',')]
                        student_branch = stu.branch.strip().lower()
                        branch_match = student_branch in target_branches
                        
                        if not branch_match:
                            # Try partial matching
                            for target_branch in target_branches:
                                if target_branch in student_branch or student_branch in target_branch:
                                    branch_match = True
                                    break
                    
                    # Check year targeting
                    if news.target_years:
                        target_years = [y.strip().lower() for y in news.target_years.split(',')]
                        student_year = stu.year.strip().lower()
                        year_match = student_year in target_years
                        
                        if not year_match:
                            # Try partial matching
                            for target_year in target_years:
                                if target_year in student_year or student_year in target_year:
                                    year_match = True
                                    break
                    
                    should_show = program_match and branch_match and year_match
                    print(f"DEBUG: Combined check - program: {program_match}, branch: {branch_match}, year: {year_match}, show: {should_show}")
                
                if should_show:
                    visible_news.append(news)
            
            print(f"DEBUG: Total visible news: {len(visible_news)}")
            
            # Get active categories for filter dropdown
            categories = NewsCategory.objects.filter(is_active=True).order_by('name')
            
            return render(request, "student_news.html", {
                'stu': stu,
                'news_list': visible_news,
                'categories': categories,
                'current_category': category_filter
            })
    except KeyError:
        return redirect('nouapp:login')
    except Student.DoesNotExist:
        return redirect('nouapp:login')
    except Exception as e:
        print(f"ERROR in student_news: {e}")
        return redirect('nouapp:login')
# Optional: Simple view to increment news view count when student reads news
def increment_news_view(request, news_id):
    """Increment view count when student views news"""
    if request.method == 'POST':
        try:
            news = NewsAnnouncement.objects.get(nid=news_id)
            news.view_count = (news.view_count or 0) + 1
            news.save()
            
            from django.http import JsonResponse
            return JsonResponse({'status': 'success'})
        except NewsAnnouncement.DoesNotExist:
            pass
    
    return JsonResponse({'status': 'error'})

# Alternative simple view if you don't have enhanced NewsAnnouncement model yet
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def simple_student_news(request):
    """Very simple news view using basic News model"""
    try:
        if request.session['rollno'] is not None:
            rollno = request.session['rollno']
            stu = Student.objects.get(rollno=rollno)
            
            # If you're still using the old News model
            from adminapp.models import News
            news_list = News.objects.all().order_by('-nid')  # Latest first
            
            return render(request, "simple_student_news.html", {
                'stu': stu,
                'news_list': news_list
            })
    except KeyError:
        return redirect('nouapp:login')
    except Student.DoesNotExist:
        return redirect('nouapp:login')
    # FIXED: Student news view with proper audience filtering
def get_student_news(request, student_id=None):
    """Get news for students with proper audience filtering"""
    try:
        now = timezone.now()
        
        # Get active, published, non-expired news
        base_queryset = NewsAnnouncement.objects.filter(
            is_active=True,
            publish_date__lte=now
        ).filter(
            Q(expiry_date__isnull=True) | Q(expiry_date__gt=now)
        ).select_related('category').order_by('-is_pinned', '-newsdate')
        
        if student_id:
            # Get student details for targeted filtering
            try:
                student = Student.objects.select_related('program', 'branch', 'year').get(id=student_id)
                
                # Filter based on target audience
                filtered_news = []
                
                for news in base_queryset:
                    should_show = False
                    
                    if news.target_audience == 'all':
                        # Show to everyone
                        should_show = True
                    
                    elif news.target_audience == 'students':
                        # FIXED: Show to ALL students, not just specific ones
                        should_show = True
                    
                    elif news.target_audience == 'specific':
                        # Check specific targeting criteria
                        program_match = True
                        branch_match = True
                        year_match = True
                        
                        # Check program targeting
                        if news.target_programs:
                            target_programs = [p.strip() for p in news.target_programs.split(',')]
                            program_match = student.program.name in target_programs
                        
                        # Check branch targeting
                        if news.target_branches:
                            target_branches = [b.strip() for b in news.target_branches.split(',')]
                            branch_match = student.branch.name in target_branches
                        
                        # Check year targeting
                        if news.target_years:
                            target_years = [y.strip() for y in news.target_years.split(',')]
                            year_match = student.year.name in target_years
                        
                        should_show = program_match and branch_match and year_match
                    
                    if should_show:
                        filtered_news.append(news)
                
                return filtered_news
                
            except Student.DoesNotExist:
                # If student not found, show general news only
                return base_queryset.filter(target_audience__in=['all', 'students'])
        
        else:
            # No specific student, show all public news
            return base_queryset.filter(target_audience__in=['all', 'students'])
            
    except Exception as e:
        print(f"Error in get_student_news: {e}")
        return []