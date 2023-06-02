from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib import messages
from django.views.generic.edit import DeleteView
from main_app.forms import UserCreateForm, ProductCreateForm, PurchaseCreateForm, ReturnsCreateForm
from main_app.models import Product, Purchase, Returns


# Create your views here.

class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class ProductsListView(ListView):
    model = Purchase
    template_name = 'shop.html'
    paginate_by = 3
    extra_context = {"purchase_form": PurchaseCreateForm()}
    queryset = Product.objects.all()


class CartUser(CreateView):
    http_method_names = ['post']
    form_class = PurchaseCreateForm
    template_name = 'cart.html'
    success_url = reverse_lazy('list_of_purchased_products')

    def get_form_kwargs(self):
       kwargs = super().get_form_kwargs()
       kwargs.update({
           'request': self.request,
           'pk': self.kwargs['pk']
       })
       return kwargs

    def form_valid(self, form):
        obj = form.save(commit=False)
        product = form.product
        obj.product = product
        obj.user = self.request.user
        product.quantity -= obj.quantity
        total_sum = obj.quantity * product.price
        obj.total_sum = total_sum
        self.request.user.wallet -= total_sum
        with transaction.atomic():
            obj.save()
            product.save()
            self.request.user.save()
        return super().form_valid(form=form)

    def form_invalid(self, form):
        return HttpResponseRedirect('/')


class CreateNewProduct(SuperUserRequiredMixin, CreateView):
    form_class = ProductCreateForm
    template_name = 'add_product.html'
    success_url = '/'


class ChangeProduct(SuperUserRequiredMixin, UpdateView):
    model = Product
    form_class = ProductCreateForm
    template_name = 'change_product.html'
    success_url = '/'
    queryset = Product.objects.all()


class ReturnsProduct(CreateView):
    http_method_names = ['post']
    form_class = ReturnsCreateForm
    template_name = 'return_product.html'
    success_url = '/'
    queryset = Returns.objects.all()

    def get_form_kwargs(self):
       kwargs = super().get_form_kwargs()
       kwargs.update({
           'request': self.request,
           'pk': self.kwargs['pk']
       })
       return kwargs

    def form_valid(self, form):
        obj = form.save(commit=False)
        purchase = form.purchase
        obj.purchase = purchase
        messages.success(self.request, 'Your return request has been processed!')
        with transaction.atomic():
            obj.save()
        return super().form_valid(form=form)

    def form_invalid(self, form):
        return HttpResponseRedirect('/')


class PurchasedProductsListView(ListView):
    model = Purchase
    template_name = 'list_of_purchased_products.html'
    paginate_by = 5
    queryset = Purchase.objects.all()


class LoginUser(LoginView):
    template_name = 'login.html'
    next_page = '/'


class LogoutUser(LogoutView):
    next_page = reverse_lazy('login')


class RegistrationNewUser(CreateView):
    form_class = UserCreateForm
    template_name = 'registration.html'
    success_url = reverse_lazy('login')


class ReturnsListView(SuperUserRequiredMixin, ListView):
    model = Returns
    template_name = 'return_list.html'
    paginate_by = 5
    queryset = Returns.objects.all()


class AdminApprove(SuperUserRequiredMixin, DeleteView):
    model = Returns
    queryset = Returns.objects.all()

    def post(self, request, *args, **kwargs):
        returns = Returns.objects.get(pk=self.kwargs['pk'])
        if 'approve' in self.request.POST:
            user = returns.purchase.user
            product = returns.purchase.product
            quantity = returns.purchase.quantity
            total_sum = returns.purchase.total_sum
            user.wallet += total_sum
            product.quantity += quantity
            messages.success(self.request, 'Your return request approved!')
            with transaction.atomic():
                user.save()
                product.save()
                returns.purchase.delete()
                returns.delete()
        else:
            messages.error(self.request, 'Your return request refused!')
            self.model.objects.get(pk=self.kwargs['pk']).delete()
        return HttpResponseRedirect('http://127.0.0.1:8000/return_list/')
