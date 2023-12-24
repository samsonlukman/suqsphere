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



def user_connections(request):
    friends = []  # Initialize the variable with an empty list
    
    if request.user.is_authenticated:
        try:
            user = User.objects.get(pk=request.user.id)

            # Get users followed by the current user
            following = Follow.objects.filter(follower=user).values_list('following', flat=True)

            # Get users who are following the current user
            followers = Follow.objects.filter(following=user).values_list('follower', flat=True)

            # Find users who both follow the current user and are followed by the current user
            friend_ids = set(following).intersection(followers)

            # Fetch the User objects for the friends
            friends = User.objects.filter(id__in=friend_ids)
        
        except User.DoesNotExist:
            pass  # Handle the case where the user does not exist
        except Exception as e:
            # Handle any other exceptions that might occur during the query
            pass

    return {'friends': friends}
