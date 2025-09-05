from django.urls import path, include
from . import views
from network.api.views import *
from network.api.market_views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# Register the ReviewViewSet with the router
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('index', IndexView.as_view(), name='index'),
    path('random-posts', RandomPostsView.as_view(), name='random-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/reactions/', PostReactionsListView.as_view(), name='post-reactions-list'),

    path('user/', views.get_user_details, name='get_user_details'),
    path('users_by_ids/', get_users_by_ids, name='users-by-ids'),
    
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('comments/<int:pk>/like_toggle/', CommentLikeToggleView.as_view(), name='comment-like-toggle'),
    
    path('get-csrf-token/', views.get_csrf_token, name="get-csrf-token"),

    path('login/', views.user_login, name='login'),
    path('logout/', logout_view_functional, name='logout_functional_api'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    
    path('profile/<int:user_id>/', ProfileView.as_view(), name='profile'),
    path('follow/<int:user_id>/', FollowUnfollowView.as_view(), name='follow-unfollow'),
    path('posts/create/', CreatePostAPIView.as_view(), name='create-post'),

    #Marketplace URLs

    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/friends/', FriendsProductListView.as_view(), name='friends-products'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/add/', AddProductView.as_view(), name='add-product'),
    path('currencies/', CurrencyListView.as_view(), name='currency-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    
    path('cart/', CartView.as_view(), name='cart'),
    
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    
    path('orders/', UserOrdersView.as_view(), name='my-orders'),
    path('sales/', UserSalesView.as_view(), name='my-sales'),
    path('', include(router.urls)),
]