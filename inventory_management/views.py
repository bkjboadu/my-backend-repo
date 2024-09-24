from rest_framework.serializers import Serializer
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Store, Category, Supplier, Product, ProductVariant, ProductImage, StockEntry,ProductReview
from .serializers import StoreSerializer,ProductSerializer,ProductVariantSerializer,StockEntrySerializer,SupplierSerializer,ProductImageSerializer,CategorySerializer,ProductReviewSerializer

# Store views
class StoreListCreateView(ListCreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated,IsAdminUser]

class StoreDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]

    def destroy(self,request,*args,**kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                "detail":f"Store '{instance.name}' has been deleted successfully."
            },
            status= status.HTTP_200_OK
        )


# Category Views
class CategoryListCreateView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]

class CategoryDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]

    def destroy(self,request,*args,**kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                "detail":f"Category '{instance.name}' has been deleted successfully."
            },
            status= status.HTTP_200_OK
        )

# Supplier Views
class SupplierListCreateView(ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]

class SupplierDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]

# Product Views
class ProductListCreateView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]

class ProductDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]


# Product Variant Views
class ProductVariantListCreateView(ListCreateAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]

class ProductVariantDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]


# Product Image Views
class ProductImageListCreateView(ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]

class ProductImageDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]

# Stock Entry Views
class StockEntryListCreateView(ListCreateAPIView):
    queryset = StockEntry.objects.all()
    serializer_class = StockEntrySerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]

class StockEntryDetailView(RetrieveUpdateDestroyAPIView):
    queryset = StockEntry.objects.all()
    serializer_class = StockEntrySerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]

# ProductReview Views
class ProductReviewListCreateView(ListCreateAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]

class ProductReviewDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes =  [IsAuthenticated,IsAdminUser]
