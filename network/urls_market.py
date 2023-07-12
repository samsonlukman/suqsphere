# Import the path function from Django's URLconf module
from django.urls import path

# Import the views defined in the auctions app
from . import views_market

# Define the URL patterns for the auctions app
urlpatterns = [
    # The root URL maps to the index view
    path("", views_market.market, name="market"),
   path("pay/", views_market.pay, name="pay"),
    path("login", views_market.login_view, name="market_login"),
    path("logout", views_market.logout_view, name="market_logout"),
    path("register", views_market.register, name="market_register"),
    path("post_item", views_market.create_listing, name="post_item"),
    path('category/<str:category>/', views_market.displayCategory, name='market_category'),
    path("cat_query", views_market.selectedCategories, name="selectedCategories"),
    path("listing/<int:id>", views_market.listing, name="market_listing"),
    path("remove_cart/<int:id>", views_market.remove_cart, name="remove_cart"),
    path("add_cart/<int:id>", views_market.add_cart, name="add_cart"),
    path("cart", views_market.display_cart, name="cart"),
    path("addComment/<int:id>", views_market.addComment, name="market_comment"),
    path("item/<int:id>", views_market.closedDetails, name="item"),
    path("my_items", views_market.my_items, name="my_items"),
]
