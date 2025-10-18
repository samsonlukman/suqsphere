# market/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal
from network.models import *
from .serializers import *
from rest_framework import viewsets, permissions
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from rest_framework import generics
from network.notifications.service import NotificationService
import requests
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
# Ensure Product, ProductSerializer are imported from their respective locations
from django.db.models import Q
from rest_framework import generics
# Ensure Product, ProductSerializer are imported from their respective locations


class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListView(generics.ListAPIView):
    """
    API view for listing all products. Supports comprehensive search and filtering.
    """
    # NOTE: Keep the base queryset clean for safety and performance
    queryset = Product.objects.filter(is_active=True, is_sold_out=False).order_by('-created_at')
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params

        # --- 1. Text Search (Includes Title, Description, Category, Seller, State) ---
        search_query = query_params.get('search', None)
        if search_query:
            # Apply search across multiple fields (case-insensitive containment)
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                # The field name for searching by category is the relationship field: 'category__categoryName'
                Q(category__categoryName__icontains=search_query) |  
                Q(seller__username__icontains=search_query) |        
                Q(state__icontains=search_query)                    
            ).distinct() # Use .distinct() to prevent duplicate results from Q lookups

        # --- 2. Simple Filters (Exact/Specific Match) ---
        
        # Category Filter (This one works)
        category_id = query_params.get('category_id', None)
        if category_id:
            # We convert the value to an integer for a strict ID comparison, though Django handles string-to-int conversion usually.
            queryset = queryset.filter(category__id=category_id) 
            
        # State Filter (Must match the state short code, e.g., 'LAGOS')
        state = query_params.get('state', None)
        if state:
            # Use __iexact for case-insensitive exact match
            queryset = queryset.filter(state__iexact=state) 
            
        is_featured = query_params.get('is_featured', None)
        if is_featured in ['true', 'True', '1']:
            queryset = queryset.filter(is_featured=True)

        # --- 3. Range Filters (Price & Stock) ---
        
        # Price Range
        min_price = query_params.get('min_price', None)
        max_price = query_params.get('max_price', None)

        try:
            if min_price:
                # Convert to float and filter: price greater than or equal to (gte)
                queryset = queryset.filter(price__gte=float(min_price))
            if max_price:
                # Convert to float and filter: price less than or equal to (lte)
                queryset = queryset.filter(price__lte=float(max_price))
        except ValueError:
             # Log the error but continue without the price filter
             print(f"DEBUG: Invalid price filter value received: min={min_price}, max={max_price}")
             pass

        # Stock Quantity
        min_stock = query_params.get('min_stock', None)
        if min_stock:
            try:
                # Convert to integer and filter: stock greater than or equal to (gte)
                queryset = queryset.filter(stock_quantity__gte=int(min_stock))
            except ValueError:
                print(f"DEBUG: Invalid stock filter value received: min_stock={min_stock}")
                pass 
                
        # IMPORTANT: You must return the filtered queryset
        return queryset
    
class ProductDetailView(generics.RetrieveAPIView):
    """
    API view for a single product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class AddProductView(APIView):
    """
    API view for adding a new product with multiple image uploads.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        # The serializer needs the request context to access uploaded files
        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()  # The custom create method will be called here
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductDeleteView(generics.DestroyAPIView):
    """
    API view to delete a product.
    Only the owner of the product can delete it.
    """
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure only the owner can see and delete their own products
        return self.queryset.filter(seller=self.request.user)
    
class ProductStatusUpdateView(generics.UpdateAPIView):
    """
    API view to toggle the active status of a product.
    """
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Ensure only the owner can update their own products
        return self.queryset.filter(seller=self.request.user)

class MyProductsListView(generics.ListAPIView):
    """
    API view to list all products owned by the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user).order_by('-created_at')


class FriendsProductListView(APIView):
    """
    API view to get products from a user's friends.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get users followed by the current user
        following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)

        # Get users who follow the current user
        followers_ids = Follow.objects.filter(following=user).values_list('follower_id', flat=True)

        # Find the intersection to get friends (mutually followed users)
        friends_ids = set(following_ids).intersection(followers_ids)

        # Get products from sellers who are friends of the current user
        products = Product.objects.filter(seller__id__in=friends_ids, is_active=True).order_by('-created_at')

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CartView(APIView):
    """
    API view for the user's shopping cart.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id, is_active=True, is_sold_out=False)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found or unavailable'}, status=status.HTTP_404_NOT_FOUND)

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
        
        if not item_created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    def delete(self, request):
        product_id = request.data.get('product_id')
        try:
            cart_item = CartItem.objects.get(cart__user=request.user, product_id=product_id)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        

class CartItemUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        try:
            cart_item = CartItem.objects.get(
                cart__user=request.user,
                product__id=request.data.get('product_id')
            )
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        new_quantity = request.data.get('quantity')
        if new_quantity is None or new_quantity < 1:
            return Response({'error': 'Quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)

        if new_quantity > cart_item.product.stock_quantity:
            return Response({'error': 'Cannot add more than available stock'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = new_quantity
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)

class CheckoutView(APIView):
    """
    Handles the checkout process.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = request.user.cart
        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total amount and currency (simplified for now)
        total_amount = sum(item.product.price * item.quantity for item in cart.items.all())
        order_currency = cart.items.first().product.currency

        # Create the order
        order = Order.objects.create(
            buyer=request.user,
            total_amount=total_amount,
            order_currency=order_currency,
            status='Pending'
        )
        
        # Create order items and clear cart
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            )

            seller = item.product.seller
            if seller != request.user:
                NotificationService.create(
                    recipient=seller,
                    sender=request.user,
                    notification_type='purchase',
                    message=f"Your product '{item.product.title}' has been purchased.",
                    metadata={'product_id': item.product.id, 'order_id': order.id}
                )

            item.delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class UserOrdersView(generics.ListAPIView):
    """Fetch all orders made by the logged-in user."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).order_by('-id')


class PurchaseHistoryView(generics.ListAPIView):
    """Fetch all completed purchases by the logged-in user (buyer)."""
    serializer_class = CompletedPurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CompletedPurchase.objects.filter(buyer=self.request.user).order_by('-id')


class SalesHistoryView(generics.ListAPIView):
    """Fetch all completed sales by the logged-in user (seller)."""
    serializer_class = CompletedPurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CompletedPurchase.objects.filter(seller=self.request.user).order_by('-id')
    


class CreateCompletedPurchaseView(generics.CreateAPIView):
    """
    Record a successful purchase after payment.
    Expected POST data:
    {
      "product_id": 5,
      "quantity": 2,
      "total_price": 4000.00,
      "payment_method": "card"
    }
    """
    serializer_class = CompletedPurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        buyer = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        total_price = request.data.get('total_price')
        payment_method = request.data.get('payment_method', 'wallet')

        if not product_id or not total_price:
            return Response({'error': 'Product ID and total price are required.'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)
        seller = product.user  # assuming Product has a `user` field as the seller

        completed = CompletedPurchase.objects.create(
            buyer=buyer,
            seller=seller,
            product=product,
            quantity=quantity,
            total_price=total_price,
            payment_method=payment_method,
            status='Completed'
        )

        serializer = CompletedPurchaseSerializer(completed)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Filter reviews by product ID
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return self.queryset.filter(product__id=product_id)
        return self.queryset

    def perform_create(self, serializer):
        # Set the author and product for the new review
        product_id = self.request.data.get('product')
        product = Product.objects.get(id=product_id)
        serializer.save(author=self.request.user, product=product)


class CurrencyListView(ListAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initialize_payment(request):
    from decimal import Decimal
    import traceback

    print("\n=== INITIALIZE PAYMENT STARTED ===")

    try:
        print("✅ AUTHENTICATED USER:", request.user)
        print("📩 RAW REQUEST DATA:", request.data)

        user = request.user
        data = request.data
        total = Decimal(data.get('total', '0'))

        if total <= 0:
            print("❌ Invalid total amount:", total)
            return Response({"error": "Invalid total amount"}, status=400)

        tx_ref = f"TX-{user.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        print("🧾 Transaction Reference:", tx_ref)

        payload = {
            "tx_ref": tx_ref,
            "amount": str(total),
            "currency": "NGN",
            "redirect_url": "suqsphere://payment-success",
            "customer": {
                "email": user.email,
                "name": user.get_full_name() or user.username,
                 "phone_number": user.phone_number,
            },
            "customizations": {
                "title": "Suqsphere Purchase",
                "description": "Payment for items",
            },
        }

        print("📦 Payload Sent to Flutterwave:", payload)

        headers = {
            "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        print("🔐 Headers:", headers)

        response = requests.post("https://api.flutterwave.com/v3/payments", json=payload, headers=headers)
        print("🌍 Flutterwave Response Code:", response.status_code)
        print("📨 Flutterwave Response Body:", response.text)

        res_data = response.json()

        if res_data.get("status") == "success":
            print("✅ Payment initialized successfully!")

            order = Order.objects.create(
                buyer=user,
                total_amount=total,
                flutterwave_tx_ref=tx_ref,
            )

            # Add order items
            cart_items = CartItem.objects.filter(cart__user=user)
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    seller=item.product.seller,
                    quantity=item.quantity,
                    price_at_purchase=item.product.price,
                )

            print(f"🛒 Order #{order.id} created with {cart_items.count()} items")

            # ✅ Clear the cart AFTER successfully creating the order
            deleted_count, _ = CartItem.objects.filter(cart__user=user).delete()
            print(f"🧹 Cleared {deleted_count} items from user's cart after order creation")

            return Response({"payment_link": res_data["data"]["link"]})

        else:
            print("❌ Flutterwave responded with error:", res_data)
            return Response({"error": res_data}, status=400)

    except Exception as e:
        print("🔥 Exception occurred during payment initialization:")
        print(traceback.format_exc())
        return Response({"error": str(e)}, status=500)

    finally:
        print("=== INITIALIZE PAYMENT ENDED ===\n")




def create_kwik_delivery(order):
    url = "https://api.kwik.delivery/api/v1/deliveries"
    headers = {
        "Authorization": f"Bearer {settings.KWIK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "pickup": {
            "address": "Warehouse address",
            "contact_name": "Suqsphere Dispatch",
            "contact_phone": "+2348000000000"
        },
        "dropoff": {
            "address": "Customer Address",
            "contact_name": order.buyer.get_full_name(),
            "contact_phone": order.buyer.profile.phone_number,
        },
        "package": {
            "weight": "2kg",
            "description": f"Order #{order.id} items"
        },
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        data = response.json()
        order.kwik_delivery_id = data["id"]
        order.delivery_status = "picked_up"
        order.save()
        return data
    else:
        return None

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_checkout(request):
    reference = request.data.get('reference')
    address = request.data.get('delivery_address')
    city = request.data.get('city')
    state = request.data.get('state')
    phone = request.data.get('phone')

    # ✅ Verify payment with Flutterwave
    headers = {'Authorization': f'Bearer {settings.FLW_SECRET_KEY}'}
    verify_url = f"https://api.flutterwave.com/v3/transactions/{reference}/verify"
    response = requests.get(verify_url, headers=headers)
    data = response.json()

    if data['status'] == 'success' and data['data']['status'] == 'successful':
        # ✅ Create order & trigger Kwik Delivery here
        # Example:
        # create_order(user=request.user, address=address, total=data['data']['amount'])
        # send_to_kwik(address, city, state, phone)
        return Response({'detail': 'Order created and delivery initiated.'})
    else:
        return Response({'detail': 'Payment verification failed.'}, status=400)
    

class UserOrdersView(generics.ListAPIView):
    """Fetch all orders made by the logged-in user."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).order_by('-id')


class PurchaseHistoryView(generics.ListAPIView):
    """Fetch all completed purchases by the logged-in user (buyer)."""
    serializer_class = CompletedPurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CompletedPurchase.objects.filter(buyer=self.request.user).order_by('-id')


class SalesHistoryView(generics.ListAPIView):
    """Fetch all completed sales by the logged-in user (seller)."""
    serializer_class = CompletedPurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CompletedPurchase.objects.filter(seller=self.request.user).order_by('-id')