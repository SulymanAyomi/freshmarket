from itertools import count, product
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
from django.db.models import Avg, Count, Min, Sum
from django.http import HttpResponse, HttpResponseRedirect, request
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.core.exceptions import ObjectDoesNotExist
from .models import Cart, CartItem, OrderItem, Product, ProductImage, Category, ProductTag, Address
import logging
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Q
from blog.models import Blog

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
    context["products"] = Product.objects.active()[:6]
    context["fruit"] = Product.objects.active().filter(category__name="Fruit")[:5]
    context["vegetable"] = Product.objects.active().filter(category__name="Vegetable")[
        :5
    ]
    context["juice"] = Product.objects.active().filter(category__name="Juice")[:5]
    context["bread"] = Product.objects.active().filter(category__name="Bread")[:5]
    context["popular"] = []
    po = OrderItem.objects.values("product__name").annotate(c=Count("id")).order_by("c")
    for product in po:
        context["popular"] += Product.objects.filter(name=product["product__name"])

    context["item"] = []
    b = CartItem.objects.values("product__name").annotate(c=Count("id")).order_by("c")
    for product in b:
        context["item"] += Product.objects.filter(name=product["product__name"])
    
    context["blogs"] = Blog.objects.all()
    print(context["blogs"])
    return render(request, "home.html", context)


class ProductListView(ListView):
    template_name = "main/product_list.html"
    paginate_by = 12

    def get_queryset(self):
        category = self.kwargs["category"]
        self.category = None
        if category != "all":
            self.category = get_object_or_404(Category, slug=category)
        if self.category:
            products = Product.objects.active().filter(category=self.category)
        else:
            products = Product.objects.active()
        return products.order_by("name")


def ProductDetailView(request, category, product):
    category = get_object_or_404(Category, name=category)
    product = Product.objects.active().get(slug=product)
    products = Product.objects.filter(category=category)

    # return render(request, "productdetail.html", context)

    if request.method == "POST":
        cartitem = CartItem.objects.get(cart=request.cart)
        formset = forms.CartForm(request.POST, instance=cartitem)
        if formset.is_valid():
            formset.save()
            return HttpResponse(cartitem.quantity)

    context = {
        "product": product,
        "products": products,
    }

    return render(
        request,
        "productdetail.html",
        context,
    )


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

    cartitem, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cartitem.quantity += 1
        cartitem.save()
    return HttpResponseRedirect(
        reverse(
            "product",
            args=(
                product.category,
                product.slug,
            ),
        )
    )


class CartListView(ListView):
    model = CartItem
    template_name = "main/cart.html"

    def get_queryset(self):
        return self.model.objects.filter(cart=self.request.cart)


def remove_from_cart(request, product):
    product = get_object_or_404(Product, slug=product)
    cartitem = CartItem.objects.get(product=product, cart=request.cart)
    cartitem.delete()
    return redirect(
        "cart",
    )
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
    #         messag:product", slug=slug)es.info(request, "Item was removed from your cart.")
    #         return redirect("core:order-summary")
    #     else:
    #         # add a message saying the user dosent have an order
    #         messages.info(request, "Item was not in your cart.")
    #         return redirect("core:product", slug=slug)
    # else:
    #     # add a message saying the user dosent have an order
    #     messages.info(request, "u don't have an active order.")
    #     return redirect("core:product", slug=slug)
    # return redirect("core


class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = "address_select.html"
    form_class = forms.AddressSelectionForm
    success_url = reverse_lazy("checkout_done")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        del self.request.session["cart_id"]
        cart = self.request.cart
        cart.create_order(
            form.cleaned_data["billing_address"],
            form.cleaned_data["shipping_address"],
            user,
        )
        return super().form_valid(form)


class ContactUsView(FormView):
    template_name = "contact.html"
    form_class = forms.ContactForm
    success_url = "/"

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)


def search(request):
    qs = request.GET.get("qs")
    context = {}
    if qs:
        context["products"] = Product.objects.filter(
            Q(name__icontains=qs) | Q(category__name__icontains=qs)
        )
        if product:
            return HttpResponse(render(request, "search.html", context))
        else:
            return HttpResponse(
                render(
                    request,
                    "search.html",
                )
            )

    else:
        return HttpResponseRedirect(
            reverse(
                "home",
            )
        )
