# Save this as: adminapp/management/commands/setup_initial_data.py
# Run with: python manage.py setup_initial_data

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from adminapp.models import Program, Branch, Year, Course, MaterialCategory

class Command(BaseCommand):
    help = 'Setup initial data for the LMS system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create Programs
        programs = [
            'BTech',
            'MTech', 
            'BCA',
            'MCA',
            'BSc Computer Science',
            'MSc Computer Science'
        ]
        
        for prog_name in programs:
            program, created = Program.objects.get_or_create(program=prog_name)
            if created:
                self.stdout.write(f'Created program: {prog_name}')
        
        # Create Branches
        branches = [
            'Computer Science',
            'Information Technology',
            'Software Engineering',
            'Computer Engineering',
            'Electronics',
            'Mechanical',
            'Civil'
        ]
        
        for branch_name in branches:
            branch, created = Branch.objects.get_or_create(branch=branch_name)
            if created:
                self.stdout.write(f'Created branch: {branch_name}')
        
        # Create Years
        years = [
            'First Year',
            'Second Year', 
            'Third Year',
            'Fourth Year',
            '1',
            '2',
            '3',
            '4'
        ]
        
        for year_name in years:
            year, created = Year.objects.get_or_create(year=year_name)
            if created:
                self.stdout.write(f'Created year: {year_name}')
        
        # Create Material Categories
        categories = [
            {'name': 'Lecture Notes', 'description': 'Class lecture notes', 'icon': 'fas fa-book', 'color_code': '#007bff'},
            {'name': 'Assignments', 'description': 'Homework and assignments', 'icon': 'fas fa-tasks', 'color_code': '#28a745'},
            {'name': 'Lab Materials', 'description': 'Laboratory exercises and guides', 'icon': 'fas fa-flask', 'color_code': '#ffc107'},
            {'name': 'Reference Books', 'description': 'Reference materials and textbooks', 'icon': 'fas fa-book-open', 'color_code': '#dc3545'},
            {'name': 'Previous Papers', 'description': 'Previous year question papers', 'icon': 'fas fa-file-alt', 'color_code': '#6f42c1'},
            {'name': 'Videos', 'description': 'Video lectures and tutorials', 'icon': 'fas fa-video', 'color_code': '#fd7e14'},
            {'name': 'Presentations', 'description': 'PowerPoint presentations', 'icon': 'fas fa-presentation', 'color_code': '#20c997'}
        ]
        
        for cat_data in categories:
            category, created = MaterialCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {cat_data["name"]}')
        
        # Create some sample courses
        try:
            # Get some objects to create sample courses
            btech_prog = Program.objects.get(program='BTech')
            cs_branch = Branch.objects.get(branch='Computer Science')
            first_year = Year.objects.get(year='First Year')
            
            sample_courses = [
                'Programming Fundamentals',
                'Data Structures',
                'Computer Networks',
                'Database Management Systems',
                'Operating Systems',
                'Software Engineering'
            ]
            
            for course_title in sample_courses:
                course, created = Course.objects.get_or_create(
                    title=course_title,
                    program=btech_prog,
                    branch=cs_branch,
                    year=first_year,
                    defaults={
                        'description': f'Course on {course_title}',
                        'course_code': course_title.replace(' ', '').upper()[:6],
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f'Created course: {course_title}')
                    
        except (Program.DoesNotExist, Branch.DoesNotExist, Year.DoesNotExist):
            self.stdout.write('Could not create sample courses - required objects not found')
        
        # Create admin user if not exists
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write('Created admin user: admin/admin123')
        
        self.stdout.write(self.style.SUCCESS('Initial data setup completed!'))
        self.stdout.write('You can now:')
        self.stdout.write('1. Log in as admin (username: admin, password: admin123)')
        self.stdout.write('2. Upload study materials')
        self.stdout.write('3. Students can view materials based on their program/branch/year')