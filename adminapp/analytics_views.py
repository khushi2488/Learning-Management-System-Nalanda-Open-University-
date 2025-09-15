# adminapp/analytics_views.py - Fixed version

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.cache import cache_control
from django.utils import timezone
from datetime import timedelta
from .analytics_utils import (
    get_enrollment_analytics,
    get_material_analytics, 
    get_student_engagement_analytics,
    get_dashboard_summary
)
from .models import StudentActivity, DailyStats

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    """Main analytics dashboard - compatible with your admin session system"""
    try:
        if request.session['adminid'] is not None:
            adminid = request.session['adminid']
            
            # Get dashboard summary data
            summary = get_dashboard_summary()
            
            return render(request, 'admin_dashboard.html', {
                'adminid': adminid,
                'summary': summary
            })
    except KeyError:
        return redirect('nouapp:login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True) 
def analytics_data(request):
    """API endpoint for chart data - FIXED to use StudentActivity for all charts"""
    try:
        if request.session['adminid'] is not None:
            data_type = request.GET.get('type', 'enrollment')
            days = int(request.GET.get('days', 30))
            
            if data_type == 'enrollment':
                data = get_enrollment_analytics(days=days)
            elif data_type == 'materials':
                data = get_material_analytics(days=days)
            elif data_type == 'engagement':
                data = get_student_engagement_analytics()
            elif data_type == 'daily_activity':
                # FIXED: Use StudentActivity instead of DailyStats
                end_date = timezone.now().date()
                start_date = end_date - timedelta(days=days)
                
                daily_activity = []
                current_date = start_date
                
                while current_date <= end_date:
                    logins = StudentActivity.objects.filter(
                        activity_date__date=current_date,
                        activity_type='login'
                    ).count()
                    
                    material_views = StudentActivity.objects.filter(
                        activity_date__date=current_date,
                        activity_type='material_view'
                    ).count()
                    
                    downloads = StudentActivity.objects.filter(
                        activity_date__date=current_date,
                        activity_type='material_download'
                    ).count()
                    
                    daily_activity.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'logins': logins,
                        'material_views': material_views,
                        'downloads': downloads
                    })
                    current_date += timedelta(days=1)
                
                data = daily_activity
            elif data_type == 'course_activity':
                # Get course/material activity data
                material_data = get_material_analytics(days=days)
                data = {
                    'download_activity': material_data['daily_activity'],
                    'view_activity': material_data['daily_activity']  # Same data for now
                }
            else:
                data = {'error': 'Invalid data type'}
            
            return JsonResponse(data, safe=False)
    except KeyError:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Debug view to check what's in the database
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def debug_analytics(request):
    """Debug view to check analytics data"""
    try:
        if request.session['adminid'] is not None:
            today = timezone.now().date()
            
            # Check recent activities
            recent_activities = StudentActivity.objects.order_by('-activity_date')[:20]
            
            # Count by activity type
            activity_counts = {}
            for activity_type in ['login', 'material_view', 'material_download', 'question_post', 'answer_post']:
                count = StudentActivity.objects.filter(activity_type=activity_type).count()
                activity_counts[activity_type] = count
            
            # Check today's activities
            today_activities = {}
            for activity_type in ['login', 'material_view', 'material_download']:
                count = StudentActivity.objects.filter(
                    activity_date__date=today,
                    activity_type=activity_type
                ).count()
                today_activities[activity_type] = count
            
            context = {
                'recent_activities': recent_activities,
                'activity_counts': activity_counts,
                'today_activities': today_activities,
                'today_date': today
            }
            
            return render(request, 'debug_analytics.html', context)
    except KeyError:
        return redirect('nouapp:login')

# Additional view functions referenced in URLs
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def enrollment_analytics_view(request):
    """Dedicated enrollment analytics view"""
    try:
        if request.session['adminid'] is not None:
            enrollment_data = get_enrollment_analytics()
            return render(request, 'enrollment_analytics.html', {
                'enrollment_data': enrollment_data
            })
    except KeyError:
        return redirect('nouapp:login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def course_analytics_view(request):
    """Dedicated course analytics view"""
    try:
        if request.session['adminid'] is not None:
            course_data = get_material_analytics()
            return render(request, 'course_analytics.html', {
                'course_data': course_data
            })
    except KeyError:
        return redirect('nouapp:login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def performance_analytics_view(request):
    """Dedicated performance analytics view"""
    try:
        if request.session['adminid'] is not None:
            performance_data = get_student_engagement_analytics()
            return render(request, 'performance_analytics.html', {
                'performance_data': performance_data
            })
    except KeyError:
        return redirect('nouapp:login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def real_time_analytics(request):
    """Real-time analytics endpoint"""
    try:
        if request.session['adminid'] is not None:
            today = timezone.now().date()
            
            # Get real-time stats
            real_time_data = {
                'active_students_today': StudentActivity.objects.filter(
                    activity_date__date=today,
                    activity_type='login'
                ).values('rollno').distinct().count(),
                
                'total_logins_today': StudentActivity.objects.filter(
                    activity_date__date=today,
                    activity_type='login'
                ).count(),
                
                'material_downloads_today': StudentActivity.objects.filter(
                    activity_date__date=today,
                    activity_type='material_download'
                ).count(),
                
                'recent_activities': list(
                    StudentActivity.objects.filter(
                        activity_date__date=today
                    ).order_by('-activity_date')[:10].values(
                        'student_name', 'activity_type', 'activity_date', 'additional_info'
                    )
                )
            }
            
            return JsonResponse(real_time_data, safe=False)
    except KeyError:
        return JsonResponse({'error': 'Unauthorized'}, status=401)