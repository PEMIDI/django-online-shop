from django.urls import path

from catalogue import views

app_name = 'catalogue'

urlpatterns = [
    path('products/list/', views.product_list_view, name='product-list'),
    path('products/search/', views.product_search_view, name='product-search'),
    path('product/detail/<int:pk>/<slug:slug>/', views.product_detail_view, name='product-detail'),
    path('category/<int:pk>/<slug:slug>/products/', views.category_product_list_view, name='category-product-list'),
    path('brand/<int:pk>/<slug:slug>/products/', views.brand_product_list_view, name='brand-product-list'),

    path('user-profile/', views.user_profile_view, name='user-profile'),
    path('campaign/', views.campaign_view, name='campaign')
]
