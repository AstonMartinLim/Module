from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from main_app.api.resourses import ProductModelViewSet, PurchaseModelViewSet, ReturnsListApiView, \
    ReturnsApproveDeleteApiView, ReturnsCreateApiView, CustomUserModelViewSet, \
    ChangeProductApiView, PurchaseProductListApiView

router = routers.SimpleRouter()
router.register(r'product', ProductModelViewSet)
router.register(r'purchase', PurchaseModelViewSet)
router.register(r'user', CustomUserModelViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('login/', obtain_auth_token),
    path('api/change_product/<int:pk>/', ChangeProductApiView.as_view()),
    path('api/list_of_purchased_products/', PurchaseProductListApiView.as_view()),
    path('api/return_product/<int:pk>/', ReturnsCreateApiView.as_view()),
    path('api/return_list/', ReturnsListApiView.as_view()),
    path('api/admin_approve/<int:pk>/', ReturnsApproveDeleteApiView.as_view()),
    ]
