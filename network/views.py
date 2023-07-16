from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.views.generic import TemplateView
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
import json
from django.http import Http404
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
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



def index(request):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "network/login.html", {
            "error_message": error_message,
        })

    post = Post.objects.all().order_by("id").reverse().select_related("user")
    paginator = Paginator(post, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_post = paginator.get_page(page_number)
    user = request.user
    profile_pics = user.profile_pics
    # Get comments for the posts displayed on the page
    comments = Comment.objects.filter(post__in=page_post)

    return render(request, "network/index.html", {

        "post": post,
        "page_post": page_post,

        "profile_pics": profile_pics,
        "comments": comments,
    })


@login_required
def like_count(request):
    post = Post.objects.all().order_by("id").reverse().select_related("user")
    return render(request, "network/likecount.html", {
        "posts": post
    })


@login_required
def profile(request, user_id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "network/register.html")
    user = User.objects.get(pk=user_id)
    post = Post.objects.filter(user=user).order_by("id").reverse()
    paginator = Paginator(post, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_post = paginator.get_page(page_number)
    user_like = request.user
    post_like = Like.objects.filter(user=user_like)
    post_akbar = Allahu_akbar.objects.filter(user=user)
    post_subhanallah = Subhanallah.objects.filter(user=user)
    post_laa = Laa.objects.filter(user=user)

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
        "user_like": user_like,
        "post_like": post_like,
        "post_akbar": post_akbar,
        "post_subhanallah": post_subhanallah,
        "post_laa": post_laa,
        "page_post": page_post,
        "following": following,
        "follower": follower,
        "username": user.username,
        "isFollowing": newFollowing
    })


@login_required
def edit_profile(request, user_id):
    if request.method == "POST":
        user = User.objects.get(pk=user_id)
        user.first_name = request.POST["1"]
        user.last_name = request.POST["2"]
        user.about = request.POST["3"]
        user.email = request.POST["4"]
        user.phone_number = request.POST["5"]
        user.save()

        # Redirect to the user profile page
        return render(request, "network/user_profile.html")  # Replace 'user_profile' with the appropriate URL name


@login_required
def post_content(request, post_id):
    post = Post.objects.get(pk=post_id)
    allComments = Comment.objects.filter(post=post)
    user = request.user
    post_like = Like.objects.filter(user=user)
    post_akbar = Allahu_akbar.objects.filter(user=user)
    post_subhanallah = Subhanallah.objects.filter(user=user)
    post_laa = Subhanallah.objects.filter(user=user)
    likes = True

    if len(post_like) > 0:
        likes = True
    else:
        likes = False

    return render(request, "network/post_content.html", {
        "posts": post,
        "allComments": allComments,
        "post_like": post_like,
        "likes": likes,
        "post_akbar": post_akbar,
        "post_subhanallah": post_subhanallah,
        "post_laa": post_laa,
    })

class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'network/reset_password_email.html'
    success_url = reverse_lazy('password_reset_done')
    template_name = 'network/reset_password.html'


@login_required
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





@login_required
def profile_pic(request, user_id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page"
        return render(request, "network/register.html")


@login_required
def post_image(request, post_id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page"
        return render(request, "network/register.html")


@login_required
def newPost(request):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "network/register.html")
    if request.method == "POST":
        post = request.POST["post_content"]
        post_image = request.FILES.get("post_image")
        user = User.objects.get(pk=request.user.id)
        postContent = Post(postContent=post, user=user, post_image=post_image)
        postContent.save()
        return HttpResponseRedirect(reverse(index))


@login_required
def remove_maashaa(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    try:
        maashaa = MaaShaaAllah.objects.get(post=post, user=request.user)
        maashaa.delete()
    except MaaShaaAllah.DoesNotExist:
        messages.error(request, 'You have not liked this post.')
    return HttpResponseRedirect(reverse(post_content, kwargs={'post_id': post_id}))


@login_required
def add_maashaa(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        user = request.user
        try:
            maa = MaaShaaAllah.objects.get(post=post, user=user)
            maa.delete()
        except MaaShaaAllah.DoesNotExist:
            haha = MaaShaaAllah.objects.create(post=post, user=user)
        return HttpResponseRedirect(reverse(post_content, kwargs={'post_id': post_id}))
    else:
        raise Http404("Method not allowed")


@login_required
def remove_haha(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    try:
        haha = Haha.objects.get(post=post, user=request.user)
        haha.delete()
    except Haha.DoesNotExist:
        messages.error(request, 'You have not liked this post.')
    return HttpResponseRedirect(reverse(post_content, kwargs={'post_id': post_id}))


@login_required
def add_haha(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        user = request.user
        try:
            haha = Haha.objects.get(post=post, user=user)
            haha.delete()
        except Haha.DoesNotExist:
            haha = Haha.objects.create(post=post, user=user)
        return HttpResponseRedirect(reverse(post_content, kwargs={'post_id': post_id}))
    else:
        raise Http404("Method not allowed")


@login_required
def remove_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    try:
        like = Like.objects.get(post=post, user=request.user)
        like.delete()
        messages.success(request, 'You unliked this post.')
    except Like.DoesNotExist:
        messages.error(request, 'You have not liked this post.')

    return HttpResponseRedirect(reverse(post_content, kwargs={'post_id': post_id}))


@login_required
def add_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        user = request.user
        try:
            like = Like.objects.get(post=post, user=user)
            like.delete()
            messages.success(request, 'You unliked this post.')
        except Like.DoesNotExist:
            like = Like.objects.create(post=post, user=user)
            messages.success(request, 'You liked this post.')

        return HttpResponseRedirect(reverse(post_content, kwargs={'post_id': post_id}))
    else:
        raise Http404("Method not allowed")




@login_required
def add_akbar(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        user = request.user
        try:
            like = Allahu_akbar.objects.get(post=post, user=user)
            like.delete()
            messages.success(request, 'You unliked this post.')
        except Allahu_akbar.DoesNotExist:
            like = Allahu_akbar.objects.create(post=post, user=user)
            messages.success(request, 'You liked this post.')

        return HttpResponseRedirect(reverse(post_content, kwargs={'post_id': post_id}))
    else:
        raise Http404("Method not allowed")



@login_required
def remove_akbar(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    try:
        like = Allahu_akbar.objects.get(post=post, user=request.user)
        like.delete()
        messages.success(request, 'You unliked this post.')
    except Allahu_akbar.DoesNotExist:
        messages.error(request, 'You have not liked this post.')

    return HttpResponseRedirect(reverse(post_content, kwargs={'post_id': post_id}))


@login_required
def add_subhanallah(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        user = request.user
        try:
            like = Subhanallah.objects.get(post=post, user=user)
            like.delete()
            messages.success(request, 'You unliked this post.')
        except Subhanallah.DoesNotExist:
            like = Subhanallah.objects.create(post=post, user=user)
            messages.success(request, 'You liked this post.')

        return HttpResponseRedirect(reverse(post_content, kwargs={'post_id': post_id}))
    else:
        raise Http404("Method not allowed")



@login_required
def remove_subhanallah(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    try:
        like = Subhanallah.objects.get(post=post, user=request.user)
        like.delete()
        messages.success(request, 'You unliked this post.')
    except Subhanallah.DoesNotExist:
        messages.error(request, 'You have not liked this post.')

    return HttpResponseRedirect(reverse(post_content, kwargs={'post_id': post_id}))


@login_required
def add_laa(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        user = request.user
        try:
            like = Laa.objects.get(post=post, user=user)
            like.delete()
            messages.success(request, 'You unliked this post.')
        except Laa.DoesNotExist:
            like = Laa.objects.create(post=post, user=user)
            messages.success(request, 'You liked this post.')

        return HttpResponseRedirect(reverse(post_content, kwargs={'post_id': post_id}))
    else:
        raise Http404("Method not allowed")


@login_required
def remove_laa(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    try:
        like = Laa.objects.get(post=post, user=request.user)
        like.delete()
        messages.success(request, 'You unliked this post.')
    except Laa.DoesNotExist:
        messages.error(request, 'You have not liked this post.')

    return HttpResponseRedirect(reverse(post_content, kwargs={'post_id': post_id}))


@login_required
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




@login_required
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
   return HttpResponseRedirect(reverse("index"))


@login_required
def following(request):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "network/register.html")

    current_user = User.objects.get(pk=request.user.id)
    following = Follow.objects.filter(following=current_user)

    # Get the posts by the users the current user is following
    followingPosts = Post.objects.filter(user__in=[f.follower for f in following]).order_by('-timestamp')

    paginator = Paginator(followingPosts, 10)  # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_post = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page_post": page_post
    })


@login_required
def edit(request, post_id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "network/register.html")
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
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return render(request, "network/login.html")


def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
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
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

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

def terms(request):
    return render(request, "network/terms.html")

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