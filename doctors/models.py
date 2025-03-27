from django.db import models
from accounts.models import User
# Create your models here.

class DoctorReg(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=15, unique=True)
    image = models.FileField(upload_to='docprofile')

    def __str__(self):
        return self.user.username
        
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=255)
    description = models.TextField()
    profile_image = models.ImageField(upload_to='doctor_profiles/')

class ProductRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    product_href = models.URLField()
    notable_effects = models.TextField()
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)

    message = models.TextField(blank=True, null=True) 
    image = models.ImageField(upload_to='recommendation_images/', blank=True, null=True) 

    status_choices = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')

    def __str__(self):
        return f"{self.product_name} - {self.status}"