from django.urls import path, include
from . import views
from network.api.views import *


urlpatterns = [
    path('index', IndexView.as_view(), name='index'),
    path('random-posts', RandomPostsView.as_view(), name='random-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('user/', views.get_user_details, name='get_user_details'),
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('get-csrf-token/', views.get_csrf_token, name="get-csrf-token"),
    path('login', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]