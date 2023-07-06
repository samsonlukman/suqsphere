# Import the path function from Django's URLconf module
from django.urls import path

# Import the views defined in the auctions app
from . import views_auctions

# Define the URL patterns for the auctions app
urlpatterns = [
    # The root URL maps to the index view
    path("", views_auctions.auctions, name="auctions"),
    path("pay/<int:id>", views_auctions.pay, name="pay"),
    path("login", views_auctions.login_view, name="login"),
    path("logout", views_auctions.logout_view, name="logout"),
    path("register", views_auctions.register, name="register"),
    path("create", views_auctions.create_listing, name="create"),
    path("displayCategory", views_auctions.displayCategory, name="displayCategory"),
    path("listing/<int:id>", views_auctions.listing, name="listing"),
    path("removeWatchList/<int:id>", views_auctions.removeWatchList, name="removeWatchList"),
    path("addWatchList/<int:id>", views_auctions.addWatchList, name="addWatchList"),
    path("watchlist", views_auctions.displayWatchList, name="watchlist"),
    path("addComment/<int:id>", views_auctions.addComment, name="addComment"),
    path("addBid/<int:id>", views_auctions.addBid, name="addBid"),
    path("closeAuction/<int:id>", views_auctions.closeAuction, name="closeAuction"),
    path("closed_listings", views_auctions.closed_listings, name="closed_listings"),
    path("listing_status/<int:id>", views_auctions.closedDetails, name="closedDetails"),
    path("my_listings", views_auctions.my_listings, name="my_listings"),
]
