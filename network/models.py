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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_like")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_like")

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
    categoryName = models.CharField(max_length=50)

    def __str__(self):
        return self.categoryName


class Currency(models.Model):
    currencyName = models.CharField(max_length=50)

    def __str__(self):
        return self.currencyName


class Bid(models.Model):
    bid = models.FloatField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="Userbid")


class Listing(models.Model):
    title = models.CharField(max_length=100)
    transaction_reference = models.CharField(max_length=100, default="aa")
    description = models.CharField(max_length=1000)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, blank=True, null=True, related_name="currency")
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="bidPrice")
    isActive = models.BooleanField(default=True)
    completed = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    watchlist = models.ManyToManyField(User, blank=True, related_name="listingWatchlist")

    def __str__(self):
        return f"{self.title}, {self.currency}{self.price}"


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return f"Image for {self.listing.title}"


class auctions_Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="auctions_userComment")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listingComment")
    message = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.author} commented on {self.listing}"


# Database for Market 

class MarketCurrency(models.Model):
    currencyName = models.CharField(max_length=50)

    def __str__(self):
        return self.currencyName
    
class MarketCategory(models.Model):
    categoryName = models.CharField(max_length=50)

    def __str__(self):
        return self.categoryName

class Market(models.Model):
    title = models.CharField(max_length=100)
    transaction_reference = models.CharField(max_length=100, default="aa")
    description = models.CharField(max_length=1000)
    currency = models.ForeignKey(MarketCurrency, on_delete=models.CASCADE, blank=True, null=True, related_name="market_currency")
    price = models.DecimalField(max_digits=10, decimal_places=5)
    isActive = models.BooleanField(default=True)
    isFeatured = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="market_user")
    category = models.ForeignKey(MarketCategory, on_delete=models.CASCADE, blank=True, null=True, related_name="market_category")
    cart = models.ManyToManyField(User, blank=True, related_name="cart")

    def __str__(self):
        return f"{self.title}, {self.currency}{self.price}"


class MarketImage(models.Model):
    item = models.ForeignKey(Market, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return f"Image for {self.item.title}"


class MarketComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="market_userComment")
    item = models.ForeignKey(Market, on_delete=models.CASCADE, blank=True, null=True, related_name="marketComment")
    message = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.author} commented on {self.item}"




