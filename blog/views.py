from django.http import HttpResponse


def post_list_view(request, year=None, month=None):
    if month is not None:
        return HttpResponse(f'Archive List Page {year}/{month}')
    if year is not None:
        return HttpResponse(f'Archive List Page {year}')
    return HttpResponse(content='Posts List Page')


def categories_list_view(request):
    return HttpResponse('Categories List Page')


def post_detail_view(request, pk, slug):
    return HttpResponse(f'Post Detail id:{pk} - slug:{slug}')


def discount_four_digit_view(request, code):
    return HttpResponse(f'30% Discount - {code}')


def discount_six_digit_view(request, code):
    return HttpResponse(f'50% Discount - {code}')
