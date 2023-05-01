from django.contrib import admin
from .models import Post, User, Follow, Like, Comment, Subscription

# Register your models here.
admin.site.register(Post)
admin.site.register(User)
admin.site.register(Follow)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Subscription)

