from django.db import models
from django.core.validators import FileExtensionValidator

# Create your models here.

class StuResponse(models.Model):
    rollno = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    
    # Use ForeignKeys to match Student model
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)  
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    
    contactno = models.CharField(max_length=10)
    emailaddress = models.CharField(max_length=50)
    responsetype = models.CharField(max_length=20)
    subject = models.CharField(max_length=200)
    responsetext = models.TextField()
    responsedate = models.DateField()
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class Question(models.Model):
    qid = models.AutoField(primary_key=True)
    question = models.TextField()
    postedby = models.CharField(max_length=50)
    posteddate = models.CharField(max_length=30)
    
class Answer(models.Model):
    aid=models.AutoField(primary_key=True)
    answer=models.TextField()
    answered=models.CharField(max_length=50)
    posteddate=models.CharField(max_length=30)
    qid=models.IntegerField()

class Submission(models.Model):
    """Student submission for assignments"""
    assignment = models.ForeignKey('adminapp.Assignment', on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('nouapp.Student', on_delete=models.CASCADE, related_name='submissions')
    submitted_file = models.FileField(
        upload_to='submissions/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=[
            'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'zip', 'rar', 'jpg', 'jpeg', 'png'
        ])],
        blank=True,
        null=True
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ], default='pending')
    grade = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions')

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student.name} - {self.assignment.title}"

    def is_late(self):
        return self.submitted_at > self.assignment.due_date if self.submitted_at else False
    