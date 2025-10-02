# market/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from network.models import *
from .serializers import *
from rest_framework import viewsets, permissions
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser

class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

from django.db.models import Q
from rest_framework import generics
# Ensure Product, ProductSerializer are imported from their respective locations

from django.db.models import Q
from rest_framework import generics
# Ensure Product, ProductSerializer are imported from their respective locations

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
            item.delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserOrdersView(generics.ListAPIView):
    """
    Lists a user's purchase history.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).order_by('-created_at')

class UserSalesView(generics.ListAPIView):
    """
    Lists a user's sales history.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Find all order items for products sold by the user
        sold_products = self.request.user.listed_products.all()
        order_ids = OrderItem.objects.filter(product__in=sold_products).values_list('order', flat=True)
        return Order.objects.filter(id__in=order_ids).order_by('-created_at')

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