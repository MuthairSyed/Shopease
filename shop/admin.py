from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price_inr', 'date_created', 'image_preview')
    list_filter = ('category', 'date_created')
    search_fields = ('title', 'description')
    readonly_fields = ('image_preview',)
    
    @admin.display(description='Price (₹)')
    def price_inr(self, obj):
        return format_html('₹{}', obj.price)
    
    @admin.display(description='Image Preview')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.image.url)
        return "No Image"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_sub', 'parent_category')
    list_filter = ('is_sub',)
    search_fields = ('title',)
    
    @admin.display(description='Parent Category')
    def parent_category(self, obj):
        if obj.parent:
            return obj.parent.title
        return "-"