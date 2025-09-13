# adminapp/analytics_utils.py - Fixed version

from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from nouapp.models import Student
from studentapp.models import StuResponse, Question, Answer
from .models import Material, News, StudentActivity, DailyStats, ProgramStats, BranchStats, Course

def log_student_activity(rollno, activity_type, request=None, additional_info=''):
    """Log student activity using rollno (compatible with your session system)"""
    try:
        # Get student info
        student = Student.objects.get(rollno=rollno)
        
        # Create activity log
        activity = StudentActivity.objects.create(
            rollno=rollno,
            student_name=student.name,
            program=student.program,
            branch=student.branch,
            year=student.year,
            activity_type=activity_type,
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            additional_info=additional_info
        )
        return activity
    except Student.DoesNotExist:
        print(f"Student with rollno {rollno} not found")
        return None

def get_enrollment_analytics(days=30):
    """Get enrollment data based on your existing Student model"""
    
    # Get enrollment by program
    enrollment_by_program = Student.objects.values('program').annotate(
        count=Count('rollno')
    ).order_by('-count')
    
    # Get enrollment by branch  
    enrollment_by_branch = Student.objects.values('branch').annotate(
        count=Count('rollno')
    ).order_by('-count')
    
    # Get enrollment by year
    enrollment_by_year = Student.objects.values('year').annotate(
        count=Count('rollno')
    ).order_by('-count')
    
    # Get daily login activity
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    daily_logins = []
    current_date = start_date
    
    while current_date <= end_date:
        login_count = StudentActivity.objects.filter(
            activity_date__date=current_date,
            activity_type='login'
        ).count()
        
        unique_students = StudentActivity.objects.filter(
            activity_date__date=current_date,
            activity_type='login'
        ).values('rollno').distinct().count()
        
        daily_logins.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'logins': login_count,
            'unique_students': unique_students
        })
        current_date += timedelta(days=1)
    
    return {
        'enrollment_by_program': list(enrollment_by_program),
        'enrollment_by_branch': list(enrollment_by_branch),
        'enrollment_by_year': list(enrollment_by_year),
        'daily_logins': daily_logins,
        'total_students': Student.objects.count()
    }

def get_material_analytics(days=30):
    """Get material usage analytics"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Daily material activity
    daily_activity = []
    current_date = start_date
    
    while current_date <= end_date:
        views = StudentActivity.objects.filter(
            activity_date__date=current_date,
            activity_type='material_view'
        ).count()
        
        downloads = StudentActivity.objects.filter(
            activity_date__date=current_date,
            activity_type='material_download'
        ).count()
        
        uploads = Material.objects.filter(
            created_at__date=current_date
        ).count()
        
        daily_activity.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'views': views,
            'downloads': downloads,
            'uploads': uploads,
            'count': downloads  # For compatibility with template
        })
        current_date += timedelta(days=1)
    
    # Most accessed materials (based on activity logs)
    popular_materials = StudentActivity.objects.filter(
        activity_type='material_download',
        activity_date__date__gte=start_date
    ).extra(
        select={'material_title': 'additional_info'}
    ).values('additional_info').annotate(
        download_count=Count('id')
    ).order_by('-download_count')[:10]
    
    return {
        'daily_activity': daily_activity,
        'popular_materials': list(popular_materials),
        'total_materials': Material.objects.count()
    }

def get_student_engagement_analytics():
    """Get student engagement metrics based on your existing models"""
    
    # Get feedback/complaint statistics
    feedback_by_program = StuResponse.objects.filter(
        responsetype='feedback'
    ).values('program').annotate(
        count=Count('id')
    ).order_by('-count')
    
    complaints_by_program = StuResponse.objects.filter(
        responsetype='complain'
    ).values('program').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Q&A Statistics from activity logs
    question_activities = StudentActivity.objects.filter(
        activity_type='question_post'
    ).values('program').annotate(
        count=Count('id')
    ).order_by('-count')
    
    answer_activities = StudentActivity.objects.filter(
        activity_type='answer_post'  
    ).values('program').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Most active students
    most_active_students = StudentActivity.objects.values(
        'rollno', 'student_name', 'program', 'branch'
    ).annotate(
        activity_count=Count('id')
    ).order_by('-activity_count')[:20]
    
    return {
        'feedback_by_program': list(feedback_by_program),
        'complaints_by_program': list(complaints_by_program),
        'questions_by_program': list(question_activities),
        'answers_by_program': list(answer_activities),
        'most_active_students': list(most_active_students),
        'total_feedback': StuResponse.objects.filter(responsetype='feedback').count(),
        'total_complaints': StuResponse.objects.filter(responsetype='complain').count(),
        'total_questions': Question.objects.count(),
        'total_answers': Answer.objects.count()
    }

def get_dashboard_summary():
    """Get dashboard summary compatible with your system - FIXED"""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Today's statistics
    today_logins = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='login'
    ).count()
    
    today_unique_students = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='login'
    ).values('rollno').distinct().count()
    
    today_downloads = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='material_download'
    ).count()
    
    today_views = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='material_view'
    ).count()
    
    # Yesterday's statistics for comparison
    yesterday_logins = StudentActivity.objects.filter(
        activity_date__date=yesterday,
        activity_type='login'
    ).count()
    
    yesterday_downloads = StudentActivity.objects.filter(
        activity_date__date=yesterday,
        activity_type='material_download'
    ).count()
    
    # Week's unique students
    week_start = today - timedelta(days=7)
    week_unique_students = StudentActivity.objects.filter(
        activity_date__date__gte=week_start,
        activity_type='login'
    ).values('rollno').distinct().count()
    
    # Calculate percentage changes
    login_change = 0
    if yesterday_logins > 0:
        login_change = ((today_logins - yesterday_logins) / yesterday_logins) * 100
    
    download_change = 0
    if yesterday_downloads > 0:
        download_change = ((today_downloads - yesterday_downloads) / yesterday_downloads) * 100
    
    return {
        'total_students': Student.objects.count(),
        'total_materials': Material.objects.count(),
        'total_courses': Course.objects.count(),  # ADDED THIS
        'total_news': News.objects.count(),
        'today_logins': today_logins,
        'today_unique_students': today_unique_students,
        'week_unique_students': week_unique_students,  # ADDED THIS
        'today_downloads': today_downloads,
        'today_views': today_views,
        'login_change': round(login_change, 1),
        'download_change': round(download_change, 1),
    }

def update_daily_stats():
    """Update daily statistics - can be run via cron job"""
    today = timezone.now().date()
    
    # Get or create today's stats
    stats, created = DailyStats.objects.get_or_create(date=today)
    
    # Update counts
    stats.total_students = Student.objects.count()
    stats.students_logged_in = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='login'
    ).values('rollno').distinct().count()
    
    stats.total_logins = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='login'
    ).count()
    
    stats.material_views = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='material_view'
    ).count()
    
    stats.material_downloads = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='material_download'
    ).count()
    
    stats.questions_posted = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='question_post'
    ).count()
    
    stats.answers_posted = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='answer_post'
    ).count()
    
    stats.feedback_submitted = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='feedback_submit'
    ).count()
    
    stats.complaints_submitted = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='complaint_submit'
    ).count()
    
    stats.materials_uploaded = Material.objects.filter(
        created_at__date=today
    ).count()
    
    stats.save()
    return stats