from django.shortcuts import render
from django.views.generic import ListView

from .models import Blog

class BlogListView(ListView):
    template_name = "blog_list.html"
    paginate_by = 2
    model = Blog
    context_object_name = 'blogs'
