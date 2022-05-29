from . import forms
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import (
FormView,
CreateView,
UpdateView,
DeleteView,
)

from datetime import datetime, timedelta
from django.http import HttpResponseRedirect, request
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.core.exceptions import ObjectDoesNotExist
from .models import Cart, CartItem, Product, ProductImage, Category, ProductTag, Address
import logging
from django.contrib.auth import login, authenticate
from django.contrib import messages

logger = logging.getLogger(__name__)

# Create your views here.
# class HomeView(ListView):
#     template_name = "home.html"
#     queryset = Product.objects.filter(active=True)[:6]
#     context_object_name = 'products'
#     days = datetime.now() - timedelta(days=3) 

#     vegetabl = Category.objects.filter(products__date_updated__gt=days)
#     # for product in queryset:
#     #     print (product.productimage_set.all)
   
def home_view(request):
    context = {}
    context['products'] = Product.objects.active()[:6]
    context['fruit'] = Product.objects.active().filter(category__name='Fruit')[:5]
    context['vegetable'] = Product.objects.active().filter(category__name='Vegetable')[:5]
    context['juice'] = Product.objects.active().filter(category__name='Juice')[:5]
    context['bread'] = Product.objects.active().filter(category__name='Bread')[:5]

    
    return render(request, "home.html", context)

class ProductListView(ListView):
    template_name = "main/product_list.html"
    paginate_by = 12

    def get_queryset(self):
        self.context = {}
        category = self.kwargs["category"]
        self.category = None
        if category != "all":
            self.category = get_object_or_404(Category, slug=category)
        if self.category:
            products = Product.objects.active().filter(category=self.category)
        else:
            products = Product.objects.active()
        self.context['category'] = Category.objects.filter(slug=category)
        return products.order_by("name")
        return self.context

def ProductDetailView(request, category, product):
        category = get_object_or_404(Category, name=category)
        product = Product.objects.active().get(slug=product)
        products = Product.objects.filter(category=category)

        
        #return render(request, "productdetail.html", context)
        
        if request.method == "POST":
            formset = forms.CartItemFormSet(request.POST, instance=request.cart)
            if formset.is_valid():
                formset.save()

        else:
            formset = forms.CartItemFormSet(instance=request.cart)
        context = {
            'product': product,
            'products': products,
            "formset": formset
        }

        return render(request, "productdetail.html", context,)
        


class SignupView(FormView):
    template_name = "signup.html"
    form_class = forms.UserCreationForm

    def get_success_url(self):
        redirect_to = self.request.GET.get("next", "/")
        return redirect_to

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")
        logger.info("New signup for email=%s through SignupView", email)
        user = authenticate(email=email, password=raw_password)
        login(self.request, user)

        form.send_mail()

        messages.info(self.request, "You signed up successfully.")

        return response

class AddressListView(LoginRequiredMixin, ListView):
    model = Address

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    fields = [
        "name",
        "address",
        "zip_code",
        "city",
        "state",
    ]
    success_url = reverse_lazy("address_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    fields = [
        "name",
        "address",
        "zip_code",
        "city",
        "state",
    ]
    success_url = reverse_lazy("address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = Address
    success_url = reverse_lazy("address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

def add_to_cart(request):
    product = get_object_or_404(Product, pk=request.GET.get("product_id"))
    cart = request.cart
    if not request.cart:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
        cart = Cart.objects.create(user=user)
        request.session["cart_id"] = cart.id

    cartitem, created = CartItem.objects.get_or_create(
        cart=cart, product=product
    )
    if not created:
        cartitem.quantity += 1
        cartitem.save()
    return HttpResponseRedirect(reverse("product", args=(product.category, product.slug,)))

class ListCartItem(ListView):
     template_name = "main/product_list.html"
     paginate_by = 12
         
    def get_queryset(self):
        cart = self.request.cart



def remove_from_cart(request, product):
    product = get_object_or_404(Product, slug=product)
    cartitem = CartItem.objects.get(product=product, cart=request.cart) 
    cartitem.delete()    
    return redirect("cart", )
    # if cartitem.exists():
    #     cart = cartitem
    #     carti = 
    #     # check if item is in cart
        
    #     order = order_qs[0]
    #     # check if the order item is in the order
    #     if order.items.filter(item__slug=item.slug).exists():
    #         order_item = OrderItem.objects.filter(
    #             item=item,
    #             user=request.user,
    #             ordered=False
    #         )[0]
    #         order.items.remove(order_item)
    #         messages.info(request, "Item was removed from your cart.")
    #         return redirect("core:order-summary")
    #     else:
    #         # add a message saying the user dosent have an order
    #         messages.info(request, "Item was not in your cart.")
    #         return redirect("core:product", slug=slug)
    # else:
    #     # add a message saying the user dosent have an order
    #     messages.info(request, "u don't have an active order.")
    #     return redirect("core:product", slug=slug)
    # return redirect("core:product", slug=slug)

    class ProductDetailView(View):
    def get(self, *args, **kwargs):
        category = self.kwargs["category"]
        self.category = None
        self.category = get_object_or_404(Category, name=category)
        product = Product.objects.active().get(slug=self.kwargs['product'])
        products = Product.objects.filter(category=self.category)

        
       
        context = {
            'product': product,
            'products': products,
        }
        return render(self.request, "productdetail.html", context)