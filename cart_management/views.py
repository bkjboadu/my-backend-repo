from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Cart,CartItem,Wishlist,PromotionCode
from .serializers import CartSerializer,CartItemSerializer,WishlistSerializer,PromotionCodeSerializer
from django.utils import timezone
from inventory_management.models import Product

class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        cart,created = Cart.objects.get_or_create(user=request.user,is_active=True)
        if cart.has_expired():
            cart = Cart.objects.create(user=request.user)

        serializer = CartSerializer(cart)
        return Response(serializer.data,status=status.HTTP_200_OK)

class CartUserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        instances = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(instances,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)



class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,product_id):
        cart,_ = Cart.objects.get_or_create(user=request.user,is_active=True)
        if cart.has_expired():
            cart = Cart.objects.create(user=request.user)

        product = get_object_or_404(Product,id=product_id)
        quantity = request.data.get("quantity",1)

        cart_item,created = CartItem.objects.get_or_create(cart=cart,product=product)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)

        try:
            cart_item.save()
        except ValueError as e:
            return Response({"detail":str(e)},status=status.HTTP_400_BAD_REQUEST)

        return Response({'details':f"{product.name} has been added to your cart"},status=status.HTTP_200_OK)


class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self,request,item_id):
        cart_item = get_object_or_404(CartItem,id=item_id,cart__user=request.user,cart__is_active=True)

        if cart_item.cart.has_expired():
            return Response({"detail":"Your cart has expired."}, status = status.HTTP_400_BAD_REQUEST)

        quantity = request.data.get('quantity',None)
        if quantity is not None:
            cart_item.quantity = int(quantity)
            try:
                cart_item.save()
            except ValueError as e:
                return Response({"details":str(e)},status=status.HTTP_400_BAD_REQUEST)

        return Response({"details":f"{cart_item.product.name} has been updated"},status = status.HTTP_200_OK)

    def delete(self,request,item_id):
        cart_item = get_object_or_404(CartItem,id=item_id,cart__user=request.user,cart__is_active=True)
        cart_item.delete()
        return Response({"details":f"{cart_item.product.name} has been removed from your cart."},status=status.HTTP_200_OK)

class PromotionCodeListCreateView(ListCreateAPIView):
    queryset = PromotionCode.objects.all()
    permission_classes = [IsAuthenticated,IsAdminUser]
    serializer_class = PromotionCodeSerializer


class PromotionCodeDetailView(RetrieveUpdateDestroyAPIView):
    queryset = PromotionCode.objects.all()
    permission_classes = [IsAuthenticated,IsAdminUser]
    serializer_class = PromotionCodeSerializer

    def destroy(self,request,*args,**kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"details":f"Promotion Code {instance.code} has been deleted"},status=status.HTTP_200_OK)


class ApplyPromotionCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        cart = get_object_or_404(Cart,user=request.user,is_active=True)
        if cart.has_expired():
            return Response({"details":"Your cart has expired"},status=status.HTTP_400_BAD_REQUEST)

        code_str = request.data.get('code')
        if not code_str:
            return Response({'details':'Please provide a promotion code'},status=status.HTTP_400_BAD_REQUEST)

        promo_code = get_object_or_404(PromotionCode,code=code_str)
        if not promo_code.is_valid():
            return Response({'details':"This promotion code is invalid or expired."},status = status.HTTP_400_BAD_REQUEST)

        cart.promotion_code = promo_code
        cart.save()
        return Response({"details":f"Promotion code {promo_code.code} applied successfully"},status=status.HTTP_200_OK)


class WishlistView(APIView):
    permission_class = [IsAuthenticated]

    def get(self,request):
        wishlist = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(wishlist,many=True)
        return Response(serializer.data,status = status.HTTP_200_OK)

    def post(self,request,product_id):
        product = get_object_or_404(Product,id=product_id)
        Wishlist.objects.get_or_create(product=product,user=request.user)
        return Response({"details":f"{product.name} has been added to wishlist"},status=status.HTTP_200_OK)

    def delete(self,request,product_id):
        wishlist_item = get_object_or_404(Wishlist,user=request.user,product=product_id)
        wishlist_item.delete()
        return Response({'details':"Item removed from wishlist"},status=status.HTTP_200_OK)


class CheckoutView(APIView):
    permission_class = [IsAuthenticated]

    def post(self,request):
        cart = get_object_or_404(Cart,user=request.user,is_active=True)

        if cart.has_expired():
            cart = Cart.objects.create(user=request.user)

        # Process payment here(integration with payment gateway)
        cart.is_active=False
        cart.save()

        return Response({"details":"Checkout completed successfully"},status=status.HTTP_200_OK)
