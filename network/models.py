from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    profile_pics = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    about = models.TextField(null=True, blank=True)



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

    def __str__(self):
        return f"{self.user} likes {self.post}"

class Allahu_akbar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userAllah")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postAllah")

    def __str__(self):
        return f"{self.user} reacts Allah akbar on {self.post}"

class MaaShaaAllah(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userMaashaa")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postMaashaa")

    def __str__(self):
        return f"{self.user} loves {self.post}"

class Haha(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userHaha")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postHaha")

    def __str__(self):
        return f"{self.user} haha'd {self.post}"

class Subhanallah(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userSubhanallah")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postSubhanallah")

    def __str__(self):
        return f"{self.user} is shocked at {self.post}"

class Laa(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userLaa")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postLaa")

    def __str__(self):
        return f"{self.user} dislikes {self.post}"


class Category(models.Model):
    # CharField to store the name of the category
    # with a max length of 50 characters
    categoryName = models.CharField(max_length=50)

    def __str__(self):
        # Returns the category name when the object is printed
        return self.categoryName

class Currency(models.Model):
    # CharField to store the name of the category
    # with a max length of 50 characters
    currencyName = models.CharField(max_length=50)

    def __str__(self):
        # Returns the category name when the object is printed
        return self.currencyName

# This class defines a Bid model with a single FloatField
# to store the bid amount
class Bid(models.Model):
    # FloatField to store the bid amount
    # with a default value of 0
    bid = models.FloatField(default=0)
    # ForeignKey to a User object, with the option to delete the object
    # if the user is deleted
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="Userbid")


# This class defines a Listing model with several fields:
# - CharField for the listing title (max length of 100 characters)
# - CharField for the listing description (max length of 1000 characters)
# - CharField for the listing image URL (max length of 200 characters)
# - ForeignKey to a Bid object to store the price of the listing
# - BooleanField to store whether the listing is active or not
# - ForeignKey to a User object to store the owner of the listing
# - ForeignKey to a Category object to store the category of the listing
# - ManyToManyField to a User object to store the users who have added the listing to their watchlist
class Listing(models.Model):
    # CharField to store the listing title
    # with a max length of 100 characters
    title = models.CharField(max_length=100)
    transaction_reference = models.CharField(max_length=100, default="aa")
    # CharField to store the listing description
    # with a max length of 1000 characters
    description = models.CharField(max_length=1000)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, blank=True, null=True, related_name="currency")
    # CharField to store the URL of the listing's image
    # with a max length of 200 characters
    image = models.ImageField(blank=True, null=True, upload_to='images/')
    # ForeignKey to a Bid object to store the price of the listing
    # with the option to delete the object if the bid is deleted
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="bidPrice")
    # BooleanField to store whether the listing is active or not
    # with a default value of True
    isActive = models.BooleanField(default=True)
    # ForeignKey to a User object to store the owner of the listing
    # with the option to delete the object if the user is deleted
    completed = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    # ForeignKey to a Category object to store the category of the listing
    # with the option to delete the object if the category is deleted
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    # ManyToManyField to a User object to store the users who have added the listing to their watchlist
    watchlist = models.ManyToManyField(User, blank=True, related_name="listingWatchlist")

    def __str__(self):
        # Returns the title of the listing when the object is printed
        return f"{self.title}, {self.currency}{self.price}"

# This class defines a Comment model with three fields:
# - ForeignKey to a User object to store the author of the comment
# - ForeignKey to a Listing object to store the listing that the comment is for
# - CharField to store the message of the comment (max length of 500 characters)
class auctions_Comment(models.Model):
    # ForeignKey to a User object to store the author of the comment
    # with the option to delete the object if the user is deleted
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="auctions_userComment")
    # ForeignKey to a Listing object to store the listing that the comment is for
    # with the option to delete the object if the listing is deleted
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listingComment")
    # CharField to store the message of the comment
    # with a max length of 500 characters
    message = models.CharField(max_length=500)

    def __str__(self):
        # Returns a string representation of the comment in the form:
        # "{author} commented on {listing}"
        f"{self.author} commented on {self.listing}"


