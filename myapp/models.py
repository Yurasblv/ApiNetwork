from django.db import models
from django.contrib.auth.models import AbstractUser
from myapp import managers
from datetime import datetime, timedelta
from djangoProject1 import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    email = None
    last_login = models.DateTimeField(default=timezone.now)

    REQUIRED_FIELDS = []

    objects = managers.UserManager()

    def __str__(self):
        return self.username


class Post(models.Model):
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    post = models.TextField()



class Like(models.Model):
    like_created = models.DateTimeField(_('like date'), default=timezone.now)
    like_user = models.ForeignKey(User, on_delete=models.CASCADE)
    like_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    like = models.SmallIntegerField(default=0)

    def __str__(self):
        return f"Likes:{self.like}, User:{self.like_user}, Post:{self.like_post} ,Date: {self.like_created}, PK --- {self.pk}"

