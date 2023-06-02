"""
URL configuration for online_shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from main_app.views import ProductsListView, CreateNewProduct, ChangeProduct, ReturnsProduct, \
    PurchasedProductsListView, LoginUser, LogoutUser, RegistrationNewUser, CartUser, ReturnsListView, AdminApprove

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ProductsListView.as_view(), name="shop"),
    path('add_product/', CreateNewProduct.as_view(), name="add_product"),
    path('change_product/<int:pk>', ChangeProduct.as_view(), name="change_product"),
    path('cart/<int:pk>/', CartUser.as_view(), name="cart"),
    path('return_product/<int:pk>/', ReturnsProduct.as_view(), name="return_product"),
    path('list_of_purchased_products/', PurchasedProductsListView.as_view(), name="list_of_purchased_products"),
    path('login/', LoginUser.as_view(), name="login"),
    path('logout/', LogoutUser.as_view(), name="logout"),
    path('registration/', RegistrationNewUser.as_view(), name="registration"),
    path('return_list/', ReturnsListView.as_view(), name="return_list"),
    path('admin_approve/<int:pk>/', AdminApprove.as_view(), name="admin_approve"),
    path('', include('main_app.urls'))
]
