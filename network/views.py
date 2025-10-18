from django.db.models import F, ExpressionWrapper, DateTimeField, Value
from datetime import datetime
from django.db.models.functions import Coalesce
import json
import os
from django.conf import settings
from django.core import serializers
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponse, FileResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.views.generic import TemplateView
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
import json, time, asyncio
from django.db.models import Q
from django.http import Http404
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .models import *
from django.db.models import Count
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import PasswordResetView
from django.shortcuts import redirect
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from .forms import GroupForm, LibraryDocumentForm, VideoForm, RegistrationForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from network.notifications.service import NotificationService

def index(request):
    """This is the index page"""
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('network_login'))
    user = User.objects.get(pk=request.user.id)

    # Get users followed by the current user
    following = Follow.objects.filter(follower=user).values_list('following', flat=True)

    # Get users who are following the current user
    followers = Follow.objects.filter(following=user).values_list('follower', flat=True)

    following_only = User.objects.filter(id__in=followers).exclude(id__in=following)
    
    
    users_i_follow = Follow.objects.filter(follower=user).select_related('following')
    # Find users who both follow the current user and are followed by the current user
    friends = set(following).intersection(followers)
    # Get the posts by the users who are friends with the current user
    post = Post.objects.filter(user__in=friends).order_by('-timestamp')

    paginator = Paginator(post, 3) # Show 20 contacts per page.
    page_number = request.GET.get('page')
    page_post = paginator.get_page(page_number)
    suggested_groups = Group.objects.all()
    groups = Group.objects.filter(members=user)
    is_member = groups.exists()  # Check if the user is a member of at least one group
    is_not_member = not is_member  # Check if the user is not a member of any group
    profile_pics = user.profile_pics
    # Get comments for the posts displayed on the page
    comments = Comment.objects.filter(post__in=page_post)
    following = Follow.objects.filter(following=user)
    follower = Follow.objects.filter(follower=user)

    return render(request, "network/index.html", {
        "is_member": is_member,
        "following_only": following_only,
        "is_not_member": is_not_member,
        "suggested_groups": suggested_groups,
        "page_post": page_post,
        "groups": groups,
        "profile_pics": profile_pics,
        "comments": comments,
        "user": user,
        "follower": follower,
    })

def myfollowing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('network_login'))
    user = User.objects.get(pk=request.user.id)

    # Get users followed by the current user
    following = Follow.objects.filter(follower=user).values_list('following', flat=True)

    # Get users who are following the current user
    followers = Follow.objects.filter(following=user).values_list('follower', flat=True)

    following_only = User.objects.filter(id__in=followers).exclude(id__in=following)

    return render(request, "network/myfollowing.html", {"following_only": following_only})

@login_required
def share_post(request):
    if request.method == "POST":
        sharer_id = request.user.id
        try:
            data = json.loads(request.body)  # Parse JSON data from the request body
            post_id = data.get("post_id")
            friend_id = data.get("friendID")
            post = Post.objects.get(id=post_id)
            sharer = User.objects.get(id=sharer_id)
            shared_to = User.objects.get(id=friend_id)
            
            # Create a SharePost instance with the current timestamp
            share = SharePost(sharer=sharer, shared_post=post, shared_to=shared_to, timestamp=timezone.now())
            share.save()
            
            return JsonResponse({"message": "Post shared successfully!"})
        except Exception as e:
            print("Error:", e)
            return JsonResponse({"error": "Error sharing post."}, status=400)


@login_required
def group_share(request):
    if request.method == "POST":
        sharer_id = request.user.id
        try:
            data = json.loads(request.body)  # Parse JSON data from the request body
            post_id = data.get("post_id")
            group_id = data.get("groupID")
            post = Post.objects.get(id=post_id)
            sharer = User.objects.get(id=sharer_id)
            shared_to = Group.objects.get(id=group_id)
            
            # Create a SharePost instance with the current timestamp
            share = GroupShare(sharer=sharer, shared_post=post, shared_to=shared_to, timestamp=timezone.now())
            share.save()
            
            return JsonResponse({"message": "Post shared successfully!"})
        except Exception as e:
            print("Error:", e)
            return JsonResponse({"error": "Error sharing post."}, status=400)        
        

def load_posts(request):
    ...
    """
    start = int(request.GET.get("start") or 0)
    end = int(request.GET.get("end") or (start + 9))

    # Retrieve posts and related images from the database
    posts = Post.objects.select_related("user").prefetch_related("post_images").order_by("-id")[start:end]
    
    post_data = []
    for post in posts:
        user = post.user
        user_data = {
            "user": user.id,
            "username": user.username,
            "profile_pic": user.profile_pics.url if user.profile_pics else None,
            "first_name": user.first_name,
            "last_name": user.last_name,
            # Add more user attributes as needed
        }
        
        images_data = []
        for image in post.post_images.all():
            images_data.append(image.post_image.url)
        
        post_data.append({
            "scrollContent": post.postContent,
            "scrollUser": user_data,
            "scrollTimestamp": post.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "scrollImages": images_data,  # List of image URLs
            "scrollPostId": post.id,
            # Add more post attributes as needed
        })
    
    time.sleep(1)  # Introducing a delay for demonstration purposes (remove in production)
    
    #return JsonResponse({
        #"posts": post_data,
    #})"""

def group_load_posts(request):
    start = int(request.GET.get("start") or 0)
    end = int(request.GET.get("end") or (start + 9))

    # Retrieve posts and related images from the database
    posts = GroupPost.objects.select_related("user").prefetch_related("group_post_images").order_by("-id")[start:end]
    
    post_data = []
    for post in posts:
        user = post.user
        user_data = {
            "user": user.id,
            "username": user.username,
            "profile_pic": user.profile_pics.url if user.profile_pics else None,
            "first_name": user.first_name,
            "last_name": user.last_name,
            # Add more user attributes as needed
        }
        
        images_data = []
        for image in post.group_post_images.all():
            images_data.append(image.post_image.url)  # Use 'post_image' instead of 'group_post_images'
        
        post_data.append({
            "scrollContent": post.postContent,
            "scrollUser": user_data,
            "scrollTimestamp": post.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "scrollImages": images_data,  # List of image URLs
            "scrollPostId": post.id,
            # Add more post attributes as needed
        })
    
    time.sleep(1)  # Introducing a delay for demonstration purposes (remove in production)
    
    return JsonResponse({
        "posts": post_data,
    })

@login_required
def all_groups(request):
    user = request.user
    groups_not_belonged = Group.objects.exclude(members=user)
    return render(request, 'network/not_belonged_groups.html', {'groups_not_belonged': groups_not_belonged})

@login_required
def search(request):
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).distinct()

        posts = Post.objects.filter(
            Q(postContent__icontains=query) |
            Q(user__username__icontains=query) |
            Q(postComment__message__icontains=query)
        ).distinct()

        groups = Group.objects.filter(
            Q(name__icontains=query)
        ).distinct()

        group_posts = GroupPost.objects.filter(
            Q(postContent__icontains=query) |
            Q(user__username__icontains=query)
        )

        forum_posts = ForumTopic.objects.filter(
            Q(title__icontains=query) |
            Q(creator__username__icontains=query)
        )

        announcements = Announcement.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(poster__username__icontains=query)
        )

        library_documents = LibraryDocument.objects.filter(
            Q(title__icontains=query) |
            Q(uploader__username__icontains=query)
        )

        library_videos = Video.objects.filter(
            Q(title__icontains=query) |
            Q(uploader__username__icontains=query)
        )

        context = {
            'posts': posts,
            'group_posts': group_posts,
            'forum_posts': forum_posts,
            'announcements': announcements,
            'library_documents': library_documents,
            'query': query,
            'users': users,
            'groups': groups,
            'videos': library_videos, 
        }

        return render(request, "network/search_results.html", context)
    else:
        return render(request, "network/search_results.html")


def my_groups_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user
    groups = Group.objects.filter(creator=user)
    return render(request, 'network/my_groups.html', {'groups': groups})

def joined_groups_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user
    groups = Group.objects.filter(members=user)
    return render(request, 'network/joined_groups.html', {'groups': groups})

def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return JsonResponse({'success': True})
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Post not found'})
    

def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
        comment.delete()
        return JsonResponse({'success': True})
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Comment not found'})
    
def delete_group_post_comment(request, group_comment_id):
    try:
        comment = get_object_or_404(GroupComment, id=group_comment_id)
        comment.delete()
        return JsonResponse({'success': True})
    except GroupComment.DoesNotExist:
        return JsonResponse({'success': False})

def delete_group_post(request, group_post_id):
    try:
        post = GroupPost.objects.get(id=group_post_id)
        post.delete()
        return JsonResponse({'success': True})
    except GroupPost.DoesNotExist:
        return JsonResponse({'success': False})



def delete_group_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST' and request.user == group.creator:
        group.delete()
    return redirect('my_groups')

def exit_group_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST' and request.user in group.members.all():
        group.members.remove(request.user)
    return redirect('joined_groups')

def create_group(request):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()

            # Automatically add the creator to the members field
            group.members.add(request.user)

            return redirect('group_detail', group_id=group.pk)
    else:
        form = GroupForm()
    
    return render(request, 'network/create_group.html', {'form': form})


def join_group(request, group_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    group = get_object_or_404(Group, pk=group_id)
    user = request.user
    group.members.add(request.user)
    
    # Add a welcome message to the user's session
    welcome_message = "Welcome to the group!"
    messages.success(request, welcome_message)
    
    # Redirect to the group detail page
    return redirect('group_detail', group_id=group.pk)

@login_required
def group_newPost(request, group_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    if request.method == "POST":
        group_id = request.POST.get("group_id")  # Assuming the group_id is passed as a form field in the request
        group = get_object_or_404(Group, pk=group_id)
        post = request.POST["post_content"]
        post_image = request.FILES.get("post_image")
        user = User.objects.get(pk=request.user.id)

        # Assign the group to the new GroupPost instance
        postContent = GroupPost(group=group, postContent=post, user=user, post_image=post_image)
        postContent.save()
        context = {
            "postContent": postContent,
        }

        return render(request, "network/group_detail.html", context)

    return render(request, "network/group_newPost.html")


    
@login_required
def group_detail(request, group_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    user = request.user
    group = get_object_or_404(Group, pk=group_id)
    group_posts = GroupPost.objects.filter(group=group).order_by("-timestamp").select_related("user")
    shared_group_posts = GroupShare.objects.filter(shared_to=group).order_by("-timestamp")
    paginator = Paginator(group_posts, 30)
    page_number = request.GET.get('page')
    page_group_posts = paginator.get_page(page_number)

    # Filter GroupComment based on related Post objects (not GroupPost)
    post_ids = group_posts.values_list('id', flat=True)
    comments = GroupComment.objects.filter(post__in=post_ids)
    profile_pics = user.profile_pics
    is_group_member = group.members.filter(id=user.id).exists()
    is_admin = group.creator == user

    context = {
        "group": group,
        "group_posts": group_posts,
        "page_group_posts": page_group_posts,
        "profile_pics": profile_pics,
        "comments": comments,
        "group_id": group_id,
        "is_group_member": is_group_member,
        "is_admin": is_admin,
        "shared": shared_group_posts,
    }

    return render(request, "network/group_detail.html", context)



@login_required
def group_newPost(request, group_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    
    group = Group.objects.get(pk=group_id)  # Get the group instance
    if request.method == "POST":
        post_content = request.POST["post_content"]
        post_images = request.FILES.getlist("post_image[]")
        user = User.objects.get(pk=request.user.id)
        
        # Create the GroupPost instance with content, user, and group
        post = GroupPost.objects.create(postContent=post_content, user=user, group=group)
        
        # Create the GroupPostImage instances for each image
        for image in post_images:
            GroupPostImage.objects.create(postContent=post, post_image=image)
        return redirect('group_detail', group_id=group_id)  # Redirect to the group detail page

    context = {
        'group_id': group_id,
    }
    
    return render(request, "network/group_newPost.html", context)



@login_required
def group_addComment(request, post_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    if request.method == 'POST':
        message = request.POST.get('newComment')
        if not message.strip():
            messages.error(request, "Comment cannot be empty.")
        else:
            post = get_object_or_404(GroupPost, id=post_id)
            author = request.user
            comment = GroupComment.objects.create(author=author, post=post, message=message)
            group_id = post.group.id  # Store the group ID
            return redirect('group_detail', group_id=group_id)  # Redirect to the group detail page

    # If the request method is not POST or the message is empty, redirect to the same page
    return redirect('group_detail', group_id=post_id)

@login_required
def group_post_content(request, post_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    post = GroupPost.objects.get(pk=post_id)
    allComments = GroupComment.objects.filter(post=post)
    user = request.user
    
    

    return render(request, "network/group_post_content.html", {
        "posts": post,
        "allComments": allComments,
        
    })

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
def post_add_or_remove_reaction(request, post_id, reaction_type):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if request.method == 'POST':
        try:
            # Define the mapping for reaction models
            reaction_model = {
                'love': Love,
                'haha': Haha,
                'like': Like,
                'shock': Shock,
                'sad': Sad,
            }[reaction_type]

            # Check if the user already reacted to the post with this reaction
            try:
                existing_reaction = reaction_model.objects.get(post=post, user=user)
                # If the same reaction is clicked, remove it
                existing_reaction.delete()
                success = False
            except ObjectDoesNotExist:
                # Remove any other reaction by this user for this post
                Love.objects.filter(post=post, user=user).delete()
                Haha.objects.filter(post=post, user=user).delete()
                Like.objects.filter(post=post, user=user).delete()
                Shock.objects.filter(post=post, user=user).delete()
                Sad.objects.filter(post=post, user=user).delete()

                # Create the new reaction
                reaction_model.objects.create(post=post, user=user)
                success = True

                # Send notification only when adding a new reaction AND if the reactor is not the post owner
                if post.user != user:
                    try:
                        # Create reaction notification
                        NotificationService.create(
                            recipient=post.user,
                            sender=user,
                            notification_type='reaction',
                            message=f"{user.username} reacted to your post",
                            metadata={
                                'post_id': post.id, 
                                'reaction_type': reaction_type
                            }
                        )
                        print(f"Reaction notification sent to {post.user.username}")
                    except Exception as e:
                        print(f"Failed to create notification: {e}")
                        # Don't fail the whole request if notification fails

            # Update the post instance to reflect the new counts
            post.refresh_from_db()

            # Calculate the total count of all reactions
            total_count = (
                post.postLove.count() +
                post.postHaha.count() +
                post.post_like.count() +
                post.postShock.count() +
                post.postSad.count()
            )

            # Send the updated counts to the client
            data = {
                'post_love': post.postLove.count(),
                'post_haha': post.postHaha.count(),
                'post_like': post.post_like.count(),
                'post_shock': post.postShock.count(),
                'post_sad': post.postSad.count(),
                'total_count': total_count,
                'success': success,
                'post_id': post.id
            }

            return JsonResponse({"data": data})

        except KeyError:
            return JsonResponse({"error": "Invalid reaction type"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)







def group_add_or_remove_reaction(request, post_id, reaction_type):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    post = get_object_or_404(GroupPost, id=post_id)
    user = request.user

    if request.method == 'POST':
        try:
            # Get the corresponding ReactionModel based on reaction_type
            reaction_model = {
                'love': GroupLove,
                'haha': GroupHaha,
                'like': GroupLike,
                'shock': GroupShock,
                'sad': GroupSad,
            }[reaction_type]

            # Try to get the existing reaction for the user and post
            reaction = reaction_model.objects.get(post=post, user=user)

            # Reaction exists, delete it
            reaction.delete()
            success = False
        except ObjectDoesNotExist:
            # Reaction does not exist, create it
            reaction = reaction_model.objects.create(post=post, user=user)
            success = True

        # Update the post instance to reflect the new counts
        post.refresh_from_db()

        # Calculate the total count of all reactions
        total_count = (
            post.group_postLove.count() +
            post.group_postHaha.count() +
            post.group_post_like.count() +
            post.group_postShock.count() +
            post.group_postSad.count()
        )

        # Send the updated counts to the client
        data = {
            'post_love': post.group_postLove.count(),
            'post_haha': post.group_postHaha.count(),
            'post_like': post.group_post_like.count(),
            'post_shock': post.group_postShock.count(),
            'post_sad': post.group_postSad.count(),
            'total_count': total_count,
            'success': success,
            'post_id': post.id
        }

        return JsonResponse({"data": data})

    return JsonResponse({"error": "Invalid request method"}, status=400)




@login_required
def upload_document(request):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    if request.method == 'POST':
        form = LibraryDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploader = request.user
            document.save()
            return redirect('general_library')
    else:
        form = LibraryDocumentForm()

    return render(request, 'network/general_library.html', {'doc_form': form})

@login_required
def upload_video(request):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.uploader = request.user
            video.save()
            return redirect('general_library')
    else:
        form = VideoForm()

    return render(request, 'network/general_library.html', {'vid_form': form})



def general_library(request):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    documents = LibraryDocument.objects.all()
    videos = Video.objects.all()
    categories = LibraryCategory.objects.all()
    return render(request, 'network/general_library.html', {
        'documents': documents,
        'videos': videos,
        'categories': categories,
    })

def category_detail(request, category_name):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    documents = LibraryDocument.objects.filter(category__categoryName=category_name)
    videos = Video.objects.filter(category__categoryName=category_name)
    return render(request, 'network/category_detail.html', {
        'documents': documents,
        'videos': videos,
        'category_name': category_name,
    })

def add_to_favorites(request, item_id, item_type):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    user = request.user

    if item_type == 'document':
        item = get_object_or_404(LibraryDocument, pk=item_id)
        FavoriteDocument.objects.get_or_create(user=user, document=item)
    elif item_type == 'video':
        item = get_object_or_404(Video, pk=item_id)
        FavoriteVideo.objects.get_or_create(user=user, video=item)

    return redirect('my_library')

def my_library(request):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    user = request.user
    favorite_documents = FavoriteDocument.objects.filter(user=user)
    favorite_videos = FavoriteVideo.objects.filter(user=user)
    return render(request, 'network/my_library.html', {
        'favorite_documents': favorite_documents,
        'favorite_videos': favorite_videos,
    })

def view_document(request, document_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    
    document = get_object_or_404(LibraryDocument, pk=document_id)
    user_ip = request.META.get('REMOTE_ADDR')  # Get user's IP address

    # Check if the IP address has already viewed the video
    if user_ip not in document.viewers_ip:
        document.views += 1
        document.viewers_ip += f"{user_ip}\n"  # Store the IP address
        document.save()
    
    return redirect(document.file.url)

def view_video(request, video_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    
    video = get_object_or_404(Video, pk=video_id)
    user_ip = request.META.get('REMOTE_ADDR')  # Get user's IP address

    # Check if the IP address has already viewed the video
    if user_ip not in video.viewers_ip:
        video.views += 1
        video.viewers_ip += f"{user_ip}\n"  # Store the IP address
        video.save()
    
    return redirect(video.file.url)




@login_required
def forum(request):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    
    topic_list = ForumTopic.objects.all().order_by('-created_at')
    paginator = Paginator(topic_list, 30)  # Show 10 topics per page.

    page_number = request.GET.get('page')
    page_topics = paginator.get_page(page_number)

    return render(request, 'network/forum.html', {'page_topics': page_topics})

@login_required
def create_topic(request):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    if request.method == 'POST':
        title = request.POST['title']
        forum_image = request.FILES.getlist("forum_image[]")
        post_content = request.POST['post_forum_content']
        topic = ForumTopic.objects.create(title=title, creator=request.user)
        ForumPost.objects.create(content=post_content, topic=topic, creator=request.user)
        for image in forum_image:
            ForumTopicImage.objects.create(content=topic, post_image=image)
        return redirect('forum')
    return render(request, 'network/create_topic.html')

@login_required
def view_topic(request, topic_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    topic = ForumTopic.objects.get(pk=topic_id)
    posts = topic.posts.all().order_by('created_at')
    return render(request, 'network/view_topic.html', {'topic': topic, 'posts': posts})

@login_required
def add_forum_post(request, topic_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    if request.method == 'POST':
        post_content = request.POST['forum_post_content']
        topic = ForumTopic.objects.get(pk=topic_id)
        ForumPost.objects.create(content=post_content, topic=topic, creator=request.user)
        return redirect('view_topic', topic_id=topic_id)

def new_announcement(request):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    if request.method == "POST":
        title = request.POST["announcement_title"]
        content = request.POST["announcement_content"]
        announcement_image = request.FILES.getlist("announcement_image[]")
        poster = request.user
        announcement = Announcement.objects.create(poster=poster, title=title, content=content)

        for image in announcement_image:
            AnnouncementPostImage.objects.create(content=announcement, post_image=image)  # Use objects.create
        return redirect("announcements")

    

    
def announcements(request):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    
    announcement_list = Announcement.objects.all().order_by('-created_at')
    paginator = Paginator(announcement_list, 30)  # Show 10 announcements per page.

    page_number = request.GET.get('page')
    page_announcements = paginator.get_page(page_number)

    return render(request, 'network/announcements.html', {'page_announcements': page_announcements})
    

@login_required
def like_count(request):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    post = Post.objects.all().order_by("id").reverse().select_related("user")
    return render(request, "network/likecount.html", {
        "posts": post
    })

from .custom_context_processors import user_connections
@login_required
def profile(request, user_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")

    user = User.objects.get(pk=user_id)

    # Get the user's own posts


# Combine original post and shared post timestamps into a single queryset
    joined_posts = (
        Post.objects.filter(user=user)
        .annotate(combined_timestamp=Coalesce(F("sharepost__timestamp"), F("timestamp"), Value(datetime.min, output_field=DateTimeField())))
        | Post.objects.filter(sharepost__shared_to=user)
    )

# Order the queryset by the combined timestamp in descending order
    all_posts = joined_posts.distinct().order_by("-combined_timestamp")


    paginator = Paginator(all_posts, 30)  # Show 30 posts per page.
    page_number = request.GET.get('page')
    page_post = paginator.get_page(page_number)

    user_like = request.user

    following = Follow.objects.filter(following=user)
    follower = Follow.objects.filter(follower=user)
    # Assuming you have an instance of the User model (user_instance)
    


    try:
        checkFollowers = follower.filter(following=User.objects.get(pk=request.user.id))
        if len(checkFollowers) != 0:
            newFollowing = True
        else:
            newFollowing = False
    except:
        newFollowing = False

    return render(request, "network/user_profile.html", {
        
    "userProfile": user,
    "user_like": user_like,
    "page_post": page_post,
    "following": following,
    "follower": follower,
    "username": user.username,
    "isFollowing": newFollowing,
    "connections_data": user_connections(request, user_id=user_id),
})





@login_required
def edit_profile(request, user_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    
    user = User.objects.get(pk=user_id)
    
    if request.method == "POST":
        user.first_name = request.POST["1"]
        user.last_name = request.POST["2"]
        user.about = request.POST["3"]
        user.email = request.POST["4"]
        user.phone_number = request.POST["5"]
        user.save()

        # Redirect to the user profile page with updated context
        return HttpResponseRedirect(reverse("profile", args=[user_id]))

    # If the request method is not POST, handle GET request
    context = {
        "userProfile": user,
    }
    return render(request, "network/user_profile.html", context)



def post_content(request, post_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    post = Post.objects.get(pk=post_id)
    allComments = Comment.objects.filter(post=post)
    user = request.user
    

    return render(request, "network/post_content.html", {
        "posts": post,
        "allComments": allComments,
        
    })




class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'network/reset_password_email.html'
    success_url = reverse_lazy('password_reset_done')
    template_name = 'network/reset_password.html'



@login_required
def addComment(request, post_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    if request.method == 'POST':
        # Retrieve the JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))
        message = data.get('newComment')
        print(message)
        
        post = Post.objects.get(id=post_id)
        author = request.user
        comment = Comment.objects.create(author=author, post=post, message=message)
        
        # Create a dictionary with comment data to return as JSON
        comment_data = {
            'id': comment.id,
            'author_username': comment.author.username,
            'message': comment.message,
            # Add other comment properties here as needed.
        }

        return JsonResponse({'success': True, 'data': comment_data})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})







@login_required
def profile_pic(request, user_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page"
        return render(request, "network/register.html")


@login_required
def post_image(request, post_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")


@login_required
def newPost(request):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    
    if request.method == "POST":
        post_content = request.POST["post_content"]
        post_images = request.FILES.getlist("post_image[]")
        user = User.objects.get(pk=request.user.id)
        
        # Create the Post instance with content and user
        post = Post.objects.create(postContent=post_content, user=user)
        
        # Create the PostImage instances for each image
        for image in post_images:
            PostImage.objects.create(postContent=post, post_image=image)
        
        return HttpResponseRedirect(reverse("profile", args=[user.id]))




@login_required
def follow(request):
   if not request.user.is_authenticated:
        return render(request, "network/error.html")
   user_follow = request.POST["followUser"]
   current_user = User.objects.get(pk=request.user.id)
   userFollowData =User.objects.get(username=user_follow)
   saveFollowers = Follow(following=current_user, follower=userFollowData)
   saveFollowers.save()
   user_id = userFollowData.id
   return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))




@login_required
def unfollow(request):
   if not request.user.is_authenticated:
        return render(request, "network/error.html")
   user_follow = request.POST["followUser"]
   current_user = User.objects.get(pk=request.user.id)
   userFollowData =User.objects.get(username=user_follow)
   saveFollowers = Follow.objects.get(following=current_user, follower=userFollowData)
   saveFollowers.delete()
   user_id = userFollowData.id
   return HttpResponseRedirect(reverse("index"))


@login_required
def following(request):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")

    current_user = User.objects.get(pk=request.user.id)
    following = Follow.objects.filter(following=current_user)

    # Get the posts by the users the current user is following
    followingPosts = Post.objects.filter(user__in=[f.follower for f in following]).order_by('-timestamp')

    paginator = Paginator(followingPosts, 30)  # Show 20 contacts per page.
    page_number = request.GET.get('page')
    page_post = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page_post": page_post
    })

@login_required
def friends_list(request):
    friends = user_connections(request).get('friends', [])  # Use the custom context processor to get friends
    friends_per_page = 81  # Set the number of friends per page

    paginator = Paginator(friends, friends_per_page)
    page = request.GET.get('page', 1)

    try:
        friends = paginator.page(page)
    except PageNotAnInteger:
        friends = paginator.page(1)
    except EmptyPage:
        friends = paginator.page(paginator.num_pages)

    return render(request, 'network/friends_list.html', {'friends': friends})


@login_required
def edit(request, post_id):
    if not request.user.is_authenticated:
        return render(request, "network/error.html")
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Post.objects.get(pk=post_id)
        edit_post.postContent = data["content"]
        edit_post.save()
        return JsonResponse({"message": "Change successful", "data": data["content"]})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return HttpResponse("Coming Soon")
        #return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return render(request, "network/login.html")

def terms(request):
    return render(request, "network/terms.html")

def privacy_policy(request):
    return render(request, "network/privacy-policy.html")

def delete_account(request):
    return render(request, "network/delete-account.html")

def csae(request):
    return render(request, "network/csae.html")

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)

            # Save the profile picture if provided
            profile_pic = form.cleaned_data.get('profile_pic')
            if profile_pic:
                user.profile_pic = profile_pic

            user.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegistrationForm()
    return render(request, "network/register.html", {'form': form})



def assetlinks(request):
    file_path = os.path.join(settings.BASE_DIR, 'network', 'static', '.well-known', 'assetlinks.json')
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/json')
    else:
        raise Http404("assetlinks.json not found")
    
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