from django.shortcuts import render, get_object_or_404
from .models import Content, Category, Type, Tag
from django.db.models import Q
from django.core.paginator import Paginator
import json
from django.utils.html import escape
from django.utils.timezone import localtime


def _getContentByTag(tag_name, limit):
    tag = Tag.objects.filter(name=tag_name).first()
    
    if tag:
        # Get all content tagged with the given tag
        content = Content.objects.filter(tags=tag, publish=True).order_by('-published_at')[:limit]
    else:
        content = Content.objects.none()  # Return an empty queryset if no tag found
    
    return content


def _get_filtered_content(include_categories, filter_categories=None, exclude_categories=None, include_tags=None, exclude_tags=None, limit=None):
    """
    Filters Content based on included/excluded categories and tags.

    Args:
        include_categories (list of Category): Required categories.
        filter_categories (list of Category): Further filter by these categories.
        exclude_categories (list of Category, optional): Categories to exclude.
        include_tags (list of Tag, optional): Tags to include.
        exclude_tags (list of Tag, optional): Tags to exclude.
        limit (int, optional): Maximum number of results. If None, return all.

    Returns:
        QuerySet of Content objects.
    """

    if not include_categories:
        raise ValueError("include_categories is required and cannot be empty.")

    # Start with the required categories filter
    query = Q(categories__in=include_categories)

    # Exclude specific categories (if provided)
    if exclude_categories:
        query &= ~Q(categories__in=exclude_categories)

    # Further filter content that has the specific category (e.g., "hardware" or "devices").
    if filter_categories:
        query &= Q(categories__in=filter_categories)

    # Include specific tags (if provided)
    if include_tags:
        query &= Q(tags__in=include_tags)

    # Exclude specific tags (if provided)
    if exclude_tags:
        query &= ~Q(tags__in=exclude_tags)

    # Apply filters and ensure unique results
    content_qs = Content.objects.filter(query, publish=True).distinct().order_by('-published_at')

    # Apply limit if specified
    if limit:
        content_qs = content_qs[:limit]

    return content_qs


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

    structured_data = _generate_structured_data()  # No `content`, so it generates homepage JSON-LD

    context = {
        'home_main_content': home_main_content,
        'home_featured_contents': home_featured_contents,
        'recent_contents': recent_contents,
        'structured_data': structured_data,
    }
    return render(request, 'horizon/home.html', context)


def content_detail(request, type, slug):
    # Get the type object
    content_type = get_object_or_404(Type, name=type)
    content = get_object_or_404(Content, type=content_type, slug=slug)

    # Fetch related posts in the same category (excluding the current post)
    related_content = Content.objects.filter(
        categories__in=content.categories.all(),  # Match any of the same categories
        publish=True
    ).exclude(slug=slug)  # Exclude current post
    related_posts = related_content.order_by('-published_at')[:5]  # Get latest 3 related posts

    structured_data = _generate_structured_data(content)  # Pass `content`, so it generates NewsArticle/Review JSON-LD

    context = {
        'content': content,
        'author': content.author,
        'related_posts': related_posts,
        'structured_data': structured_data,
    }

    return render(request, 'horizon/detail.html', context)


def news_type_page(request):
    top_news_articles = _getContentByType("news", "Top News", 3)
    news_articles = _getContentByType("news", "", 100)

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
    products_category = Category.objects.filter(name="products").first()
    hardware_category = Category.objects.filter(name="hardware").first()
    devices_category = Category.objects.filter(name="devices").first()
    wearables_category = Category.objects.filter(name="wearables").first()
    assistants_category = Category.objects.filter(name="assistants").first()

    category_main_tag = Tag.objects.filter(name="Category Main").first()
    category_featured_tag = Tag.objects.filter(name="Category Featured").first()

    featured_contents = _get_filtered_content(
        include_categories=[products_category],
        include_tags=[category_main_tag],
        limit=3
    )

    hardware_content = _get_filtered_content(
        include_categories=[products_category, hardware_category],
        include_tags=[category_featured_tag],
        filter_categories=[hardware_category],
        limit=3
    )

    devices_content = _get_filtered_content(
        include_categories=[products_category, devices_category],
        include_tags=[category_featured_tag],
        filter_categories=[devices_category],
        limit=3
    )

    wearables_content = _get_filtered_content(
        include_categories=[products_category, wearables_category],
        include_tags=[category_featured_tag],
        filter_categories=[wearables_category],
        limit=3
    )

    assistants_content = _get_filtered_content(
        include_categories=[products_category, assistants_category],
        include_tags=[category_featured_tag],
        filter_categories=[assistants_category],
        limit=3
    )


    latest_contents = _get_filtered_content(include_categories=[products_category], limit=100)
    
    # Paginate news articles (5 per page)
    latest_contents_paginator = Paginator(latest_contents, 2)
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


def _generate_structured_data(content=None):
    """
    Dynamically generates JSON-LD structured data for both the homepage and content pages.
    
    - If `content` is None → Generates structured data for homepage.
    - If `content` exists → Generates structured data for NewsArticle or ReviewNewsArticle.
    """
    if content is None:
        # Generate structured data for the homepage
        structured_data = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "The Game Horizon",
            "url": "https://thegamehorizon.com",
            "description": "Your ultimate source for gaming news, reviews, guides, and more.",
            "publisher": {
                "@type": "Organization",
                "name": "The Game Horizon",
                "url": "https://thegamehorizon.com",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://thegamehorizon.com/static/publisher_256x256.png",
                    "width": 256,
                    "height": 256
                }
            }
        }

        # "potentialAction": {
        #     "@type": "SearchAction",
        #     "target": "https://thegamehorizon.com/?s={search_term_string}",
        #     "query-input": "required name=search_term_string"
        # }
    
    else:
        # Determine the content type: NewsArticle, ReviewNewsArticle, or General Article
        content_type = content.type.name.lower()

        # HORIZON content types
        # news
        # review
        # articles
        # comparison
        # deal
        # picks
        # story

        structured_data_type = "Article"
        if content_type == "news":
            structured_data_type = "NewsArticle"
        elif content_type == "review":
            structured_data_type = "ReviewNewsArticle"
        elif content_type == "articles":
            structured_data_type = "Article"
        elif content_type == "comparison":
            structured_data_type = "Article"
        elif content_type == "deal":
            structured_data_type = "Article"
        elif content_type == "picks":
            structured_data_type = "Article"
        else:
            structured_data_type = "Article"
        
        structured_data = {
            "@context": "https://schema.org",
            "@type": structured_data_type,
            "headline": escape(content.title),
            "description": escape(content.meta_description),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"https://thegamehorizon.com/{content.get_url_path()}"
            },
            "author": {
                "@type": "Person",
                "name": f"{content.author.first_name} {content.author.last_name}"
            },
            "publisher": {
                "@type": "Organization",
                "name": "The Game Horizon",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://thegamehorizon.com/static/publisher_256x256.png",
                    "width": 256,
                    "height": 256
                }
            },
            "datePublished": localtime(content.published_at).isoformat(),
            "dateModified": localtime(content.updated_at).isoformat(),
            "image": content.image_featured if content.image_featured else ""
        }

        # If the content is a review, add review schema
        # if content_type == "review":
        #     structured_data["review"] = {
        #         "@type": "Review",
        #         "reviewBody": escape(content.description),
        #         "author": {
        #             "@type": "Person",
        #             "name": f"{content.author.first_name} {content.author.last_name}"
        #         },
        #         "datePublished": localtime(content.published_at).isoformat(),
        #         "reviewRating": {
        #             "@type": "Rating",
        #             "ratingValue": str(content.rating if hasattr(content, "rating") else "4"),
        #             "bestRating": "5",
        #             "worstRating": "1"
        #         }
        #     }

    return json.dumps(structured_data, indent=2)
