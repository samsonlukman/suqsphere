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
    pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-pinned', '-timestamp']
    

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


"""This is like a repitition of the Follow model above but I wanted to simplify
this for messages"""
class Friend(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    
    class Meta:
        unique_together = ('follower', 'following')

# This model represents a one-on-one chat
class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} | {self.conversation} | {self.timestamp}"

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
    currencyName = models.CharField(max_length=50, default="NGN")

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

# --- Nigerian States Choices ---
NIGERIAN_STATES = [
    ('ABIA', 'Abia'),
    ('ADAMAWA', 'Adamawa'),
    ('AKWA IBOM', 'Akwa Ibom'),
    ('ANAMBRA', 'Anambra'),
    ('BAUCHI', 'Bauchi'),
    ('BAYELSA', 'Bayelsa'),
    ('BENUE', 'Benue'),
    ('BORNO', 'Borno'),
    ('CROSS RIVER', 'Cross River'),
    ('DELTA', 'Delta'),
    ('EBONYI', 'Ebonyi'),
    ('EDO', 'Edo'),
    ('EKITI', 'Ekiti'),
    ('ENUGU', 'Enugu'),
    ('FCT', 'F.C.T. Abuja'),
    ('GOMBE', 'Gombe'),
    ('IMO', 'Imo'),
    ('JIGAWA', 'Jigawa'),
    ('KADUNA', 'Kaduna'),
    ('KANO', 'Kano'),
    ('KATSINA', 'Katsina'),
    ('KEBBI', 'Kebbi'),
    ('KOGI', 'Kogi'),
    ('KWARA', 'Kwara'),
    ('LAGOS', 'Lagos'),
    ('NASARAWA', 'Nasarawa'),
    ('NIGER', 'Niger'),
    ('OGUN', 'Ogun'),
    ('ONDO', 'Ondo'),
    ('OSUN', 'Osun'),
    ('OYO', 'Oyo'),
    ('PLATEAU', 'Plateau'),
    ('RIVERS', 'Rivers'),
    ('SOKOTO', 'Sokoto'),
    ('TARABA', 'Taraba'),
    ('YOBE', 'Yobe'),
    ('ZAMFARA', 'Zamfara'),
]


class Product(models.Model):
    # Basic Product Details
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    
    # --- NEW FIELD FOR STATE LOCATION ---
    state = models.CharField(
        max_length=50,
        choices=NIGERIAN_STATES,
        default='LAGOS',  
        help_text="The Nigerian state where the product is located."
    )
    
    # Financials and Inventory
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True, related_name="products")
    stock_quantity = models.PositiveIntegerField(default=1)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=2)
    
    # Status and Metadata
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_sold_out = models.BooleanField(default=False)
    
    # Relationships
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listed_products")
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name="products")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} by {self.seller.username} ({self.get_state_display()})"

    def save(self, *args, **kwargs):
        # Automatically update is_sold_out based on stock
        # NOTE: Keeping the is_sold_out logic as requested by user in the history.
        self.is_sold_out = (self.stock_quantity == 0)
        super().save(*args, **kwargs)

# Order Statuses
STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Processing', 'Processing'),
    ('Paid', 'Paid'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
]


class ManualDelivery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manual_deliveries')
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='manual_delivery', null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    total_items = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Update In Orders')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto-update order status to match manual delivery status
        if self.order and self.status != self.order.status:
            self.order.status = self.status
            self.order.save(update_fields=['status'])

    def __str__(self):
        return f"Order by {self.user.username} on {self.created_at}: {self.reference}"

class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True, related_name="orders", default=18)

    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    delivery_type = models.CharField(max_length=50, default='manual')  # e.g., Standard, Express

    # Payment / Transaction details
    transaction_id = models.CharField(max_length=200, unique=True, blank=True, null=True)  # Flutterwave tx_ref
    flutterwave_tx_ref = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Successful', 'Successful'),
            ('Failed', 'Failed'),
        ],
        default='Pending',
    )

    # Delivery details
    kwik_delivery_id = models.CharField(max_length=255, blank=True, null=True)
    delivery_status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('PickedUp', 'Picked Up'),
            ('InTransit', 'In Transit'),
            ('Delivered', 'Delivered'),
        ],
        default='Pending',
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username if self.buyer else 'Unknown'}: {self.buyer.phone_number}, {self.buyer.email}"


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name="ordered_items")
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="order_sales")  # 🧩 NEW FIELD
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)  # locked price

    def subtotal(self):
        return self.quantity * self.price_at_purchase

    def __str__(self):
        return f"{self.quantity} x {self.product.title if self.product else 'Deleted Product'}"


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

class CompletedPurchase(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="purchases")
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="completed_sales")
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name="completed_purchases")
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    PAYMENT_METHODS = [
        ('wallet', 'Wallet'),
        ('card', 'Card'),
        ('ussd', 'USSD'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='wallet')

    STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Refunded', 'Refunded'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Completed')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} - {self.buyer.username} → {self.seller.username}"

    
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


class DeviceToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.CharField(max_length=255, unique=True)  # One token per device
    device_name = models.CharField(max_length=100, blank=True, null=True)  # Optional
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.token[:20]}"
    
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('follow', 'Follow'),
        ('reaction', 'Reaction'),
        ('comment', 'Comment'),
        ('purchase', 'Purchase'),
        ('message', 'Message'),
        ('post', 'Post'),
        ('system', 'System'),
        ('ai_daily', 'AI Daily'),
        ('daily_market_update', 'Daily Market Update'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)  # Optional link to open on click
    metadata = models.JSONField(default=dict, blank=True)  # can store {"post_id": 12} or {"order_id": 3}
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} -> {self.recipient}"
