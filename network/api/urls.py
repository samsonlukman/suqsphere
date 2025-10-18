from django.urls import path, include
from . import views
from network.api.views import *
from network.api.market_views import *
from network.api import market_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# Register the ReviewViewSet with the router
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('index', IndexView.as_view(), name='api_index'),
    path('random-posts', RandomPostsView.as_view(), name='api_random-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='api_post-detail'),
    path('posts/<int:post_id>/reactions/', PostReactionsListView.as_view(), name='api_post-reactions-list'),
    path('posts/<int:post_id>/add-remove-reaction/<str:reaction_type>/', PostReactionCreateView.as_view(), name='api_add-or-remove-reaction'),
    
    path('user/', views.get_user_details, name='api_get_user_details'),
    path('users_by_ids/', get_users_by_ids, name='users-by-ids'),
    
    path('comments/', CommentListCreateView.as_view(), name='api_comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='api_comment-detail'),
    path('comments/<int:pk>/like_toggle/', CommentLikeToggleView.as_view(), name='api_comment-like-toggle'),
    
    path('get-csrf-token/', views.get_csrf_token, name="api_get-csrf-token"),
    path('save-token/', SavePushTokenView.as_view(), name='save_token'),
 

    path('notifications', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', mark_notification_read, name='api_notification-mark-read'),


    path('login/', LoginView.as_view(), name='api_login'),
    path('logout/', LogoutView.as_view(), name='logout_functional_api'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path("verify-email/<uidb64>/<token>/", VerifyEmailAPIView.as_view(), name="verify-email"),
    
    path('profile/<int:user_id>/', ProfileView.as_view(), name='api_profile'),
    path('profile/edit/', UserProfileUpdateView.as_view(), name='profile-edit'),
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

    path('search/', GlobalSearchAPIView.as_view(), name='global-search'),

    path('my-products/', MyProductsListView.as_view(), name='my-products'),
    path('products/delete/<int:pk>/', ProductDeleteView.as_view(), name='product-delete'),
    path('products/update-status/<int:pk>/', ProductStatusUpdateView.as_view(), name='product-status-update'),
    
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout/complete/', market_views.complete_checkout, name='complete-checkout'),
    path('initialize-payment/', market_views.initialize_payment, name='initialize-payment'),
    path('create_kwik_delivery/', market_views.create_kwik_delivery, name='create-quick-delivery'),

    path('orders/', UserOrdersView.as_view(), name='user-orders'),
    path('purchases/', PurchaseHistoryView.as_view(), name='purchase-history'),
    path('sales/', SalesHistoryView.as_view(), name='sales-history'),
    path('record-purchase/', CreateCompletedPurchaseView.as_view(), name='record-purchase'),
    path('', include(router.urls)),
]