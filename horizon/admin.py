from django.contrib import admin
from django.db import models
from .models import Author, Category, Content, Type, Tag
from django.utils.html import format_html
from .models import UploadedImage
from django import forms


class TypeAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Show name in the list view
    search_fields = ('name',)  # Enable search by type name
    ordering = ('name',)  # Sort by name

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Show name in the list view
    search_fields = ('name',)  # Enable search by tag name
    ordering = ('name',)  # Sort by name

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')  # Show category and its parent
    list_filter = ('parent',)  # Add filter for parent category
    search_fields = ('name',)  # Allow searching by category name


class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'type', 'get_tags', 'published_at', 'updated_at', 'publish')  # Show these fields in the list view
    list_filter = ('category', 'published_at', 'publish')  # Add filters for category and date
    search_fields = ('title', 'body')  # Enable search functionality
    ordering = ('-published_at',)  # Show newest first
    # Allow multiple tag selections without overwriting
    filter_horizontal = ('tags',)  # Makes tag selection easier in admin panel
    readonly_fields = ('html_body',)

    def get_tags(self, obj):
        """
        Custom method to display multiple tags as a comma-separated string.
        """
        return ", ".join([tag.name for tag in obj.tags.all()])
    
    get_tags.short_description = 'Tags'  # Custom column name

    formfield_overrides = {
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(attrs={'rows': 50, 'style': 'width: 100%;'})},
        models.JSONField: {'widget': forms.Textarea(attrs={'rows': 5, 'cols': 120, 'style': 'width: 100%;'})},
    }


class AuthorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "title", "profile_image_preview")
    search_fields = ("first_name", "middle_name", "last_name", "title")
    list_filter = ("title",)
    
    def full_name(self, obj):
        """Display full name in the admin panel"""
        return f"{obj.first_name} {obj.middle_name + ' ' if obj.middle_name else ''}{obj.last_name}"
    
    full_name.admin_order_field = "first_name"
    full_name.short_description = "Full Name"

    def profile_image_preview(self, obj):
        """Show profile image in admin list view if available"""
        if obj.profile_image:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%;" />', obj.profile_image)
        return "No Image"
    
    profile_image_preview.short_description = "Profile Image"


class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'available_resized_images')
    readonly_fields = ('available_resized_images',)


# Register models
admin.site.register(Content, ContentAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(UploadedImage, UploadedImageAdmin)
