class Nylon(models.Model):
    nylon = models.CharField(max_length=100)

    def __str__(self):
        return self.nylon

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



class MarketImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='product_images/') # More descriptive upload path
    
    def __str__(self):
        return f"Image for {self.product.title}"

class MarketComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="market_comments", default=1)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="comments")
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.author.username} commented on {self.product.title}"


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
    
class Gas(models.Model):
    hulk = models.CharField(max_length=100)




admin.site.register(Nylon)

class OrderItemInline(admin.TabularInline):
    """Inline to show order items on the Order admin page."""
    model = OrderItem
    raw_id_fields = ('product',)
    extra = 0
    readonly_fields = ('price_at_purchase',)

# 2. ModelAdmin for Primary Models
# These classes customize the list view and detail view of each model.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'seller',
        'price',
        'currency',
        'category',
        'is_active',
        'is_sold_out',
        'stock_quantity',
    )
    list_filter = ('is_active', 'is_featured', 'category', 'currency')
    search_fields = ('title', 'description', 'seller__username')
    prepopulated_fields = {'title': ('description',)}
    readonly_fields = ('is_sold_out',)
    fieldsets = (
        ('Product Information', {
            'fields': ('title', 'description', 'price', 'currency', 'category', 'stock_quantity')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'is_sold_out')
        }),
        ('Ownership', {
            'fields': ('seller',)
        }),
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at', 'order_currency')
    search_fields = ('buyer__username', 'transaction_id')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Order Details', {
            'fields': ('buyer', 'status', 'total_amount', 'order_currency', 'transaction_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)

admin.site.register(CartItem)
# 3. Registering the remaining simple models
admin.site.register(MarketComment)
admin.site.register(Jags)