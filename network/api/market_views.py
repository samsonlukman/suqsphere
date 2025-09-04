# market/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from network.models import *
from .serializers import *
from rest_framework import viewsets, permissions

class ProductListView(generics.ListAPIView):
    """
    API view for listing all products. Supports filtering by category and search.
    """
    queryset = Product.objects.filter(is_active=True, is_sold_out=False).order_by('-created_at')
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category_name = self.request.query_params.get('category', None)
        search_query = self.request.query_params.get('search', None)

        if category_name:
            queryset = queryset.filter(category__categoryName=category_name)
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )
        
        return queryset

class ProductDetailView(generics.RetrieveAPIView):
    """
    API view for a single product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class AddProductView(APIView):
    """
    API view for adding a new product.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        # We handle image upload here or use a dedicated view for it.
        # For simplicity, we'll assume the request body contains all data.
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FriendsProductListView(APIView):
    """
    API view to get products from a user's friends.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        friends = user.following.filter(follower__in=user.followed_by.all()).values_list('pk', flat=True)
        products = Product.objects.filter(seller__pk__in=friends, is_active=True)
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