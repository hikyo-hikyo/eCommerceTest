from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Store, Product, Review
from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer


class StoreViewSet(viewsets.ModelViewSet):
    """ViewSet for Store model that provides crud operations."""
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def get_permissions(self):
        """Everyone can view the stores, but only authenticated users can modify/create them."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        """Current user is the vendor of the store."""
        serializer.save(vendor=self.request.user)

    @action(detail=True, methods=['get'], url_path='products')
    def products(self, request, pk=None):
        """Api endpoint for GET /api/stores/{store_id}/products/"""
        store = self.get_object()
        products = store.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product model that provides crud operations."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        """Similar to StoreViewSet, anyone can view products, but only authenticated users can modify/create them."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        """Only the vendor of the store can add products to the store."""
        store = serializer.validated_data.get('store')
        if store and store.vendor != self.request.user:
            raise permissions.PermissionDenied(
                "You can only add products to your own store.")
        serializer.save()

    @action(detail=True, methods=['get'], url_path='reviews')
    def reviews(self, request, pk=None):
        """Api endpoint for GET /api/products/{product_id}/reviews/"""
        product = self.get_object()
        reviews = product.reviews.all()          # using related_name='reviews'
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """View set to manage reviews. Only authenticated users can create reviews."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """Review author is the current user and product is the one being reviewed."""
        serializer.save(
            user=self.request.user,
            product_id=self.request.data.get('product')
        )
