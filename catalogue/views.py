from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from catalogue.models import Product, Category, Brand
from catalogue.utils import check_email


def product_list_view(request):
    # category = Category.objects.get(pk=2)  # hit-1
    # products = Product.objects.filter(is_available=True, category=category)  # hit-2
    #
    # products = Product.objects.filter(is_available=True, category_id=2)  # hit-1
    #
    # products = Product.objects.filter(is_available=True, category__name='Samsung')  # hit-1
    #
    # products = Product.objects.filter(is_available=True, category=category)  # and (&)
    # products = Product.objects.filter(is_available=True).filter(category=category)  # and (&)
    # products = Product.objects.filter(Q(is_available=True) & Q(category=category))  # and (&)
    #
    # products = Product.objects.filter(Q(is_available=True) | Q(category=category))  # or (|)

    products = Product.objects.select_related('category', 'brand').all()
    context = {
        'products': products,
    }
    return render(request, 'catalogue/product-list.html', context=context)


def product_detail_view(request, pk, slug):
    # Solution-1
    try:
        product = Product.objects.get(pk=pk, slug=slug)  # hit-1
    except Product.DoesNotExist:
        try:
            product = Product.objects.get(upc=pk, slug=slug)  # hit-2
        except Product.DoesNotExist:
            return HttpResponse('Product Does Not Exist')

    # Solution-2
    # qs = Product.objects.select_related('category', 'brand').filter((Q(pk=pk) | Q(upc=pk)), slug=slug)  # hit-1
    qs = Product.objects.select_related('category', 'brand').filter((Q(pk=pk) | Q(upc=pk)) & Q(slug=slug))  # hit-1
    if qs.exists():
        product = qs.first()
    else:
        return HttpResponse('Product Does Not Exist')

    context = {
        'product': product,
    }
    return render(request, 'catalogue/product-detail.html', context=context)


def category_product_list_view(request, pk, slug):
    # Solution-1
    qs = Category.objects.filter(pk=pk, slug=slug)  # hit-1
    if qs.exists():
        category = qs.first()
    else:
        return HttpResponse('Category Does Not Exist')

    products = Product.objects.filter(category=category)  # hit-2
    products = category.products.all()  # hit-2

    # Solution-2
    qs = Category.objects.prefetch_related('products').filter(pk=pk, slug=slug)  # hit-1
    if qs.exists():
        category = qs.first()
    else:
        return HttpResponse('Category Does Not Exist')
    products = Product.objects.filter(category=category)  # hit-2

    context = {
        'category': category,
        'products': products
    }
    return render(request, 'catalogue/category-product-list.html', context=context)


def brand_product_list_view(request, pk, slug):
    qs = Brand.objects.prefetch_related('products').filter(pk=pk, slug=slug)
    if qs.exists():
        brand = qs.first()
    else:
        return HttpResponse('Brand Does Not Exist')

    products = brand.products.all()
    context = '<br>'.join([f"{product.upc} - {product.title} - {product.brand}" for product in products])
    return HttpResponse(context)


def product_search_view(request):
    query = request.GET.get('q')
    products = Product.objects.select_related('category').filter(is_available=True, title__icontains=query)
    context = '<br>'.join([f"{product.upc} - {product.title} - {product.category.name}" for product in products])
    return HttpResponse(f'Search Page <br> <br> {context}')


@login_required(login_url='/admin/login/')  # Check Log-in user
@require_http_methods(request_method_list=['GET', 'POST'])  # Check allowed request method view
@user_passes_test(test_func=lambda u: u.email.endswith('@gmail.com'), login_url='/admin/login/')
@user_passes_test(test_func=check_email)  # Check passes test
@user_passes_test(test_func=lambda u: u.is_active)
@user_passes_test(test_func=lambda u: u.is_staff)
@permission_required('transaction.has_score_permission', raise_exception=True)  # Check user has permission
@permission_required('transaction.has_score_permission', login_url='/catalogue/product/detail/1/samsung-note-10/')
@user_passes_test(test_func=lambda u: u.has_perm('transaction.has_score_permission'), login_url='/admin/login/')
def user_profile_view(request):
    return HttpResponse(f'Hello {request.user}')


@login_required(login_url='/admin/login/')
@require_GET
@require_POST
@user_passes_test(test_func=lambda u: u.score > 200, login_url='/admin/login/')
@user_passes_test(test_func=lambda u: u.age > 15, login_url='/admin/login/')
@permission_required('transaction.has_score_permission', raise_exception=True)
def campaign_view(request):
    if request.user.is_authenticated:
        """Check log-in user"""
        pass

    if request.method == 'POST':
        """Check allowed request method to view"""
        pass

    if request.method == 'GET':
        """Check allowed request method to view"""
        pass

    if request.user.score > 200 and request.user.age > 15:
        """Check passes test"""
        pass

    if request.user.has_perm('transaction.has_score_permission'):
        pass

    return HttpResponse('Welcome to campaign')
