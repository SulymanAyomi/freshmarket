from django.urls import path, include
from main import views
from django.contrib.auth import views as auth_views
from main import forms
from django.views.generic import TemplateView


urlpatterns = [
    path("", views.home_view, name="home"),
    path("cart/", views.CartListView.as_view(), name="cart"),
    path(
        "remove_from_cart/<slug:product>",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
    path(
        "order/address_select/",
        views.AddressSelectionView.as_view(),
        name="address_select",
    ),
    path(
        "add_to_cart/",
        views.add_to_cart,
        name="add_to_cart",
    ),
    path(
        "products/<slug:category>/",
        views.ProductListView.as_view(),
        name="products",
    ),
    path(
        "products/<str:category>/<slug:product>/",
        views.ProductDetailView,
        name="product",
    ),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            form_class=forms.AuthenticationForm,
        ),
        name="login",
    ),
    path(
        "address/",
        views.AddressListView.as_view(),
        name="address_list",
    ),
    path(
        "address/create/",
        views.AddressCreateView.as_view(),
        name="address_create",
    ),
    path(
        "address/<int:pk>/",
        views.AddressUpdateView.as_view(),
        name="address_update",
    ),
    path(
        "address/<int:pk>/delete/",
        views.AddressDeleteView.as_view(),
        name="address_delete",
    ),
    path(
        "order/done/",
        TemplateView.as_view(template_name="order_done.html"),
        name="checkout_done",
    ),
    path(
        "about-us/",
        TemplateView.as_view(template_name="about_us.html"),
        name="about-us",
    ),
    path(
        "contact-us/",
        views.ContactUsView.as_view(),
        name="contact",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("search", views.search, name="search"),
]
