from django.contrib import admin
from .models import Blog, FeedBack

# Register your models here.


class BlogAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_added',)
    list_filter = ('name', 'date_added')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(Blog, BlogAdmin)