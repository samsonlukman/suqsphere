from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    profile_pics = models.ImageField(upload_to='profile_pics/', null=True, blank=True)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="post_user")
    postContent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    post_image = models.ImageField(upload_to='post_image/', null=True, blank=True)

    def __str__(self):
        return f"{self.user} {self.postContent} {self.timestamp}"

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userComment")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True, related_name="postComment")
    message = models.CharField(max_length=10000)

    def __str__(self):
        return f"{str(self.author)} commented on {self.post}"

class Follow(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="following_user")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="followed_user")

    def __str__(self):
        return f"{self.following} is following {self.follower}"


class Like(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user_like")
    post = models.ForeignKey(Post,on_delete=models.CASCADE, related_name="post_like")

class Allahu_akbar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userAllah")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postAllah")

class Subhanallah(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userSubhanallah")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postSubhanallah")

class Laa(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userLaa")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postLaa")




    def __str__(self):
        return f"{self.user} liked {self.post}"