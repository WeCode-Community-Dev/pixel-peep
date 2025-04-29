from django.db import models

# Create your models here.

class OriginalImageModel(models.Model):
    id = models.AutoField(primary_key= True)
    image_uploaded = models.ImageField(upload_to= 'original_images')



