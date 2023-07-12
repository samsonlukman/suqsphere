from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .views import *
from django.contrib import messages
from django.db.models import Sum
from .models import *



# This function handles the rendering of the index page with all active listings and categories
def market(request):
    # Get all active listings
    items = Market.objects.filter(isActive=True)[:4]
    allCategories = MarketCategory.objects.all()
    context = {"item": items, "category": allCategories,}
    return render(request, "market/index.html", context)

def pay(request):  
    id = request.GET.get("id")
    tx_ref = request.GET.get("tx_ref")

    if tx_ref:
        # Save the transaction reference in the database
        payment.transaction_reference = tx_ref
        payment.completed = True
        payment.save()

        # Delete paid items
        paid_items = Market.objects.filter(payment=payment)
        for item in paid_items:
            item.delete()

        # Display a success message to the user
        success_message = "Payment made successfully"

        # Redirect the user to the listing page
        return render(request, "market/pay_success.html", {
            "success_message": success_message,
            "listing": payment,
        })
    else:
        # Handle the case when the transaction reference is missing or not provided
        error_message = "Payment failed: Transaction reference not found"
        messages.error(request, error_message)
        return redirect(market)


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
    itemData = Market.objects.get(pk=id)

    # Check if the current user is in the watchlist of the listing
    isCart = request.user in itemData.cart.all()
    # Get all comments for the current listing
    allComments = MarketComment.objects.filter(item=itemData)

    # Check if the current user is the owner of the listing
    isOwner = request.user.username == itemData.owner.username

    currencies = [
        "AED", "ARS", "AUD", "BRL", "CAD", "CHF", "CZK", "ETB", "EUR", "GBP",
        "GHS", "ILS", "INR", "JPY", "KES", "MAD", "MUR", "MYR", "NGN", "NOK",
        "NZD", "PEN", "PLN", "RUB", "RWF", "SAR", "SEK", "SGD", "SLL", "TZS",
        "UGX", "USD", "XAF", "XOF", "ZAR", "ZMK", "ZMW", "MWK"
    ]

    # Render the listing page with the relevant data
    return render(request, "market/itemDetails.html", {
        "listing": itemData,
        "isListingInWatchList": isCart,
        "isOwner": isOwner,
        "flutterwaveCurrencies": currencies,
        "allComments": allComments,
    })


# This function handles the removal of a listing from the current user's watchlist
def remove_cart(request, id):
    # Get the listing data for the given id
    listingData = Market.objects.get(pk=id)
    # Get the current user
    currentUser = request.user
    # Remove the current user from the listing's watchlist
    listingData.cart.remove(currentUser)
    # Redirect to the listing page
    return HttpResponseRedirect(reverse("item",args=(id, )))

# This function handles the addition of a listing to the current user's watchlist
def add_cart(request, id):
    # Get the listing data for the given id
    listingData = Market.objects.get(pk=id)
    # Get the current user
    currentUser = request.user
    # Add the current user to the listing's watchlist
    listingData.cart.add(currentUser)

    # Redirect to the listing page
    return HttpResponseRedirect(reverse("item",args=(id, )))

# This function is responsible for displaying the watchlist page for the user


def display_cart(request):
    # Get the current user making the request
    currentUser = request.user
    # Get all the items in the user's cart
    items = currentUser.cart.all()

    # Calculate the total amount for each currency in the cart
    amount = {}
    for item in items:
        currency = item.currency
        amount[currency] = items.filter(currency=currency).aggregate(total=Sum('price'))['total']

    currencies = [
        "AED", "ARS", "AUD", "BRL", "CAD", "CHF", "CZK", "ETB", "EUR", "GBP",
        "GHS", "ILS", "INR", "JPY", "KES", "MAD", "MUR", "MYR", "NGN", "NOK",
        "NZD", "PEN", "PLN", "RUB", "RWF", "SAR", "SEK", "SGD", "SLL", "TZS",
        "UGX", "USD", "XAF", "XOF", "ZAR", "ZMK", "ZMW", "MWK"
    ]

    context = {
        "items": items,
        "flutterwaveCurrencies": currencies,
        "amount": amount,
    }

    # Render the cart page, passing in the items and amount to display
    return render(request, "market/cart.html", context)


# This function is responsible for adding a new comment to a listing
def addComment(request, id):
    # Get the current user making the request
    currentUser = request.user
    # Get the listing data for the given id
    listingData = Market.objects.get(pk=id)
    # Get the message for the new comment from the request
    message = request.POST["newComment"]

    # Create a new comment object with the author, listing, and message
    newComment = MarketComment(
        author=currentUser,
        item=listingData,
        message=message
    )
    # Save the comment to the database
    newComment.save()
    # Redirect the user back to the listing page
    return HttpResponseRedirect(reverse("item",args=(id, )))


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
    listingData = Listing.objects.get(pk=id)

    # Check if the current user is in the watchlist of the listing
    isListingInWatchList = request.user in listingData.watchlist.all()

    # Get all comments for the current listing
    allComments = MarketComment.objects.filter(listing=listingData)

    # Check if the current user is the owner of the listing
    isOwner = request.user.username == listingData.owner.username

    # Render the listing page with the relevant data
    return render(request, "market/listing.html", {
        "listing": listingData,
        "isListingInWatchList": isListingInWatchList,
        "allComments": allComments,
        "isOwner": isOwner
    })


def create_listing(request):
    if not request.user.is_authenticated:
        error_message = "You need to log in to access this page."
        return HttpResponse(error_message, status=401)

    if request.method == "GET":
        allCategories = MarketCategory.objects.all()
        allCurrencies = MarketCurrency.objects.all()
        context = {
            "category": allCategories,
            "currency": allCurrencies,
        }
        return render(request, "market/create.html", context)

    elif request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        images = request.FILES.getlist("images[]")  # Get the list of uploaded image files
        price = request.POST["price"]
        category = request.POST["category"]
        currency = request.POST["currency"]
        currentUser = request.user

        categoryData = MarketCategory.objects.get(categoryName=category)
        currencyData = MarketCurrency.objects.get(currencyName=currency)

        

        newItem = Market(
            title=title,
            description=description,
            price=price,
            category=categoryData,
            owner=currentUser,
            currency=currencyData,
        )
        newItem.save()

        for image in images:
            itemImage = MarketImage(item=newItem, image=image)
            itemImage.save()

        return HttpResponseRedirect(reverse("market"))


def displayCategory(request, category):
    """
    Handles displaying items in a specific category.
    """
    if request.method == "POST":
        # Get the category selected by the user
        formCategory = request.POST["category"]
        category = MarketCategory.objects.get(categoryName=formCategory)

        # Get all active listings in the selected category
        activeItems = Market.objects.filter(isActive=True, category=category)

        # Get all categories to display in the sidebar
        allCategories = MarketCategory.objects.all()

        return render(request, "market/category.html", {
            "items": activeItems,
            "category": allCategories
        })
    else:
        # Get the selected category from the URL parameter
        category = MarketCategory.objects.get(categoryName=category)
        
        # Get all active listings in the selected category
        activeItems = Market.objects.filter(isActive=True, category=category)

        # Get all categories to display in the sidebar
        allCategories = MarketCategory.objects.all()

        return render(request, "market/category.html", {
            "items": activeItems,
            "category": allCategories
        })

    

def selectedCategories(request):
    if request.method == "POST":
        # Get the category selected by the user
        formCategory = request.POST["category"]
        category = MarketCategory.objects.get(categoryName=formCategory)

        # Get all active listings in the selected category
        activeItems = Market.objects.filter(isActive=True, category=category)

        # Get all categories to display in the sidebar
        allCategories = MarketCategory.objects.all()

        return render(request, "market/category.html", {
            "items": activeItems,
            "category": allCategories
        })
def my_items(request):
    own_items = Market.objects.filter(owner=request.user)
    return render(request, "market/my_items.html", {
        "items": own_items,
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
            return HttpResponseRedirect(reverse("market"))
        else:
            return render(request, "market/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "market/login.html")


def logout_view(request):
    """
    Handles user logout.
    """
    logout(request)
    return HttpResponseRedirect(reverse("market"))


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
            return render(request, "network/register.html", {
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
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        except ValidationError as e:
            return render(request, "network/register.html", {
                "message": e.message
            })

        login(request, user)
        return HttpResponseRedirect(reverse("market"))
    else:
        return render(request, "network/register.html")

