from django.db import models
from io import BytesIO
from PIL import Image
from django.core.files import File

from main.models import User


# Create your models here.

class Blog(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)
    image =  models.ImageField(upload_to="blog-images")
    thumbnail = models.ImageField(upload_to="blog-images/thumbnail", blank=True, null=True)
    summary = models.TextField(default="blog summary", max_length=100)
    details = models.TextField(max_length=5000)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_image(self):
        if self.image:
            return "http://127.0.0.1:8000" + self.image.url
        return ""

    def get_thumbnail(self):
        if self.thumbnail:
            return "http://127.0.0.1:8000" + self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()

                return "http://127.0.0.1:8000" + self.thumbnail.url
            else:
                return ""

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert("RGB")
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, "JPEG", quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail

class FeedBack(models.Model):
    comment = models.CharField(max_length=400)
    rating = models.DecimalField(blank=True, max_digits=5, decimal_places=2, null=True)
    Blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comment')
    date_added = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  

    def __str__(self):
        return self.user  