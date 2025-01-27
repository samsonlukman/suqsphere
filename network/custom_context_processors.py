from .models import *
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def my_groups_and_joined(request):
    if request.user.is_authenticated:
        my_groups = Group.objects.filter(creator=request.user)
        groups_i_joined = request.user.group_members.all()
    else:
        my_groups = []
        groups_i_joined = []

    return {
        'my_groups': my_groups,
        'groups_i_joined': groups_i_joined,
    }



def user_connections(request, user_id=None):
    friends = []  # Initialize the variable with an empty list
    default_images = [{'url': '/media/post_image/nodp.jpg', 'username': None, 'id': None}] * 9  # Default images
    media_default_images = [{'url': '/media/post_image/nodp.jpg', 'username': None, 'id': None}] * 9  # Default images
    connection_images = []
    following_only = []  # Default to an empty list
    following = []  # Default to an empty list

    if request.user.is_authenticated:
        try:
            # Use the provided user_id if available, otherwise use the request user's id
            user = User.objects.get(pk=user_id) if user_id else request.user
            
            # Get users followed by the current user
            following = list(Follow.objects.filter(follower=user).values_list('following', flat=True)) or []

            # Get users who are following the current user
            followers = list(Follow.objects.filter(following=user).values_list('follower', flat=True)) or []
            following_only = User.objects.filter(id__in=followers).exclude(id__in=following)

            # Find users who both follow the current user and are followed by the current user
            friend_ids = set(following).intersection(followers)

            # Fetch the User objects for the friends
            friends = User.objects.filter(id__in=friend_ids)
           
            user_images = PostImage.objects.filter(postContent__user=user)

            # Replace default images with user-uploaded images
            for i, user_image in enumerate(user_images):
                if user_image.post_image:
                    media_default_images[i] = {'url': user_image.post_image.url, 'username': user.username, 'id': user.id}

            # Get profile pictures of friends
            connection_images = [{'url': friend.profile_pics.url if friend.profile_pics else None,
                                  'username': friend.username,
                                  'id': friend.id} for friend in friends]

            # Replace default images with user connection images
            for i in range(len(connection_images)):
                if connection_images[i]['url']:
                    default_images[i] = connection_images[i]

        except User.DoesNotExist:
            pass  # Handle the case where the user does not exist
        except Exception as e:
            pass  # Handle any other exceptions that might occur during the query

    return {
        'friends': friends,
        'friend_images': default_images,
        "users_i_follow": following_only,
        "following": following,
        "image_urls": media_default_images,
    }
