
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("newpost", views.newPost, name="newPost"),
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
    path('subscribe/', views.subscribe, name='subscribe'),
    path('send_push_notification/', views.send_push_notification, name='send_push_notification'),
] 
