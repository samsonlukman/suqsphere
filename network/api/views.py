from django.db.models import F, ExpressionWrapper, DateTimeField, Value
from datetime import datetime
from django.db.models.functions import Coalesce
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse, reverse_lazy
from rest_framework.pagination import PageNumberPagination
from django.contrib import messages
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q, Count
from network.models import *
from network.forms import GroupForm, LibraryDocumentForm, VideoForm, RegistrationForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.template.response import TemplateResponse
from .serializers import *
import requests
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
from django.db.models import Q
from network.models import *
from .serializers import *
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.middleware.csrf import get_token
from rest_framework import filters, viewsets, status, filters, generics, permissions
from rest_framework.views import APIView
from rest_framework import status
import json
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from rest_framework.generics import RetrieveAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.core.paginator import Paginator, EmptyPage
from django.conf import settings
from django.views.generic import TemplateView

User = get_user_model()

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20

#user gets posts from friends only
class IndexView(APIView):
    """
    API view for the index page
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Users followed by the current user
        following = Follow.objects.filter(follower=user).values_list('following', flat=True)

        # Users following the current user
        followers = Follow.objects.filter(following=user).values_list('follower', flat=True)

        # Users who follow the current user but are not followed back
        following_only = User.objects.filter(id__in=followers).exclude(id__in=following)

        # Friends (users who are both following and followed by the current user)
        friends = set(following).intersection(followers)

        # Posts by friends
        posts = Post.objects.filter(user__in=friends).annotate(
            total_likes=Count('post_like'),
            total_sads=Count('postSad'),
            total_loves=Count('postLove'),
            total_hahas=Count('postHaha'),
            total_shocks=Count('postShock'),
        ).prefetch_related('postComment__author').order_by('-pinned', '-timestamp')  # Prefetch related comments

        # Paginate posts
        paginator = CustomPagination()
        page_posts = paginator.paginate_queryset(posts, request)

        # Suggested groups
        suggested_groups = Group.objects.all()

        # Groups the user is a member of
        groups = Group.objects.filter(members=user)
        is_member = groups.exists()
        is_not_member = not is_member

        # Serialize data
        posts_serializer = PostSerializer(page_posts, many=True)
        groups_serializer = GroupSerializer(groups, many=True)
        suggested_groups_serializer = GroupSerializer(suggested_groups, many=True)
        following_only_serializer = UserSerializer(following_only, many=True)

        return paginator.get_paginated_response({
            "is_member": is_member,
            "is_not_member": is_not_member,
            "following_only": following_only_serializer.data,
            "suggested_groups": suggested_groups_serializer.data,
            "posts": posts_serializer.data,
            "groups": groups_serializer.data,
        })
    
#For user to get random post
class RandomPostsView(APIView):
    """
    API view to get all posts without any filter, ordered by latest.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all posts, ordered by latest
        posts = Post.objects.annotate(
            total_likes=Count('post_like'),
            total_sads=Count('postSad'),
            total_loves=Count('postLove'),
            total_hahas=Count('postHaha'),
            total_shocks=Count('postShock'),
        ).prefetch_related('postComment__author').order_by('-pinned', '-timestamp')  # Prefetch comments for optimization

        # Paginate posts
        paginator = CustomPagination()
        page_posts = paginator.paginate_queryset(posts, request)
        # Serialize data
        posts_serializer = PostSerializer(page_posts, many=True)

        return paginator.get_paginated_response({
            "posts": posts_serializer.data
        })
class ProfileView(APIView):
    """
    API view for user profile.
    Returns details for the profile specified by user_id,
    and also indicates if the requesting user follows them.
    """
    permission_classes = [permissions.IsAuthenticated] # Or [permissions.IsAuthenticatedOrReadOnly] if public profiles

    def get(self, request, user_id):
        # The requesting user (currently logged-in user)
        requesting_user = request.user 
        
        try:
            # The user whose profile is being viewed (the actual profile user)
            profile_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the requesting_user follows this profile_user (this is correct)
        is_following = False
        if requesting_user.is_authenticated:
            is_following = Follow.objects.filter(
                follower=requesting_user,
                following=profile_user
            ).exists()

        # --- CRITICAL FIX START: Calculate connections for `profile_user` ---
        
        # Who does `profile_user` follow?
        profile_user_following_ids = Follow.objects.filter(follower=profile_user).values_list('following', flat=True)
        # Who follows `profile_user`?
        profile_user_follower_ids = Follow.objects.filter(following=profile_user).values_list('follower', flat=True)

        # Friends of `profile_user` (mutual following)
        profile_user_friends_ids = set(profile_user_following_ids).intersection(profile_user_follower_ids)

        # --- CRITICAL FIX END ---

        # Get `profile_user`'s posts (this part was already correct)
        posts = Post.objects.filter(user=profile_user).annotate(
            total_likes=Count('post_like'),
            total_sads=Count('postSad'),
            total_loves=Count('postLove'),
            total_hahas=Count('postHaha'),
            total_shocks=Count('postShock'),
        ).prefetch_related('postComment__author', 'post_images').order_by('-pinned', '-timestamp')

        # Paginate posts (assuming CustomPagination is defined and imported)
        # from .your_pagination_module import CustomPagination 
        paginator = CustomPagination() # Replace CustomPagination with your actual pagination class
        page_posts = paginator.paginate_queryset(posts, request)

        # Serialize data
        posts_serializer = PostSerializer(page_posts, many=True, context={'request': request})
        user_serializer = UserSerializer(profile_user) # Serialize the profile_user

        return paginator.get_paginated_response({
            "user": user_serializer.data,              # Data for the profile being viewed
            "posts": posts_serializer.data,            # Posts of the profile being viewed
            "is_following": is_following,              # If the requesting_user follows profile_user
            
            # --- Return connections for `profile_user` ---
            "followers_count": list(profile_user_follower_ids), # Return list of IDs for profile_user's followers
            "following_count": list(profile_user_following_ids),# Return list of IDs for profile_user's following
            "friends": list(profile_user_friends_ids),           # Return list of IDs for profile_user's friends
        })

    
class FollowUnfollowView(APIView):
    """
    API view to follow/unfollow a user
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            user_to_follow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user == user_to_follow:
            return Response({"error": "You cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)

        follow_relation, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )

        if not created:
            follow_relation.delete()
            action = "unfollowed"
        else:
            action = "followed"

        return Response({
            "status": "success",
            "action": action,
            "followers_count": user_to_follow.followers.count(),
            "following_count": request.user.following.count()
        }, status=status.HTTP_200_OK)
    

    

class CreatePostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            post_content = request.data.get("post_content")
            post_images = request.FILES.getlist("post_images[]")
            
            if not post_content and not post_images:
                return Response(
                    {"error": "Post must contain either text or an image"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(post_images) > 1:
                return Response(
                    {"error": "A post cannot have more than one image"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            post = Post.objects.create(
                postContent=post_content,
                user=request.user
            )

            for image in post_images:
                PostImage.objects.create(
                    post=post,
                    post_image=image
                )

            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    
class CommentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class CommentListCreateView(ListCreateAPIView):
    serializer_class = CommentSerializer
    pagination_class = None # Set to None, or keep if you manage pagination differently
    filter_backends = [OrderingFilter]
    ordering = ['timestamp'] # Important for chronological order of parent comments
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Fetch only top-level comments (where parent is null) for a specific post
        # IMPORTANT: Prefetch replies to avoid N+1 queries.
        queryset = Comment.objects.filter(parent__isnull=True).select_related('author').prefetch_related(
            # Prefetch nested replies. For deeper nesting, you might need recursive prefetching or a custom manager.
            # This covers 1 level of replies. For deeper, it gets complex quickly in `prefetch_related`.
            'replies__author', # Prefetch replies and their authors
            'replies__replies__author', # Prefetch 2nd level replies and their authors
            # Add more for deeper levels if needed, or consider a custom tree fetching logic
            'comment_likes', # For `likes_count` and `liked_by_me` on parent comments
            'replies__comment_likes', # For likes on 1st level replies
            'replies__replies__comment_likes', # For likes on 2nd level replies
        ).order_by('-timestamp') # Order top-level comments by most recent first for the feed

        post_id = self.request.query_params.get('post_id')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset.distinct() # Use distinct() to prevent duplicates if prefetching causes them

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication is required to post a comment.")
        # The serializer will handle saving the 'post' and 'parent' fields if provided in request.data
        serializer.save(author=self.request.user)


class CommentLikeToggleView(APIView):
    permission_classes = [IsAuthenticated] # Only authenticated users can like/unlike

    def post(self, request, pk, format=None):
        comment = get_object_or_404(Comment, pk=pk)
        user = request.user

        try:
            comment_like = CommentLike.objects.get(user=user, comment=comment)
            comment_like.delete() # If exists, unlike
            liked = False
        except CommentLike.DoesNotExist:
            CommentLike.objects.create(user=user, comment=comment) # If not, like
            liked = True

        likes_count = CommentLike.objects.filter(comment=comment).count()

        return Response({
            "comment_id": comment.id,
            "liked": liked, # Boolean indicating current like status by the user
            "likes_count": likes_count # Total likes count
        }, status=status.HTTP_200_OK)


class CommentDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        """
        Ensure only the author can update the comment.
        """
        if self.get_object().author != self.request.user:
            raise PermissionDenied("You do not have permission to edit this comment.")
        serializer.save()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    user = request.user
    print(user)
    serializer = UserSerializer(user)
    return Response(serializer.data)

class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PostDetailView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.prefetch_related(
            'post_like', 'postSad', 'postLove', 'postHaha', 'postShock'
        )
    
REACTION_MODELS = {
    'like': Like,
    'love': Love,
    'haha': Haha,
    'sad': Sad,
    'shock': Shock,
}

class PostReactionsListView(generics.ListAPIView):
    """
    API view to list users who reacted to a specific post,
    optionally filtered by reaction type.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Allow anyone to see reactions
    serializer_class = UserSerializer # We will serialize the User objects who reacted

    def get_queryset(self):
        post_id = self.kwargs['post_id'] # Get post_id from URL
        reaction_type = self.request.query_params.get('type', 'all') # Get reaction type from query params (e.g., ?type=like)
        
        post = get_object_or_404(Post, pk=post_id) # Get the Post object

        user_ids = set() # Use a set to store unique user IDs

        # Filter by reaction type
        if reaction_type == 'all':
            # If 'all', collect user IDs from all reaction types for this post
            for model_name, model_class in REACTION_MODELS.items():
                user_ids.update(model_class.objects.filter(post=post).values_list('user__id', flat=True))
        elif reaction_type in REACTION_MODELS:
            # If a specific reaction type, get user IDs for that type
            model_class = REACTION_MODELS[reaction_type]
            user_ids.update(model_class.objects.filter(post=post).values_list('user__id', flat=True))
        else:
            # If an invalid reaction type is provided, return an empty queryset
            return User.objects.none()

        # Return User objects based on the collected unique IDs
        # Order by username for consistent display, or add a reaction timestamp for sorting.
        return User.objects.filter(id__in=list(user_ids)).order_by('username')
    
    # Override list method to include total counts for all reaction types in the response
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, pk=post_id)
        
        total_counts = {}
        for reaction_type, model_class in REACTION_MODELS.items():
            total_counts[f'{reaction_type}_count'] = model_class.objects.filter(post=post).count()

        return Response({
            'reactors': serializer.data, # List of User objects
            'total_counts': total_counts, # Dictionary of all reaction counts for the post
            'total_all_reactions': sum(total_counts.values()) # Sum of all reactions
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users_by_ids(request):
    """
    Returns a list of User objects given a comma-separated string of IDs.
    Example: /api/users_by_ids/?ids=1,5,10
    """
    ids_param = request.query_params.get('ids', '')
    if not ids_param:
        return Response([], status=status.HTTP_200_OK)
    
    try:
        user_ids = [int(id_str) for id_str in ids_param.split(',') if id_str.strip()]
    except ValueError:
        return Response({"error": "Invalid ID format. Must be comma-separated integers."}, status=status.HTTP_400_BAD_REQUEST)

    users = User.objects.filter(id__in=user_ids)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
class FriendsListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
        followers_ids = Follow.objects.filter(following=user).values_list('follower_id', flat=True)
        friends_ids = set(following_ids).intersection(followers_ids)
        friends = User.objects.filter(id__in=friends_ids)
        serializer = FriendsSerializer(friends, many=True)
        return Response(serializer.data)

class MessagesPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50

class ConversationView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = MessagesPagination

    def get(self, request, other_user_id):
        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # FIX: A simple and reliable query to find a two-person conversation.
        # This filters for conversations where the current user is a participant
        # AND the other user is a participant.
        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=other_user
        ).first()
        
        print(f"DEBUG: Found conversation: {conversation}")

        if not conversation:
            print("DEBUG: No conversation found, creating a new one.")
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, other_user)
        
        messages_queryset = Message.objects.filter(conversation=conversation).order_by('-timestamp')
        
        paginator = self.pagination_class()
        paginated_messages = paginator.paginate_queryset(messages_queryset, request)
        
        messages_serializer = MessageSerializer(paginated_messages, many=True)
        
        paginated_response = paginator.get_paginated_response(messages_serializer.data)

        response_data = paginated_response.data
        response_data['conversation_id'] = conversation.id
        
        response_data['results'].reverse()
        
        return Response(response_data)
    
class RegisterAPIView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny] # Allow anyone to register
    parser_classes = [MultiPartParser, FormParser] # Required for handling file uploads (profile_pics)

    # Override the default create method to add custom pre-validation or context
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer) # Calls serializer.save() which uses custom .create()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})

class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Use Django's built-in login function to set the session
        login(request, user)

        # We can still get or create a token for future requests, if needed
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user)

        return Response({
            'token': token.key,
            'user_data': user_serializer.data,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Use Django's built-in logout function to destroy the session
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    
class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('registration/password_reset_done')
    email_template_name = 'registration/password_reset_email.html'

    def form_valid(self, form):
        context = {'email': form.cleaned_data['email']}
        return render(self.request, self.template_name, context)

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('registration/password_reset_complete')


class CustomPasswordResetCompleteView(TemplateView):
    template_name = 'registration/password_reset_complete.html'
