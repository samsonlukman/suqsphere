from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .views import *
from django.contrib import messages

from .models import *


# This function handles the rendering of the index page with all active listings and categories
def auctions(request):
    # Get all active listings
    activeListings = Listing.objects.filter(isActive=True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "category": allCategories
    })


def pay(request, id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "auctions/error.html", {
            "error": error_message,
        })
    payment = Listing.objects.get(id=id)
    tx_ref = request.GET.get("tx_ref")

    if tx_ref:
        # Save the transaction reference in the database
        payment.transaction_reference = tx_ref
        payment.completed = True
        payment.save()

        # Display a success message to the user
        success_message = "Payment made successfully"

        # Redirect the user to the listing page
        return render(request, "auctions/pay_success.html", {
            "success_message": success_message,
            "listing": payment,
        })
    else:
        # Handle the case when the transaction reference is missing or not provided
        error_message = "Payment failed: Transaction reference not found"
        messages.error(request, error_message)
        return redirect("listing", id=id)


def closedDetails(request, id):
    """
    Handles the rendering of the details page for a specific listing.
    Parameters:
        request: HTTP request object
        id: primary key of the listing in the database
    Returns:
        An HTTP response with the listing page rendered
    """
    # Get the listing data from the database using the provided primary key
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "auctions/error.html", {
            "error": error_message,
        })
    listingData = Listing.objects.get(pk=id)

    # Check if the current user is in the watchlist of the listing
    isListingInWatchList = request.user in listingData.watchlist.all()
    # Get all comments for the current listing
    allComments = auctions_Comment.objects.filter(listing=listingData)

    # Check if the current user is the owner of the listing
    isOwner = request.user.username == listingData.owner.username

    currencies = [
        "AED", "ARS", "AUD", "BRL", "CAD", "CHF", "CZK", "ETB", "EUR", "GBP",
        "GHS", "ILS", "INR", "JPY", "KES", "MAD", "MUR", "MYR", "NGN", "NOK",
        "NZD", "PEN", "PLN", "RUB", "RWF", "SAR", "SEK", "SGD", "SLL", "TZS",
        "UGX", "USD", "XAF", "XOF", "ZAR", "ZMK", "ZMW", "MWK"
    ]

    # Render the listing page with the relevant data
    return render(request, "auctions/closedDetails.html", {
        "listing": listingData,
        "isListingInWatchList": isListingInWatchList,
        "isOwner": isOwner,
        "flutterwaveCurrencies": currencies,
        "allComments": allComments,
    })

def closed_listings(request):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "auctions/error.html", {
            "error": error_message,
        })
    closed_listing = Listing.objects.filter(isActive=False)
    context = {
        "listings": closed_listing,
    }
    return render(request, "auctions/closedListing.html", context)

# This function handles the closing of a listing and rendering the updated listing page
def closeAuction(request, id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "auctions/error.html", {
            "error": error_message,
        })
    # Get the listing data for the given id
    listingData = Listing.objects.get(pk=id)
    # Set the listing to inactive
    listingData.isActive = False
    # Save the updated listing data
    listingData.save()
    # Check if the user who requested to close the auction is the owner of the listing
    isOwner = request.user.username == listingData.owner.username
    # Check if the listing is in the current user's watchlist
    isListingInWatchList = request.user in listingData.watchlist.all()
    # Get all comments for the listing
    allComments = auctions_Comment.objects.filter(listing=listingData)
    # Render the updated listing page
    return render(request, "auctions/closedDetails.html", {
        "listing": listingData,
        "isListingInWatchList": isListingInWatchList,
        "allComments": allComments,
        "isOwner": isOwner,
        "update": True,
        "message": "Close Successful"
    })

# This function handles the removal of a listing from the current user's watchlist
def removeWatchList(request, id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "auctions/error.html", {
            "error": error_message,
        })
    # Get the listing data for the given id
    listingData = Listing.objects.get(pk=id)
    # Get the current user
    currentUser = request.user
    # Remove the current user from the listing's watchlist
    listingData.watchlist.remove(currentUser)
    # Redirect to the listing page
    return HttpResponseRedirect(reverse("closedDetails",args=(id, )))

# This function handles the addition of a listing to the current user's watchlist
def addWatchList(request, id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "auctions/error.html", {
            "error": error_message,
        })
    # Get the listing data for the given id
    listingData = Listing.objects.get(pk=id)
    # Get the current user
    currentUser = request.user
    # Add the current user to the listing's watchlist
    listingData.watchlist.add(currentUser)

    # Redirect to the listing page
    return HttpResponseRedirect(reverse("closedDetails",args=(id, )))

# This function is responsible for displaying the watchlist page for the user
def displayWatchList(request):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "auctions/error.html", {
            "error": error_message,
        })
    # Get the current user making the request
    currentUser = request.user
    # Get all the listings that are in the user's watchlist
    listings = currentUser.listingWatchlist.all()
    # Render the watchlist page, passing in the listings to display
    return render(request, "auctions/watchlist.html", {
        "listings": listings

    })

# This function is responsible for adding a new bid to a listing
def addBid(request, id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "auctions/error.html", {
            "error": error_message,
        })
    # Get the new bid amount from the request
    newBid = request.POST['newBid']
    # Get the listing data for the given id
    listingData = Listing.objects.get(pk=id)
    # Check if the current user is the owner of the listing
    isOwner = request.user.username == listingData.owner.username
    # If the new bid is higher than the current highest bid, update the bid
    if int(newBid) > listingData.price.bid:
        # Create a new bid object with the user and bid amount
        updateBid = Bid(user=request.user, bid=int(newBid))
        # Save the bid to the database
        updateBid.save()
        # Update the listing with the new highest bid
        listingData.price = updateBid
        listingData.save()
        # Render the listing page with a success message
        return render(request, "auctions/closedDetails.html", {
            "listing": listingData,
            "message": "Bid Successful",
            "update": True,
            "isOwner": isOwner
        })
    else:
        # Render the listing page with a failure message
        return render(request, "auctions/closedDetails.html", {
            "listing": listingData,
            "message": "Bid failed",
            "update": False,
            "isOwner": isOwner
        })

# This function is responsible for adding a new comment to a listing
def addComment(request, id):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "auctions/error.html", {
            "error": error_message,
        })
    # Get the current user making the request
    currentUser = request.user
    # Get the listing data for the given id
    listingData = Listing.objects.get(pk=id)
    # Get the message for the new comment from the request
    message = request.POST["newComment"]

    # Create a new comment object with the author, listing, and message
    newComment = auctions_Comment(
        author=currentUser,
        listing=listingData,
        message=message
    )
    # Save the comment to the database
    newComment.save()
    # Redirect the user back to the listing page
    return HttpResponseRedirect(reverse("closedDetails",args=(id, )))


def listing(request, id):
    """
    Handles the rendering of the details page for a specific listing.
    Parameters:
        request: HTTP request object
        id: primary key of the listing in the database
    Returns:
        An HTTP response with the listing page rendered
    """
    # Get the listing data from the database using the provided primary key
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "auctions/error.html", {
            "error": error_message,
        })
    listingData = Listing.objects.get(pk=id)

    # Check if the current user is in the watchlist of the listing
    isListingInWatchList = request.user in listingData.watchlist.all()

    # Get all comments for the current listing
    allComments = auctions_Comment.objects.filter(listing=listingData)

    # Check if the current user is the owner of the listing
    isOwner = request.user.username == listingData.owner.username

    # Render the listing page with the relevant data
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchList": isListingInWatchList,
        "allComments": allComments,
        "isOwner": isOwner
    })


def create_listing(request):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "auctions/error.html", {
            "error": error_message,
        })

    if request.method == "GET":
        allCategories = Category.objects.all()
        allCurrencies = Currency.objects.all()
        return render(request, "auctions/create.html", {
            "category": allCategories,
            "currency": allCurrencies,
        })

    elif request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        images = request.FILES.getlist("images[]")  # Get the list of uploaded image files
        price = request.POST["price"]
        category = request.POST["category"]
        currency = request.POST["currency"]
        currentUser = request.user

        categoryData = Category.objects.get(categoryName=category)
        currencyData = Currency.objects.get(currencyName=currency)

        bid = Bid(bid=float(price), user=currentUser)
        bid.save()

        newListing = Listing(
            title=title,
            description=description,
            price=bid,
            category=categoryData,
            owner=currentUser,
            currency=currencyData,
        )
        newListing.save()

        for image in images:
            listingImage = ListingImage(listing=newListing, image=image)
            listingImage.save()

        return HttpResponseRedirect(reverse("auctions"))


def displayCategory(request):
    """
    Handles displaying items in a specific category.
    """
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "auctions/error.html", {
            "error": error_message,
        })
    if request.method == "POST":
        # Get the category selected by the user
        formCategory = request.POST["category"]
        category = Category.objects.get(categoryName=formCategory)

        # Get all active listings in the selected category
        activeListings = Listing.objects.filter(isActive=True, category=category)

        # Get all categories to display in the sidebar
        allCategories = Category.objects.all()

        return render(request, "auctions/index.html", {
            "listings": activeListings,
            "category": allCategories
        })
def my_listings(request):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return render(request, "auctions/error.html", {
            "error": error_message,
        })
    listings = Listing.objects.filter(owner=request.user)
    return render(request, "auctions/my_listings.html", {
        "listings": listings
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    """
    Handles user logout.
    """
    logout(request)
    return HttpResponseRedirect(reverse("auctions"))


def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        profile_pics = request.FILES.get("profile_pic")

        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            if profile_pics:
                user.profile_pics.save(profile_pics.name, profile_pics, save=True)
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        except ValidationError as e:
            return render(request, "auctions/register.html", {
                "message": e.message
            })

        login(request, user)
        return HttpResponseRedirect(reverse("auctions"))
    else:
        return render(request, "auctions/register.html")

