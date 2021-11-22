from django.urls import path, re_path

from blog import views

app_name = 'blog'

urlpatterns = [
    path('list/', views.post_list_view, name='post-list'),
    path('detail/<int:pk>/<slug:slug>/', views.post_detail_view, name='post-detail'),
    path('categories/list/', views.categories_list_view, name='categories-list'),
    path('archive/<int:year>/<int:month>/', views.post_list_view, name='archive-list-year-month'),
    # path('archive/<int:year>/', views.post_list_view, name='archive-list-year'),
    re_path(r'^archive/(?P<year>(?:(?:18|19|20|21)\d{2}))/$', views.post_list_view, name='archive-list-year'),

    # 4-digit(30%) | 6-digit(50%)
    re_path(r'^discount/(?P<code>\w{4})/$', views.discount_four_digit_view, name='discount-four-digit'),
    re_path(r'^discount/(?P<code>\w{6})/$', views.discount_six_digit_view, name='discount-six-digit'),
]
