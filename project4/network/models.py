from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="post_user")
    postContent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user} {self.postContent} {self.timestamp}"

class Follow(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="following_user")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="followed_user")

    def __str__(self):
        return f"{self.following} is following {self.follower}"


class Like(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user_like")
    post = models.ForeignKey(Post,on_delete=models.CASCADE, related_name="post_like")
    
    
    def __str__(self):
        return f"{self.user} liked {self.post}"