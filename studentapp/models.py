from django.db import models
from django.core.validators import FileExtensionValidator

# Create your models here.

class StuResponse(models.Model):
    rollno=models.IntegerField()
    name=models.CharField(max_length=50)
    program=models.CharField(max_length=50)
    branch=models.CharField(max_length=50)
    year=models.CharField(max_length=50)
    contactno=models.CharField(max_length=10)
    emailaddress=models.CharField(max_length=50)
    responsetype=models.CharField(max_length=50)
    subject=models.CharField(max_length=500)
    responsetext=models.CharField(max_length=1000)
    responsedate=models.CharField(max_length=30)

class Question(models.Model):
    qid=models.AutoField(primary_key=True)
    question=models.TextField()
    postedby=models.CharField(max_length=50)
    posteddate=models.CharField(max_length=30)
    
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
    