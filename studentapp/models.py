from django.db import models

# Create your models here.
from adminapp.models import Program, Branch, Year

class StuResponse(models.Model):
    rollno = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    
    # UPDATED: Use ForeignKeys to match Student model
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
    