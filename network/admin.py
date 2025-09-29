from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(LibraryImage)
admin.site.register(SharePost)
admin.site.register(GroupShare)
admin.site.register(User)
admin.site.register(PostImage)
admin.site.register(Announcement)
admin.site.register(AnnouncementPostImage)
admin.site.register(ForumTopicImage)
admin.site.register(LibraryCategory)
admin.site.register(LibraryDocument)
admin.site.register(Video)
admin.site.register(FavoriteDocument)
admin.site.register(FavoriteVideo)
admin.site.register(GroupPostImage)
admin.site.register(ForumPost)
admin.site.register(ForumTopic)
admin.site.register(Follow)
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'pinned', 'timestamp')
    list_editable = ('pinned',)
admin.site.register(Friend)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Sad)
admin.site.register(Love)
admin.site.register(Haha)
admin.site.register(Shock)
admin.site.register(CommentLike)
admin.site.register(Group)
admin.site.register(GroupPost)
admin.site.register(GroupComment)
admin.site.register(GroupLike)
admin.site.register(GroupSad)
admin.site.register(GroupLove)
admin.site.register(GroupHaha)
admin.site.register(GroupShock)
admin.site.register(Listing)
admin.site.register(Category)
admin.site.register(auctions_Comment)
admin.site.register(Bid)
admin.site.register(Currency)
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

class OrderItemInline(admin.TabularInline):
    """Inline to show order items on the Order admin page."""
    model = OrderItem
    raw_id_fields = ('product',)
    extra = 0
    readonly_fields = ('price_at_purchase',)

# 2. ModelAdmin for Primary Models
# These classes customize the list view and detail view of each model.
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
admin.site.register(MarketImage)
admin.site.register(Review)