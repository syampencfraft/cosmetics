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
        