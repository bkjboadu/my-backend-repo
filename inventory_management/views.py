from rest_framework.serializers import Serializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import (
    Store,
    Product,
    ProductImage,
    StockEntry,
    ProductReview,
)
from .serializers import (
    StoreSerializer,
    ProductSerializer,
    StockEntrySerializer,
    ProductImageSerializer,
    ProductReviewSerializer,
)
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend


# Store views
class StoreListCreateView(ListCreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return []


class StoreDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return []

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": f"Store '{instance.name}' has been deleted successfully."},
            status=status.HTTP_200_OK,
        )


# Product Views
class ProductListCreateView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return []


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]
        return []

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": f"Product'{instance.name}' has been deleted successfully."},
            status=status.HTTP_200_OK,
        )


class ProductImageListCreateView(ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return []


class ProductImageDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return []

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                "detail": f"Product Image '{instance.product.name}' has been deleted successfully."
            },
            status=status.HTTP_200_OK,
        )


# Stock Entry Views
class StockEntryListCreateView(ListCreateAPIView):
    queryset = StockEntry.objects.all()
    serializer_class = StockEntrySerializer
    permission_classes = [IsAdminUser]


class StockEntryDetailView(RetrieveUpdateDestroyAPIView):
    queryset = StockEntry.objects.all()
    serializer_class = StockEntrySerializer
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                "detail": f"StockEntry '{instance.product.name}' has been deleted successfully."
            },
            status=status.HTTP_200_OK,
        )


# ProductReview Views
class ProductReviewListCreateView(ListCreateAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs["product_id"]
        return ProductReview.objects.filter(product_id=product_id)

    def perform_create(self, serializer):
        product_id = self.kwargs["product_id"]
        product = get_object_or_404(Product, pk=product_id)
        serializer.save(user=self.request.user, product=product)


class ProductReviewDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer

    def get_permissions(self):
        if self.request.method in ["DELETE"]:
            return [IsAdminUser()]
        return []

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                "detail": f"Product Review for '{instance.product.name}' has been deleted successfully."
            },
            status=status.HTTP_200_OK,
        )
