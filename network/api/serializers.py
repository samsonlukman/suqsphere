from rest_framework import serializers
from network.models import *
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    profile_pics = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'profile_pics']


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer()
    following = UserSerializer()

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following']


class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'members']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'message']


class PostImageSerializer(serializers.ModelSerializer):
    post_image = serializers.SerializerMethodField()

    class Meta:
        model = PostImage
        fields = ['id', 'post_image']

    def get_post_image(self, obj):
        return f"http://192.168.0.202:8000{obj.post_image.url}" #Must change
    
class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    post_images = PostImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True, source='postComment')  # Related name for comments
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
            'total_hahas', 'total_shocks', 'total_reactions', 'total_comments'
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




class EditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']

        
        first_name = serializers.CharField(required=False)
        last_name = serializers.CharField(required=False)
        email = serializers.EmailField(required=False)
        phone_number = serializers.CharField(required=False)
        username = serializers.CharField(required=False)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'password']
        

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