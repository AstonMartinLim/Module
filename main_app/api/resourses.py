from rest_framework import permissions, viewsets, status
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.response import Response
from main_app.api.serializers import CustomUserSerializer, ProductSerializer, PurchaseSerializer, ReturnsSerializer
from main_app.models import CustomUser, Product, Purchase, Returns
from django.db import transaction


class CustomUserModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class ProductModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ChangeProductApiView(UpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Product.objects.all()
    allowed_methods = ['put', 'patch']
    serializer_class = ProductSerializer


class PurchaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

    def get_serializer_context(self):
        context = super(PurchaseModelViewSet, self).get_serializer_context()
        context.update({"user": self.request.user})
        return context

    def perform_create(self, serializer):
        serializer.validated_data['product'].quantity -= serializer.validated_data['quantity']
        self.request.user.wallet -= serializer.validated_data['product'].price * serializer.validated_data['quantity']
        with transaction.atomic():
            self.request.user.save()
            serializer.validated_data['product'].save()
            serializer.save()


class PurchaseProductListApiView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    http_method_names = ['get']


class ReturnsCreateApiView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Returns.objects.all()
    serializer_class = ReturnsSerializer

    def get_serializer_context(self):
        context = super(ReturnsCreateApiView, self).get_serializer_context()
        context.update({"request": self.request})
        return context


class ReturnsListApiView(ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Returns.objects.all()
    serializer_class = ReturnsSerializer
    http_method_names = ['get']


class ReturnsApproveDeleteApiView(DestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Returns.objects.all()
    serializer_class = ReturnsSerializer
    http_method_names = ['delete']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.purchase.user.wallet += instance.purchase.total_sum
        instance.purchase.product.quantity += instance.purchase.quantity

        with transaction.atomic():
            instance.purchase.user.save()
            instance.purchase.product.save()
            instance.purchase.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

