from django.contrib.auth import views as auth_views

from django.urls import path
from .views import CustomPasswordResetView

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("newpost", views.newPost, name="newPost"),
    path("post_content/<int:post_id>", views.post_content, name="post_content"),
    path('profile_pic/<int:user_id/', views.profile_pic, name="profile_pic"),
    path('profile/<int:user_id>/', views.profile, name="profile"),
    path('addComment/<int:post_id>/', views.addComment, name='addComment'),
    path("follow", views.follow, name="follow"),
    path("unfollow", views.unfollow, name="unfollow"),
    path("following", views.following, name="following"),
    path("edit/<int:post_id>", views.edit, name="edit"),
     path("remove_like/<int:post_id>", views.remove_like, name="remove_like"),
    path("add_like/<int:post_id>", views.add_like, name="add_like"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
