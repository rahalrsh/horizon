from django.shortcuts import render, get_object_or_404
from .models import Content, Category, Type, Tag
from django.db.models import Q
from django.core.paginator import Paginator
import os
from django.http import FileResponse, Http404
from django.conf import settings


def _getContentByTag(tag_name, limit):
    tag = Tag.objects.filter(name=tag_name).first()
    
    if tag:
        # Get all content tagged with the given tag
        content = Content.objects.filter(tags=tag, publish=True).order_by('-published_at')[:limit]
    else:
        content = Content.objects.none()  # Return an empty queryset if no tag found
    
    return content


def _getContentByParentCategory(parent_category_name, tag_name, limit):
    # Get "tech" category
    parant_category = Category.objects.filter(name=parent_category_name).first()
    tag = Tag.objects.filter(name=tag_name).first() if tag_name else None
    if parant_category:
        # Get all subcategories of "parent_category_name" including itself
        sub_categories = Category.objects.filter(Q(parent=parant_category) | Q(id=parant_category.id))
        # Query all content under "parent_category_name" and its subcategories
        if tag:
            all_content = Content.objects.filter(category__in=sub_categories, tags=tag, publish=True).order_by('-published_at')[:limit]
        else:
            all_content = Content.objects.filter(category__in=sub_categories, publish=True).order_by('-published_at')[:limit]
    else:
        all_content = Content.objects.none()  # Return empty if "tech" not found
    
    return all_content

def _getContentByCategory(parent_category_name, category_name, tag_name, limit):
    parent_category = Category.objects.filter(name=parent_category_name).first()
    category = Category.objects.filter(parent=parent_category, name=category_name).first()
    tag = Tag.objects.filter(name=tag_name).first() if tag_name else None
    
    if category and tag:
        content = Content.objects.filter(category=category, tags=tag, publish=True).order_by('-published_at')[:limit]
    elif category and not tag:
        # Get content that belongs directly to the specified category
        content = Content.objects.filter(category=category, publish=True).order_by('-published_at')[:limit]
    else:
        content = Content.objects.none()  # Return an empty queryset if the category is not found
    
    return content

def _getContentByType(type_name, tag_name, limit):
    # Get "tech" category
    type_obj = Type.objects.filter(name=type_name).first()
    tag = Tag.objects.filter(name=tag_name).first() if tag_name else None

    if tag:
        all_content = Content.objects.filter(type=type_obj, tags=tag, publish=True).order_by('-published_at')[:limit]
    else:
        all_content = Content.objects.filter(type=type_obj, publish=True).order_by('-published_at')[:limit]
    return all_content

def _getRecentContent(limit):
    all_content = Content.objects.filter(publish=True).order_by('-published_at')[:limit]
    return all_content


def home(request):
    home_main_content = _getContentByTag("Home Main", 1)
    home_featured_contents = _getContentByTag("Home Featured", 5)
    recent_contents= _getRecentContent(5)

    context = {
        'home_main_content': home_main_content,
        'home_featured_contents': home_featured_contents,
        'recent_contents': recent_contents,
    }
    return render(request, 'horizon/home.html', context)


def content_detail(request, type, slug):
    # Get the type object
    content_type = get_object_or_404(Type, name=type)
    content = get_object_or_404(Content, type=content_type, slug=slug)


    # Fetch related posts in the same category (excluding the current post)
    related_content = Content.objects.filter(
        category=content.category,  # Same category
        publish=True
    ).exclude(slug=slug)  # Exclude current post
    related_posts = related_content.order_by('-published_at')[:3]  # Get latest 3 related posts

    context = {
        'content': content,
        'author': content.author,
        'related_posts': related_posts,
        }

    return render(request, 'horizon/detail.html', context)


def news_type_page(request):
    top_news_articles = _getContentByType("news", "Top News", 3)
    news_articles = _getContentByType("news", "", 100)

    print(top_news_articles)
    
    # Paginate news articles (5 per page)
    paginator = Paginator(news_articles, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'top_news_articles': top_news_articles, # Show top 3 as featured news
        'news_articles': page_obj # Paginated articles
    }
    
    return render(request, 'horizon/news.html', context)


def products_category_page(request):
    featured_contents = _getContentByParentCategory("products", "Category Main", 3)
    hardware_content = _getContentByCategory("products", "hardware", "Category Featured", 3)
    devices_content = _getContentByCategory("products", "devices", "Category Featured", 3)
    wearables_content = _getContentByCategory("products", "wearables", "Category Featured", 3)
    assistants_content = _getContentByCategory("products", "assistants", "Category Featured", 3)
    latest_contents = _getContentByParentCategory("products", "", 100)
    
    # Paginate news articles (5 per page)
    latest_contents_paginator = Paginator(latest_contents, 3)
    page_number = request.GET.get("page")
    latest_contents_page = latest_contents_paginator.get_page(page_number)

    context = {
        'featured_contents': featured_contents, # Show top 3 as featured
        'featured_in_category': {
            'hardware': hardware_content,
            'devices': devices_content,
            'wearables': wearables_content,
            'assistants': assistants_content,
        },
        'latest_contents_page': latest_contents_page # Paginated articles
    }

    return render(request, 'horizon/products.html', context)
