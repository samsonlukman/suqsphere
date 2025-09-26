from django.urls import path, include
from . import views
from network.api.views import *
from network.api.market_views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# Register the ReviewViewSet with the router
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('index', IndexView.as_view(), name='api_index'),
    path('random-posts', RandomPostsView.as_view(), name='api_random-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='api_post-detail'),
    path('posts/<int:post_id>/reactions/', PostReactionsListView.as_view(), name='api_post-reactions-list'),

    path('user/', views.get_user_details, name='api_get_user_details'),
    path('users_by_ids/', get_users_by_ids, name='users-by-ids'),
    
    path('comments/', CommentListCreateView.as_view(), name='api_comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='api_comment-detail'),
    path('comments/<int:pk>/like_toggle/', CommentLikeToggleView.as_view(), name='api_comment-like-toggle'),
    
    path('get-csrf-token/', views.get_csrf_token, name="api_get-csrf-token"),

    path('login/', LoginView.as_view(), name='api_login'),
    path('logout/', LogoutView.as_view(), name='logout_functional_api'),
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    
    path('profile/<int:user_id>/', ProfileView.as_view(), name='api_profile'),
    path('follow/<int:user_id>/', FollowUnfollowView.as_view(), name='api_follow-unfollow'),
    path('posts/create/', CreatePostAPIView.as_view(), name='api_create-post'),

    path('friends/', FriendsListView.as_view(), name='api_friends-list'),
    path('conversations/<int:other_user_id>/', ConversationView.as_view(), name='api_conversation-detail'),

    #Marketplace URLs

    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/friends/', FriendsProductListView.as_view(), name='friends-products'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/add/', AddProductView.as_view(), name='add-product'),
    path('currencies/', CurrencyListView.as_view(), name='currency-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/update-item/', CartItemUpdateView.as_view(), name='cart-item-update'),

    path('my-products/', MyProductsListView.as_view(), name='my-products'),
    path('products/delete/<int:pk>/', ProductDeleteView.as_view(), name='product-delete'),
    path('products/update-status/<int:pk>/', ProductStatusUpdateView.as_view(), name='product-status-update'),
    
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    
    path('orders/', UserOrdersView.as_view(), name='my-orders'),
    path('sales/', UserSalesView.as_view(), name='my-sales'),
    path('', include(router.urls)),
]