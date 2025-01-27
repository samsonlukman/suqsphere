from django.db.models import F, ExpressionWrapper, DateTimeField, Value
from datetime import datetime
from django.db.models.functions import Coalesce
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
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

User = get_user_model()


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
        ).prefetch_related('postComment__author').order_by('-timestamp')  # Prefetch related comments

        # Paginate posts
        paginator = PageNumberPagination()
        paginator.page_size = 3
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

class CommentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class CommentListCreateView(ListCreateAPIView):
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    filter_backends = [OrderingFilter]
    ordering = ['-timestamp']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filters comments by a specific post ID if provided.
        """
        queryset = Comment.objects.all()
        post_id = self.request.query_params.get('post_id')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    def perform_create(self, serializer):
        """
        Associates the authenticated user as the comment's author.
        """
        serializer.save(author=self.request.user)

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
    
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        serializer = UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    logout(request)
    return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)