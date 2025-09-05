from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    profile_pics = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    about = models.TextField(null=True, blank=True)



class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="post_user")
    postContent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user} {self.postContent} {self.timestamp}"

class PostImage(models.Model):
    postContent = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_images")
    post_image = models.ImageField(upload_to='post_image/', null=True, blank=True)

    def __str__(self):
        return f"Image for {self.postContent}"


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userComment")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True, related_name="postComment")
    message = models.CharField(max_length=10000)
    timestamp = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        'self', # Refers to the Comment model itself
        on_delete=models.CASCADE,
        null=True,     # Parent is optional (top-level comments have no parent)
        blank=True,    # Allow null in forms/admin
        related_name='replies' # Use 'replies' to access child comments
    )

    class Meta:
        ordering = ['timestamp']
    

    def __str__(self):
        return f"{str(self.author)} wrote {self.message} on {self.post}"
    
class Follow(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="following_user")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="followed_user")

    def __str__(self):
        return f"{self.following} is following {self.follower}"

# Regular post reactions
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_like")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_like")

    def __str__(self):
        return f"{self.user} likes {self.post}"

class Sad(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userSad")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postSad")

    def __str__(self):
        return f"{self.user} reacts Sad on {self.post}"

class Love(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userLove")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postLove")

    def __str__(self):
        return f"{self.user} reacts Love on {self.post}"

class Haha(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userHaha")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postHaha")

    def __str__(self):
        return f"{self.user} reacts Haha on {self.post}"

class Shock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userShock")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postShock")

    def __str__(self):
        return f"{self.user} reacts Shock on {self.post}"

class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comment_likes")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="comment_likes")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment') # A user can like a comment only once

    def __str__(self):
        return f"{self.user} likes comment {self.comment.id}"
    
# Define the Group model and GroupPost model
class Group(models.Model):
    name = models.CharField(max_length=100)  # Default value for 'name'
    description = models.TextField(blank=True, null=True,)  # Default value for 'description'
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='group_members')

    def __str__(self):
        return f"{self.name}"





class SharePost(models.Model):
    sharer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='shared_posts')
    shared_post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, default=None)
    shared_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.sharer} shared {self.shared_post} to {self.shared_to}"


class GroupShare(models.Model):
    sharer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='group_share')
    shared_post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, default=None)
    shared_to = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, default=None)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.sharer} shared {self.shared_post} to {self.shared_to}"
    
#Group post reactions
class GroupPost(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_posts")
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="group_post_user")
    postContent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    groupshare = models.ForeignKey(GroupShare, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.postContent} by {self.user}"
           
class GroupPostImage(models.Model):
    postContent = models.ForeignKey(GroupPost, on_delete=models.CASCADE, related_name="group_post_images")
    post_image = models.ImageField(upload_to='post_image/', null=True, blank=True)

    def __str__(self):
        return f"Image for {self.postContent}"
    
class GroupComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="group_userComment")
    post = models.ForeignKey(GroupPost, on_delete=models.CASCADE, blank=True, null=True, related_name="group_postComment")
    message = models.CharField(max_length=10000)

    def __str__(self):
        return f"{str(self.author)} commented on {self.post}"
    


class GroupLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_user_like")
    post = models.ForeignKey(GroupPost, on_delete=models.CASCADE, related_name="group_post_like")

    def __str__(self):
        return f"{self.user} likes {self.post}"

class GroupSad(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_userSad")
    post = models.ForeignKey(GroupPost, on_delete=models.CASCADE, related_name="group_postSad")

    def __str__(self):
        return f"{self.user} reacts Sad on {self.post}"

class GroupLove(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_userLove")
    post = models.ForeignKey(GroupPost, on_delete=models.CASCADE, related_name="group_postLove")

    def __str__(self):
        return f"{self.user} reacts Love on {self.post}"

class GroupHaha(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_userHaha")
    post = models.ForeignKey(GroupPost, on_delete=models.CASCADE, related_name="group_postHaha")

    def __str__(self):
        return f"{self.user} reacts Haha on {self.post}"

class GroupShock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_userShock")
    post = models.ForeignKey(GroupPost, on_delete=models.CASCADE, related_name="group_postShock")

    def __str__(self):
        return f"{self.user} reacts Shock on {self.post}"
    

class LibraryCategory(models.Model):
    CATEGORY_CHOICES = [
        ('Science', 'Science'),
        ('IT', 'IT'),
        ('Math', 'Math'),
        ('Skills and Self-growth', 'Skills and Self-growth'),
        ('Agriculture', 'Agriculture'),
        ('Finance', 'Finance'),
        ('Economics', 'Economics'),
        ('Philosophy', 'Philosophy'),
        ('Others', 'Others'),
    ]

    categoryName = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.categoryName

class LibraryImage(models.Model):
    content = models.ForeignKey(LibraryCategory, on_delete=models.CASCADE, related_name='libraryimage_set')
    post_image = models.ImageField(upload_to='post_image/', null=True, blank=True)

    def __str__(self):
        return f"Image for {self.content}"

class LibraryDocument(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(LibraryCategory, on_delete=models.CASCADE, blank=True, null=True)
    file = models.FileField(upload_to='library/documents/')
    views = models.PositiveIntegerField(default=0)
    viewers_ip = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Video(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(LibraryCategory, on_delete=models.CASCADE, blank=True, null=True)
    file = models.FileField(upload_to='library/videos/')
    views = models.PositiveIntegerField(default=0)
    viewers_ip = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    
class FavoriteDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey('LibraryDocument', on_delete=models.CASCADE)

class FavoriteVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey('Video', on_delete=models.CASCADE)



class ForumTopic(models.Model):
    title = models.CharField(max_length=200)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ForumTopicImage(models.Model):
    content = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name="forum_topic_post_images")
    post_image = models.ImageField(upload_to='post_image/', null=True, blank=True)

    def __str__(self):
        return f"Image for {self.content}"

class ForumPost(models.Model):
    content = models.TextField()
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='posts')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.creator.username} in {self.topic.title}"

class Announcement(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="announcement_poster")
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} announced by {self.poster}"
    
class AnnouncementPostImage(models.Model):
    content = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name="announcement_post_images")
    post_image = models.ImageField(upload_to='post_image/', null=True, blank=True)

    def __str__(self):
        return f"Image for {self.content}"


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
    user = models.ForeignKey('User', on_delete=models.CASCADE, blank=True, null=True, related_name="Userbid")


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

class Water(models.Model):
    table = models.IntegerField()

class Product(models.Model):
    # Basic Product Details
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    
    # Financials and Inventory
    price = models.DecimalField(max_digits=10, decimal_places=2) # Changed to 2 decimal places for standard currency
    currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True, related_name="products")
    stock_quantity = models.PositiveIntegerField(default=1)
    
    # Status and Metadata
    is_active = models.BooleanField(default=True) # Renamed for consistency
    is_featured = models.BooleanField(default=False) # Renamed for consistency
    is_sold_out = models.BooleanField(default=False)
    
    # Relationships
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listed_products") # Renamed 'owner' to 'seller'
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name="products")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} by {self.seller.username}"

    def save(self, *args, **kwargs):
        # Automatically update is_sold_out based on stock
        self.is_sold_out = (self.stock_quantity == 0)
        super().save(*args, **kwargs)

class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True, related_name="orders")
    
    # Order Statuses
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Transaction Details
    transaction_id = models.CharField(max_length=200, unique=True, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username}"
    


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name="ordered_items")
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2) # Store the price at time of purchase to prevent issues if seller changes the price later

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"
    

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.title} in cart"
    
class MarketComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="market_comments", default=1)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="comments")
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.author.username} commented on {self.product.title}"
    
class MarketImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='product_images/') # More descriptive upload path
    
    def __str__(self):
        return f"Image for {self.product.title}"

# models.py
class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'author')  # A user can only review a product once

    def __str__(self):
        return f"Review by {self.author.username} for {self.product.title}"