from django.urls import path
from .views import home, content_detail, news_type_page, products_category_page
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),  # Homepage
    # path('products/', products_category_page, name='products_category_page_path_name'),
    # path('news/', news_type_page, name='news_type_page_path_name'),  # News page
    path('<str:type>/<slug:slug>/', content_detail, name='content_detail_path_name'),  # Detail page
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# 404 page setup
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

handler404 = 'horizon.urls.custom_404_view'
