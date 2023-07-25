from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("terms", views.terms, name="terms"),
    path("newpost", views.newPost, name="newPost"),
    path("python_course", views.python_course, name="python_course"),
    path("pay/<str:tx_ref>", views.pay, name="py_pay"),
    path("post_content/<int:post_id>", views.post_content, name="post_content"),
    path("post_image/<int:post_id>", views.post_image, name="post_image"),
    path('profile_pic/<int:user_id/', views.profile_pic, name="profile_pic"),
    path('profile/<int:user_id>/', views.profile, name="profile"),
    path('edit_profile/<int:user_id>/', views.edit_profile, name="edit_profile"),
    path('addComment/<int:post_id>/', views.addComment, name='addComment'),
    path("follow", views.follow, name="follow"),
    path("unfollow", views.unfollow, name="unfollow"),
    path("following", views.following, name="following"),
    path("like_count", views.like_count, name="like_count"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("remove_like/<int:post_id>", views.remove_like, name="remove_like"),
    path("add_like/<int:post_id>", views.add_like, name="add_like"),
    path("remove_akbar/<int:post_id>", views.remove_akbar, name="remove_like"),
    path("add_akbar/<int:post_id>", views.add_akbar, name="add_akbar"),
    path("remove_subhanallah/<int:post_id>", views.remove_subhanallah, name="remove_subhanallah"),
    path("add_subhanallah/<int:post_id>", views.add_subhanallah, name="add_subhanallah"),
    path("remove_maashaa/<int:post_id>", views.remove_maashaa, name="remove_maashaa"),
    path("add_maashaa/<int:post_id>", views.add_maashaa, name="add_maashaa"),
    path("remove_haha/<int:post_id>", views.remove_haha, name="remove_haha"),
    path("add_haha/<int:post_id>", views.add_haha, name="add_haha"),
    path("remove_laa/<int:post_id>", views.remove_laa, name="remove_laa"),
    path("add_laa/<int:post_id>", views.add_laa, name="add_laa"),
    path("login", views.login_view, name="network_login"),
    path("logout", views.logout_view, name="network_logout"),
    path("register", views.register, name="network_register"),
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    # Include the URLs from auctions_urls.py
    path("auctions/", include("network.urls_auctions")),
    path("market/", include("network.urls_market")),


]
