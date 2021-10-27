from django.contrib import admin
from django.contrib.auth.models import Group
from myapp.models import User, Post, Like


class Users(admin.ModelAdmin):
    admin.site.register(User)


admin.site.register(Post)
admin.site.unregister(Group)
admin.site.register(Like)
