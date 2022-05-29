from django.urls import path, include
from blog import views
from django.contrib.auth import views as auth_views
from main import forms

urlpatterns = [
    path(
            "blog/",
            views.BlogListView.as_view(),
            name="blog_list",
        ),
]