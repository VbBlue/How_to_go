from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

# bizinfo에서 크롤링한 사업정보 모델
class Bizinfo(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    title = models.CharField(max_length=200)
    ministry = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    period = models.CharField(max_length=200)
    summary = models.TextField(max_length=2000)
    link1 = models.CharField(max_length=200)
    link2 = models.CharField(max_length=200, null=True, blank=True)
    registration_date = models.DateField(auto_now_add=True)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('info-detail', args=[str(self.id)])

class Bookmark(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    biz_id = models.ForeignKey(Bizinfo, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return Bizinfo.get_absolute_url()