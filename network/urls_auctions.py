# Import the path function from Django's URLconf module
from django.urls import path

# Import the views defined in the auctions app
from . import views_auctions

# Define the URL patterns for the auctions app
urlpatterns = [
    # The root URL maps to the index view
    path("", views_auctions.auctions, name="auctions"),
    # URL for the login view
    path("pay/<int:id>", views_auctions.pay, name="pay"),
    path("login", views_auctions.login_view, name="login"),
    # URL for the logout view
    path("logout", views_auctions.logout_view, name="logout"),
    # URL for the register view
    path("register", views_auctions.register, name="register"),
    # URL for the create listing view
    path("create", views_auctions.create_listing, name="create"),
    # URL for the view to display listings in a selected category
    path("displayCategory", views_auctions.displayCategory, name="displayCategory"),
    # URL for the listing detail view
    path("listing/<int:id>", views_auctions.listing, name="listing"),
    # URL for the view to remove a listing from the user's watchlist
    path("removeWatchList/<int:id>", views_auctions.removeWatchList, name="removeWatchList"),
    # URL for the view to add a listing to the user's watchlist
    path("addWatchList/<int:id>", views_auctions.addWatchList, name="addWatchList"),
    # URL for the view to display the user's watchlist
    path("watchlist", views_auctions.displayWatchList, name="watchlist"),
    # URL for the view to add a comment to a listing
    path("addComment/<int:id>", views_auctions.addComment, name="addComment"),
    # URL for the view to add a bid to a listing
    path("addBid/<int:id>", views_auctions.addBid, name="addBid"),
    # URL for the view to close an auction and select a winner
    path("closeAuction/<int:id>", views_auctions.closeAuction, name="closeAuction"),
    path("closed_listings", views_auctions.closed_listings, name="closed_listings"),
    path("listing_status/<int:id>", views_auctions.closedDetails, name="closedDetails"),
    path("my_listings", views_auctions.my_listings, name="my_listings"),
]
