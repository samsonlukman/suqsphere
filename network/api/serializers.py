from rest_framework import serializers
from network.models import *
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    profile_pics = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'profile_pics', 'about', 'phone_number',]

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        # This points back to the serializer that holds this field
        # allowing it to recursively serialize child comments
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer()
    following = UserSerializer()

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following']

#For messages
class FriendsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_pics']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'messages']

class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'members']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), write_only=True)
    likes_count = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()
    replies = RecursiveField(many=True, read_only=True) 

    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'message', 'timestamp', 'parent', 'likes_count', 'liked_by_me', 'replies']
        read_only_fields = ['timestamp', 'likes_count', 'liked_by_me', 'replies']
        extra_kwargs = {
            'parent': {'required': False, 'allow_null': True}
        }

    def get_likes_count(self, obj):
        return obj.comment_likes.count()

    def get_liked_by_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.comment_likes.filter(user=request.user).exists()
        return False


class PostImageSerializer(serializers.ModelSerializer):
    post_image = serializers.SerializerMethodField()

    class Meta:
        model = PostImage
        fields = ['id', 'post_image']

    def get_post_image(self, obj):
        return obj.post_image.url


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    post_images = PostImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True, source='postComment')
    total_likes = serializers.SerializerMethodField()
    total_sads = serializers.SerializerMethodField()
    total_loves = serializers.SerializerMethodField()
    total_hahas = serializers.SerializerMethodField()
    total_shocks = serializers.SerializerMethodField()
    total_reactions = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'user', 'postContent', 'timestamp', 'post_images',
            'comments', 'total_likes', 'total_sads', 'total_loves',
            'total_hahas', 'total_shocks', 'total_reactions', 'total_comments',
            
        ]

    def get_total_likes(self, obj):
        return obj.post_like.count()

    def get_total_sads(self, obj):
        return obj.postSad.count()

    def get_total_loves(self, obj):
        return obj.postLove.count()

    def get_total_hahas(self, obj):
        return obj.postHaha.count()

    def get_total_shocks(self, obj):
        return obj.postShock.count()

    def get_total_reactions(self, obj):
        return (
            obj.post_like.count() +
            obj.postSad.count() +
            obj.postLove.count() +
            obj.postHaha.count() +
            obj.postShock.count()
        )

    def get_total_comments(self, obj):
        return obj.postComment.count()



class SocialMediaSearchSerializer(serializers.Serializer):
    """
    Serializer to combine search results from multiple models (Users and Posts).
    """
    # Use your existing serializers to handle the detailed data structure
    users = UserSerializer(many=True, read_only=True)
    posts = PostSerializer(many=True, read_only=True)
    
    # Optional: include a count of results
    total_user_results = serializers.IntegerField(read_only=True)
    total_post_results = serializers.IntegerField(read_only=True)

class EditProfileSerializer(serializers.ModelSerializer):
    # Ensure profile_pics is handled correctly for file uploads
    profile_pics = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'profile_pics', 'about']
        
        extra_kwargs = {
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': False, 'allow_blank': True}, # <-- ADD allow_blank=True
            'phone_number': {'required': False},
            'about': {'required': False},
        }
        
    # FIX 1: Add the allow_blank=True to the email field explicitly to allow empty strings.
    # We rely on the model itself to enforce whether the field can truly be blank.
    # Since you didn't provide the model, we assume email can be blank/null.
    # If the model requires an email, this will not fully solve the issue, but it's the DRF fix.
    
    # FIX 2: Refined uniqueness check
    def validate_email(self, value):
        user = self.context['request'].user
        
        # 1. If the email field is sent as an empty string, don't run uniqueness check.
        #    (The field will default to the model's behavior: blank or not.)
        if not value:
            # If your User model requires email (null=False, blank=False), Django will throw a non-field error later.
            return value 
            
        # 2. Check if the email being validated is the same as the current user's email
        #    (This covers when the user sends their existing email without changing it)
        if self.instance and self.instance.email == value:
            return value 
            
        # 3. If the email is new, proceed with the uniqueness check
        if User.objects.exclude(pk=user.pk).filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already in use by another user.")
            
        return value

    # Keep the refined username validation logic from the previous fix:
    def validate_username(self, value):
        user = self.context['request'].user
        if self.instance and self.instance.username == value:
            return value
        if User.objects.exclude(pk=user.pk).filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'password', 'profile_pics']
        

    def validate(self, data):
        password = data.get('password')
        try:
            # Use Django's password validation to ensure a strong password
            validate_password(password=password)
        except ValidationError as e:
            # Print the validation error details
            print(f"Validation error: {e.messages}")
            raise serializers.ValidationError(e.messages)

        return data

    def to_representation(self, instance):
        return {
            'status': 'error',
            'message': 'Validation error',
            'errors': self.errors,
        }

    def create(self, validated_data):
        try:
            # Try to create the user
            user = User.objects.create_user(**validated_data)
            return user
        except ValidationError as ve:
            # Handle validation error and include it in the response
            self.errors = ve.messages
            return None
        except Exception as e:
            # Print the error and raise the exception again
            print(f"Error creating user: {e}")
            raise e
        
#MARKETPLACE SERIALIZERS


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'currencyName']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'categoryName']

class MarketImageSerializer(serializers.ModelSerializer):
    """Serializer for a single product image."""
    class Meta:
        model = MarketImage
        fields = ['image']


class ProductSerializer(serializers.ModelSerializer):
    # Field for displaying images in a GET request (read-only)
    images = MarketImageSerializer(many=True, read_only=True)
    
    # Fields for displaying related objects (read-only)
    seller = serializers.CharField(source='seller.username', read_only=True)
    
    # THE FIX: Add explicit output serializers for currency and category.
    # These fields will be used for GET requests, embedding the full object.
    currency = CurrencySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    
    # The writable fields for POST/PUT requests
    currency_id = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(), source='currency', write_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    
    # The field for is_active
    is_active = serializers.BooleanField(default=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 'stock_quantity', 'is_active', 
            'is_featured', 'is_sold_out', 'seller', 'images', 'state_display',
            'currency', 'state', 'category', # Now correctly represented for output
            'currency_id', 'category_id', # Writable fields for input
            'created_at', 'updated_at', 'weight'
        ]
        extra_kwargs = {'state': {'required': True}}

    def create(self, validated_data):
        images_data = self.context.get('request').FILES.getlist('images')

        product = Product.objects.create(
            seller=self.context['request'].user,
            **validated_data
        )

        for image_file in images_data:
            MarketImage.objects.create(product=product, image=image_file)
            
        return product

class MarketCommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    
    class Meta:
        model = MarketComment
        fields = ['id', 'author', 'message', 'created_at']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price_at_purchase']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    buyer = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = [
            'id',
            'buyer',
            'total_amount',
            'order_currency',
            'status',
            'transaction_id',
            'items',
            'created_at',
            'updated_at',
            
        ]

class CompletedPurchaseSerializer(serializers.ModelSerializer):
    buyer = serializers.StringRelatedField()
    seller = serializers.StringRelatedField()
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CompletedPurchase
        fields = [
            'id',
            'buyer',
            'seller',
            'product',
            'quantity',
            'total_price',
            'payment_method',
            'status',
            'created_at',
        ]
# serializers.py
class ReviewSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'author', 'rating', 'comment', 'created_at']
        read_only_fields = ['product', 'author']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'  