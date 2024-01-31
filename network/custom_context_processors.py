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
    default_images = [{'url': '/media/post_image/nodp.jpg', 'username': None, 'id': None}] * 9  # Create a list of nine default images
    connection_images = []

    if request.user.is_authenticated:
        try:
            # Use the provided user_id if available, otherwise use the request user's id
            user = User.objects.get(pk=user_id) if user_id else User.objects.get(pk=request.user.id)

            # Get users followed by the current user
            following = Follow.objects.filter(follower=user).values_list('following', flat=True)

            # Get users who are following the current user
            followers = Follow.objects.filter(following=user).values_list('follower', flat=True)

            # Find users who both follow the current user and are followed by the current user
            friend_ids = set(following).intersection(followers)

            # Fetch the User objects for the friends
            friends = User.objects.filter(id__in=friend_ids)

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
            # Handle any other exceptions that might occur during the query
            pass

    return {'friends': friends, 'friend_images': default_images}
