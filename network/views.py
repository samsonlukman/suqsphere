from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .models import *
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import firebase_admin
from firebase_admin import credentials, messaging
from django.shortcuts import redirect

def follow(request):
   if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "network/register.html")
   user_follow = request.POST["followUser"]
   current_user = User.objects.get(pk=request.user.id)
   userFollowData =User.objects.get(username=user_follow)
   saveFollowers = Follow(following=current_user, follower=userFollowData)
   saveFollowers.save()
   user_id = userFollowData.id
   return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))


def unfollow(request):
   if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "network/register.html")
   user_follow = request.POST["followUser"]
   current_user = User.objects.get(pk=request.user.id)
   userFollowData =User.objects.get(username=user_follow)
   saveFollowers = Follow.objects.get(following=current_user, follower=userFollowData)
   saveFollowers.delete()
   user_id = userFollowData.id
   return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))

def index(request):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "network/register.html")
    
    post = Post.objects.all().order_by("id").reverse().select_related("user")
    paginator = Paginator(post, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_post = paginator.get_page(page_number)
    user = request.user
    profile_pics = user.profile_pics
    allLikes = Like.objects.all()

    whoYouLiked = []
    try:
        for like in allLikes:
            if like.user.id == request.user.id:
                whoYouLiked.append(like.post.id)
    except:
        whoYouLiked = []

    # Get comments for the posts displayed on the page
    comments = Comment.objects.filter(post__in=page_post)

    return render(request, "network/index.html", {
        "post": post,
        "page_post": page_post,
        "whoYouLiked": whoYouLiked,
        "profile_pics": profile_pics,
        "comments": comments,        
    })

def post_content(request, post_id):
    post = Post.objects.get(pk=post_id)
    allComments = Comment.objects.filter(post=post)

    return render(request, "network/post_content.html", {
        "post": post,
        "allComments": allComments
    })


def add_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    if Like.objects.filter(user=user, post=post).exists():
        # The user has already liked this post, do nothing
        pass
    else:
        # The user has not already liked this post, increment the like count and create a new like instance
        post.likes += 1
        post.save()
        like = Like.objects.create(user=user, post=post)
    return redirect("index")

def remove_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    try:
        like = Like.objects.get(user=user, post=post)
    except Like.DoesNotExist:
        # The user has not already liked this post, do nothing
        pass
    else:
        # The user has already liked this post, decrement the like count and delete the like instance
        post.likes -= 1
        post.save()
        like.delete()
    return redirect("index")

def load_posts(request):
    post = Post.objects.all().order_by("id").reverse().select_related("user")
    paginator = Paginator(post, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_post = paginator.get_page(page_number)

    # Serialize the posts to JSON
    data = []
    for post in page_post:
        data.append({
            'id': post.id,
            'user': post.user.username,
            'content': post.postContent,
            'timestamp': post.timestamp.strftime('%b %d %Y, %I:%M %p'),
            'likes': post.likes.count(),
            'liked': request.user in post.likes.all(),
        })

    return JsonResponse({'posts': data})

@csrf_exempt
def subscribe(request):
    if request.method == 'POST':
        # Parse the JSON data in the request body
        data = json.loads(request.body)

        # Extract the subscription endpoint, public key, and auth token from the request
        endpoint = data.get('endpoint')
        p256dh = data.get('keys', {}).get('p256dh')
        auth = data.get('keys', {}).get('auth')
        print(endpoint)
        print(p256dh)
        print(auth)

        # Save the subscription to the database
        subscription = Subscription.objects.create(
            user=request.user,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
        )

        # Return a JSON response indicating success
        return JsonResponse({'success': True})

    # Return an error response for all other request methods
    return JsonResponse({'error': 'Invalid request method'})

# Initialize Firebase SDK
cred = credentials.Certificate('network/firebase_keys/ServiceAccountKey.json')
firebase_admin.initialize_app(cred)


@csrf_exempt
def send_push_notification(request):
    if request.method == 'POST':
        # Parse the JSON data in the request body
        data = json.loads(request.body)

        # Extract the subscription endpoint and payload from the request
        endpoint = data.get('endpoint')
        payload = data.get('payload')

        # Construct a message payload for FCM
        message = messaging.Message(
            notification=messaging.Notification(
                title=payload.get('title'),
                body=payload.get('body')
            ),
            token=endpoint
        )

        # Send the message using the Firebase Admin SDK
        response = messaging.send(message)

        # Return a JSON response indicating success
        return JsonResponse({'success': True, 'response': response})

    # Return an error response for all other request methods
    return JsonResponse({'error': 'Invalid request method'})

def addComment(request, post_id):
    if request.method == 'POST':
        message = request.POST.get('newComment')
        if not message.strip():
            messages.error(request, "Comment cannot be empty.")
            return redirect('index')
        post = Post.objects.get(id=post_id)
        author = request.user
        comment = Comment.objects.create(author=author, post=post, message=message)
        return HttpResponseRedirect(reverse("post_content",args=(post_id, )))





def profile_pic(request, user_id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page"
        return render(request, "network/register.html")
    


def newPost(request):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "network/register.html")
    if request.method == "POST":
        post = request.POST["post_content"]
        user = User.objects.get(pk=request.user.id)
        postContent = Post(postContent=post, user=user)
        postContent.save()

        # Get all subscription endpoints
        endpoints = Subscription.objects.all().values_list('endpoint', flat=True)

        # Send push notifications to all endpoints
        for endpoint in endpoints:
            send_push_notification(endpoint, 'New Post', 'A new post has been created!')

        return HttpResponseRedirect(reverse(index))


def profile(request, user_id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "network/register.html")
    user = User.objects.get(pk=user_id)
    post = Post.objects.filter(user=user).order_by("id").reverse()
    paginator = Paginator(post, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_post = paginator.get_page(page_number)
    # Get comments for the posts displayed on the page
    comments = Comment.objects.filter(post__in=page_post)

    following = Follow.objects.filter(following=user)
    follower = Follow.objects.filter(follower=user)

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
        "post": post,
        "page_post": page_post,
        "following": following,
        "follower": follower,
        "username": user.username,
        "isFollowing": newFollowing,
        "comments": comments,
    })




def following(request):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "network/register.html")
    current_user = User.objects.get(pk=request.user.id)
    following = Follow.objects.filter(following=current_user)
    posts = Post.objects.all().order_by("id").reverse()

    followingPosts = []
    for users in following:
        for post in posts:
            if users.follower == post.user:
                followingPosts.append(post)
    paginator = Paginator(followingPosts, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_post = paginator.get_page(page_number)
    

    return render(request, "network/following.html",{
        "page_post":page_post
    })


def edit(request, post_id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "network/register.html")
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Post.objects.get(pk=post_id)
        edit_post.postContent = data["content"]
        edit_post.save()
        return redirect("post_content", post_id=post_id)




def remove_like(request, post_id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "network/register.html")
    post = Post.objects.get(pk=post_id)
    post.likes -= 1
    post.save()
    user = User.objects.get(pk=request.user.id)
    like = Like.objects.filter(user=user, post=post).first()
    if like:
        like.delete()
        return JsonResponse({"likes": post.likes, "message": "Like removed!"})
    else:
        return JsonResponse({"message":"This like does not exist"})


def add_like(request, post_id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "network/register.html")
    post = Post.objects.get(pk=post_id)
    post.likes += 1
    post.save()
    user = User.objects.get(pk=request.user.id)
    newLike = Like(user=user, post=post)
    newLike.save()
    return JsonResponse({"likes": post.likes, "message": "Like added!"})






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
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        profile_pics = request.FILES.get("profile_pic")

        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            if profile_pics:
                user.profile_pics.save(profile_pics.name, profile_pics, save=True)
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        except ValidationError as e:
            return render(request, "network/register.html", {
                "message": e.message
            })

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

