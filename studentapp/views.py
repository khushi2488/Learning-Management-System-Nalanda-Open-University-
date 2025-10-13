from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_control
from .models import StuResponse, Question, Answer
from datetime import date, datetime
from django.contrib import messages
from adminapp.models import Material, Course, Program, Branch, Year, NewsAnnouncement, NewsCategory
from django.db.models import Q, Count
from adminapp.analytics_utils import log_student_activity
from django.utils import timezone
from nouapp.models import Enquiry, Student, EnquiryReply

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def studenthome(request):
    try:
        if request.session['rollno'] is not None:
            rollno = request.session['rollno']
            stu = Student.objects.select_related('program', 'branch', 'year').get(rollno=rollno)

            # Log login activity
            try:
                log_student_activity(rollno, 'login', request)
            except:
                pass  # Continue even if logging fails

            # Get time-based greeting
            current_hour = datetime.now().hour
            if current_hour < 12:
                greeting = "Good Morning"
                greeting_icon = "☀️"
                greeting_message = "Start your day with learning!"
            elif current_hour < 17:
                greeting = "Good Afternoon"
                greeting_icon = "🌤️"
                greeting_message = "Keep up the great work!"
            else:
                greeting = "Good Evening"
                greeting_icon = "🌙"
                greeting_message = "Evening is perfect for study!"

            # Get student's first name
            student_name = stu.name.split()[0] if stu.name else rollno

            # Get engagement statistics
            # FIXED: Material only filters by course, not program/branch/year
            # Get all materials (or filter by course if student has courses)
            available_materials = Material.objects.filter(is_public=True).count()
            
            # If you want to filter by student's courses, you'd need to:
            # 1. Get the student's enrolled courses
            # 2. Filter materials by those courses
            # Example (uncomment if you have a way to get student's courses):
            # student_courses = stu.courses.all()  # Adjust based on your model
            # available_materials = Material.objects.filter(course__in=student_courses).count()

            # Student's questions and answers - with safe defaults
            my_questions = 0
            my_answers = 0
            
            try:
                my_questions = Question.objects.filter(student=stu).count()
            except Exception as e:
                print(f"Question count error: {e}")
                
            try:
                my_answers = Answer.objects.filter(student=stu).count()
            except Exception as e:
                print(f"Answer count error: {e}")

            # Pending enquiries
            try:
                pending_enquiries = Enquiry.objects.filter(
                    rollno=rollno,
                    status='pending'
                ).count()
            except:
                pending_enquiries = 0

            # Recent news (last 5)
            try:
                recent_news = NewsAnnouncement.objects.filter(
                    is_published=True
                ).order_by('-created_at')[:5]
            except:
                recent_news = []

            # Get latest material uploaded
            latest_material = None
            try:
                # FIXED: Get latest public material or by course
                latest_material = Material.objects.filter(
                    is_public=True
                ).order_by('-created_at').first()
            except:
                pass

            # Calculate engagement score (simple metric)
            engagement_score = min(100, (my_questions * 10) + (my_answers * 5) + 20)

            context = {
                'stu': stu,
                'greeting': greeting,
                'greeting_icon': greeting_icon,
                'greeting_message': greeting_message,
                'student_name': student_name,
                'available_materials': available_materials,
                'my_questions': my_questions,
                'my_answers': my_answers,
                'pending_enquiries': pending_enquiries,
                'recent_news': recent_news,
                'latest_material': latest_material,
                'engagement_score': engagement_score,
            }

            return render(request, "studenthome.html", context)
    except KeyError:
        return redirect('nouapp:login')
    except Exception as e:
        print(f"Error in studenthome view: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, "An error occurred loading the dashboard")
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
            stu=Student.objects.select_related('program', 'branch', 'year').get(rollno=rollno)
            if request.method=="POST":
                responsetype=request.POST['responsetype']
                subject=request.POST['subject']
                responsetext=request.POST['responsetext']
                responsedate=date.today()

                # FIXED: Access the actual string values from ForeignKey relationships
                sr=StuResponse(
                    rollno=stu.rollno,
                    name=stu.name,
                   program=stu.program,      # Pass the Program object
                    branch=stu.branch,        # Pass the Branch object
                    year=stu.year,           # Get string value from Year object
                    contactno=stu.contactno,
                    emailaddress=stu.emailaddress,
                    responsetype=responsetype,
                    subject=subject,
                    responsetext=responsetext,
                    responsedate=responsedate
                )
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
def viewprofile(request):
    try:
        if request.session['rollno']!=None:
            rollno=request.session['rollno']
            stu=Student.objects.select_related('program', 'branch', 'year').get(rollno=rollno)
            return render(request,"viewprofile.html" , {'stu':stu})
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

# FIXED: Updated viewmat view - removed incorrect select_related
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def viewmat(request):
    try:
        rollno = request.session.get('rollno')
        if not rollno:
            return redirect('nouapp:login')

        # FIXED: Use select_related to get related objects efficiently
        stu = Student.objects.select_related('program', 'branch', 'year').get(rollno=rollno)

        # Log material view activity
        log_student_activity(rollno, 'material_view', request)

        # FIXED: Now we have the actual Program, Branch, Year objects
        student_program_obj = stu.program
        student_branch_obj = stu.branch  
        student_year_obj = stu.year

        # Find courses matching the student's program/branch/year directly
        matching_courses = Course.objects.filter(
            program=student_program_obj,
            branch=student_branch_obj,
            year=student_year_obj
        )

        if matching_courses.exists():
            mat = Material.objects.filter(
                course__in=matching_courses,
                is_latest_version=True
            ).select_related('course', 'course__program', 'course__branch', 'course__year', 'category', 'created_by')
        else:
            # If no exact matches, show all materials (or implement fuzzy matching)
            mat = Material.objects.filter(is_latest_version=True).select_related(
                'course', 'course__program', 'course__branch', 'course__year', 'category', 'created_by'
            )

        return render(request, 'viewmat.html', {'mat': mat, 'stu': stu})

    except Student.DoesNotExist:
        return redirect('nouapp:login')
    except Exception as e:
        print(f"Error in viewmat: {e}")
        return redirect('nouapp:login')

# FIXED: Updated download_material view
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
            stu=Student.objects.get(rollno=rollno)  # REMOVED select_related
            return render(request,"viewprofile.html" , {'stu':stu})
    except KeyError:
        return redirect('nouapp:login')
    

# FIXED: Enhanced student news view - removed incorrect select_related
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def student_news(request):
    """Enhanced view for students to see news with proper ForeignKey filtering"""
    try:
        if request.session['rollno'] is not None:
            rollno = request.session['rollno']
            # FIXED: Use select_related to efficiently get related objects
            stu = Student.objects.select_related('program', 'branch', 'year').get(rollno=rollno)

            # Get category filter if provided
            category_filter = request.GET.get('category', '')

            # Get all active news that are currently published and not expired
            now = timezone.now()
            news_query = NewsAnnouncement.objects.filter(
                is_active=True,
                publish_date__lte=now
            ).exclude(
                expiry_date__lt=now
            ).select_related('category').prefetch_related(
                'target_programs', 'target_branches', 'target_years'
            ).order_by('-is_pinned', '-publish_date')

            # Apply category filter if specified
            if category_filter:
                news_query = news_query.filter(category_id=category_filter)

            # Filter news based on target audience
            visible_news = []
            for news in news_query:
                should_show = False

                if news.target_audience == 'all':
                    should_show = True

                elif news.target_audience == 'students':
                    should_show = True

                elif news.target_audience == 'specific_program':
                    # FIXED: Check if student's program object is in target_programs
                    if news.target_programs.filter(id=stu.program.id).exists():
                        should_show = True

                elif news.target_audience == 'specific_branch':
                    # FIXED: Check if student's branch object is in target_branches
                    if news.target_branches.filter(id=stu.branch.id).exists():
                        should_show = True

                elif news.target_audience == 'specific_year':
                    # FIXED: Check if student's year object is in target_years
                    if news.target_years.filter(id=stu.year.id).exists():
                        should_show = True

                if should_show:
                    visible_news.append(news)

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
    
    from django.http import JsonResponse
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

# FIXED: Student news view with proper audience filtering - removed incorrect select_related
def get_student_news(request, student_id=None):
    """Get news for students with proper ManyToMany audience filtering"""
    try:
        now = timezone.now()
        
        # Get active, published, non-expired news
        base_queryset = NewsAnnouncement.objects.filter(
            is_active=True,
            publish_date__lte=now
        ).filter(
            Q(expiry_date__isnull=True) | Q(expiry_date__gt=now)
        ).select_related('category').prefetch_related(
            'target_programs', 'target_branches', 'target_years'
        ).order_by('-is_pinned', '-newsdate')
        
        if student_id:
            # Get student details for targeted filtering
            try:
                student = Student.objects.get(id=student_id)  # REMOVED select_related
                
                # Filter based on target audience
                filtered_news = []
                
                for news in base_queryset:
                    should_show = False
                    
                    if news.target_audience == 'all':
                        # Show to everyone
                        should_show = True
                    
                    elif news.target_audience == 'students':
                        # Show to ALL students
                        should_show = True
                    
                    elif news.target_audience == 'specific_program':
                        # Check if student's program matches any target programs
                        target_programs = news.target_programs.values_list('program', flat=True)
                        if student.program in target_programs:
                            should_show = True
                    
                    elif news.target_audience == 'specific_branch':
                        # Check if student's branch matches any target branches
                        target_branches = news.target_branches.values_list('branch', flat=True)
                        if student.branch in target_branches:
                            should_show = True
                    
                    elif news.target_audience == 'specific_year':
                        # Check if student's year matches any target years
                        target_years = news.target_years.values_list('year', flat=True)
                        if student.year in target_years:
                            should_show = True
                    
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
# Example fix for creating StuResponse objects in studentapp views

def submit_feedback(request):  # or whatever your function is called
    if request.method == "POST":
        rollno = request.session['rollno']
        
        try:
            # Get the student object to access ForeignKey relationships
            student = Student.objects.get(rollno=rollno)
            
            # Create StuResponse with ForeignKey objects
            sturesponse = StuResponse(
                rollno=rollno,
                name=student.name,
                program=student.program,      # ForeignKey object
                branch=student.branch,        # ForeignKey object  
                year=student.year,            # ForeignKey object
                contactno=student.contactno,
                emailaddress=student.emailaddress,
                responsetype=request.POST['responsetype'],  # 'feedback' or 'complain'
                subject=request.POST['subject'],
                responsetext=request.POST['responsetext'],
                responsedate=date.today()
            )
            sturesponse.save()
            messages.success(request, 'Response submitted successfully!')
            
        except Student.DoesNotExist:
            messages.error(request, 'Student not found')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            
    return render(request, "feedback_form.html")  # your template    



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def student_enquiry_dashboard(request):
    """Display all enquiries for the logged-in student"""
    try:
        rollno = request.session.get('rollno')
        if not rollno:
            return redirect('nouapp:login')
        
        stu = Student.objects.get(rollno=rollno)
        
        # Query using emailaddress field
        enquiries = Enquiry.objects.filter(emailaddress=stu.emailaddress).order_by('-id')
        
        context = {
            'stu': stu,
            'enquiries': enquiries,
            'total_enquiries': enquiries.count(),
            'pending_enquiries': enquiries.filter(status='pending').count(),
            'resolved_enquiries': enquiries.filter(status='resolved').count(),
        }
        return render(request, 'enquiry_dashboard.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, "Student record not found.")
        return redirect('nouapp:login')
    except Exception as e:
        # print(f"Error in student_enquiry_dashboard: {e}")
        # messages.error(request, "An error occurred. Please try again.")
        # return redirect('studentapp:studenthome')
        print(f"CRITICAL ERROR TYPE: {type(e).__name__} - MESSAGE: {e}")
        # !!! RAISE THE EXCEPTION TO GET THE FULL TRACEBACK !!!
        raise e 


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_enquiry(request):
    """Create a new enquiry"""
    try:
        rollno = request.session.get('rollno')
        if not rollno:
            return redirect('nouapp:login')
        
        stu = Student.objects.get(rollno=rollno)
        
        if request.method == 'POST':
            subject = request.POST.get('subject', '').strip()
            message = request.POST.get('message', '').strip()
            category = request.POST.get('category', '')
            priority = request.POST.get('priority', 'low')
            
            if not subject or not message:
                messages.error(request, 'Subject and message are required!')
                return render(request, 'create_enquiry.html', {'stu': stu})
            
            Enquiry.objects.create(
                name=stu.name,
                emailaddress=stu.emailaddress,  # Use emailaddress
                contactno=stu.contactno,
                address='',
                subject=subject,
                message=message,
                category=category,
                priority=priority,
                status='pending'
            )
            messages.success(request, 'Enquiry submitted successfully!')
            return redirect('studentapp:student_enquiry_dashboard')
        
        return render(request, 'create_enquiry.html', {'stu': stu})
        
    except Student.DoesNotExist:
        messages.error(request, "Student record not found.")
        return redirect('nouapp:login')
    except Exception as e:
        print(f"Error in create_enquiry: {e}")
        messages.error(request, f"Error creating enquiry: {str(e)}")
        return redirect('studentapp:studenthome')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def enquiry_detail(request, enquiry_id):
    """View enquiry details and replies"""
    try:
        rollno = request.session.get('rollno')
        if not rollno:
            return redirect('nouapp:login')
        
        stu = Student.objects.get(rollno=rollno)
        
        # Get enquiry and verify ownership
        enquiry = get_object_or_404(Enquiry, id=enquiry_id, emailaddress=stu.emailaddress)
        
        if request.method == 'POST':
            reply_message = request.POST.get('reply_message', '').strip()
            if reply_message:
                from django.contrib.auth.models import User
                user, _ = User.objects.get_or_create(
                    username=f'student_{rollno}',
                    defaults={'email': stu.emailaddress}
                )
                
                EnquiryReply.objects.create(
                    enquiry=enquiry,
                    user=user,
                    message=reply_message,
                    is_admin=False
                )
                messages.success(request, 'Reply added successfully!')
                return redirect('studentapp:enquiry_detail', enquiry_id=enquiry_id)
        
        context = {
            'stu': stu,
            'enquiry': enquiry,
            'replies': enquiry.replies.all().order_by('created_at')
        }
        return render(request, 'enquiry_detail.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, "Student record not found.")
        return redirect('nouapp:login')
    except Exception as e:
        print(f"Error in enquiry_detail: {e}")
        messages.error(request, "An error occurred.")
        return redirect('studentapp:student_enquiry_dashboard')