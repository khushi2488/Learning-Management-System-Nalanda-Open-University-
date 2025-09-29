from django.db import models
from django.utils import timezone
from datetime import timedelta

class Student(models.Model):
    rollno = models.BigIntegerField(primary_key=True)  # Changed to BigIntegerField for PostgreSQL
    name = models.CharField(max_length=50)
    fname = models.CharField(max_length=50)
    mname = models.CharField(max_length=50)
    gender = models.CharField(max_length=6)
    address = models.TextField()
    program = models.ForeignKey('adminapp.Program', on_delete=models.CASCADE)
    branch = models.ForeignKey('adminapp.Branch', on_delete=models.CASCADE)
    year = models.ForeignKey('adminapp.Year', on_delete=models.CASCADE)
    contactno = models.CharField(max_length=10)
    emailaddress = models.CharField(max_length=50)
    regdate = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.name} ({self.rollno})"

class Login(models.Model):
    userid = models.CharField(max_length=50, primary_key=True)
    password = models.CharField(max_length=30)
    confirmpassword = models.CharField(max_length=30)
    usertype = models.CharField(max_length=50)
    status = models.CharField(max_length=10)

class Enquiry(models.Model):
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=6)
    address = models.TextField()
    contactno = models.CharField(max_length=10)
    emailaddress = models.CharField(max_length=50)
    enquirytext = models.TextField()
    enquirydate = models.CharField(max_length=30)

# For forgot password / reset password token
class PasswordResetToken(models.Model):
    userid = models.CharField(max_length=50)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
        
    def is_expired(self):
        expiry_time = self.created_at + timedelta(hours=1)  # 1 hour expiry
        return timezone.now() > expiry_time
        
    def __str__(self):
        return f"Reset token for {self.userid}"