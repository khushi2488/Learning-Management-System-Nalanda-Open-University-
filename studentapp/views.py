
from django.shortcuts import render, redirect, get_object_or_404
from nouapp.models import Student, Login
from django.views.decorators.cache import cache_control
from .models import StuResponse, Question, Answer, Submission
from datetime import date
from django.contrib import messages
from adminapp.models import Material, Course, Program, Branch, Year, Assignment
from django.db.models import Q
from adminapp.analytics_utils import log_student_activity
from .forms import SubmissionForm

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
                    program=stu.program.program,  # Get string value from Program object
                    branch=stu.branch.branch,     # Get string value from Branch object
                    year=stu.year.year,           # Get string value from Year object
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

#____________Assignment Views______________________

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def list_assignments(request):
    """List assignments for the student"""
    try:
        if request.session['rollno'] is not None:
            rollno = request.session['rollno']
            stu = Student.objects.get(rollno=rollno)
            assignments = Assignment.objects.select_related('course').filter(is_active=True)
            return render(request, 'studentapp/assignment_list.html', {
                'assignments': assignments,
                'stu': stu
            })
    except KeyError:
        return redirect('nouapp:login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def submit_assignment(request, assignment_id):
    """Submit assignment"""
    try:
        if request.session['rollno'] is not None:
            rollno = request.session['rollno']
            stu = Student.objects.get(rollno=rollno)
            assignment = get_object_or_404(Assignment, id=assignment_id)

            # Check if already submitted
            existing_submission = Submission.objects.filter(assignment=assignment, student=stu).first()
            if existing_submission:
                messages.warning(request, 'You have already submitted this assignment.')
                return redirect('studentapp:view_submission_status', assignment_id=assignment_id)

            if request.method == 'POST':
                form = SubmissionForm(request.POST, request.FILES)
                if form.is_valid():
                    submission = form.save(commit=False)
                    submission.assignment = assignment
                    submission.student = stu
                    submission.save()
                    messages.success(request, 'Assignment submitted successfully!')
                    return redirect('studentapp:view_submission_status', assignment_id=assignment_id)
            else:
                form = SubmissionForm()

            return render(request, 'studentapp/submit_assignment.html', {
                'form': form,
                'assignment': assignment,
                'stu': stu
            })
    except KeyError:
        return redirect('nouapp:login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_submission_status(request, assignment_id):
    """View submission status"""
    try:
        if request.session['rollno'] is not None:
            rollno = request.session['rollno']
            stu = Student.objects.get(rollno=rollno)
            assignment = get_object_or_404(Assignment, id=assignment_id)
            submission = Submission.objects.filter(assignment=assignment, student=stu).first()
            return render(request, 'studentapp/submission_status.html', {
                'assignment': assignment,
                'submission': submission,
                'stu': stu
            })
    except KeyError:
        return redirect('nouapp:login')
